"""
sql.py – Product / Pricing RAG pipeline using SQLite + Groq LLaMA

Improvements over the original:
  - Class-based pipeline (ProductRAG) instead of loose module functions
  - Conversation memory so follow-up questions ("what about under 30k?")
    retain context from previous turns
  - Retry logic with exponential backoff for Groq API calls
  - Cleaner separation of concerns (DB layer, LLM layer, orchestration)
"""

from __future__ import annotations

import logging
import os
import re
import sqlite3
import time
from pathlib import Path
from typing import Optional

import pandas as pd
from dotenv import load_dotenv
from groq import Groq, APIError, APIConnectionError, RateLimitError

# ---------------------------------------------------------------------------
# Environment & Logging
# ---------------------------------------------------------------------------

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants / Configuration
# ---------------------------------------------------------------------------

DB_PATH: Path = Path(os.getenv("SQLITE_DB_PATH", "db.sqlite"))
TABLE_NAME: str = os.getenv("SQLITE_TABLE_NAME", "products")
GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama3-70b-8192")
DEFAULT_LIMIT: int = int(os.getenv("DEFAULT_LIMIT", "10"))
MAX_LIMIT: int = int(os.getenv("MAX_LIMIT", "50"))
MAX_RETRIES: int = int(os.getenv("GROQ_MAX_RETRIES", "3"))
RETRY_BASE_DELAY: float = float(os.getenv("GROQ_RETRY_BASE_DELAY", "1.0"))
MAX_HISTORY_TURNS: int = int(os.getenv("MAX_HISTORY_TURNS", "4"))

# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

SQL_GENERATION_PROMPT = (
    "You are an expert SQLite query writer. "
    "Given a table schema, recent conversation history, and a user question, "
    "write a single safe SELECT query that answers the question in context.\n"
    "Rules:\n"
    "  1. Only use SELECT – never INSERT, UPDATE, DELETE, DROP, ALTER, or PRAGMA.\n"
    "  2. Wrap the query in <sql>...</sql> tags and output nothing else.\n"
    "  3. Use LIKE with '%value%' for text searches so partial matches work.\n"
    "  4. Never add a LIMIT clause – the caller will add one.\n"
    "  5. Use only columns that exist in the provided schema.\n"
    "  6. If the user question refers back to a prior topic (e.g. 'what about "
    "cheaper ones', 'show more from that brand'), use the conversation history "
    "to resolve what they mean before writing SQL."
)

SYSTEM_PROMPT = (
    "You are a helpful e-commerce assistant similar to Flipkart's product advisor. "
    "Answer the user's question conversationally using only the database results "
    "provided and the recent conversation history for context. "
    "Be concise (2-4 sentences). If results are empty or irrelevant, say so politely."
)

# ---------------------------------------------------------------------------
# Custom Exceptions
# ---------------------------------------------------------------------------

class ProductRAGError(Exception):
    """Base exception for pipeline errors."""


class DatabaseError(ProductRAGError):
    """Raised for SQLite connection / query issues."""


class LLMError(ProductRAGError):
    """Raised when the Groq LLM call fails or returns an unusable response."""


class UnsafeSQLError(ProductRAGError):
    """Raised when generated SQL fails the safety check."""


# ---------------------------------------------------------------------------
# Database Layer
# ---------------------------------------------------------------------------

class ProductDatabase:
    """Thin wrapper around the SQLite product database."""

    def __init__(self, db_path: Path = DB_PATH, table_name: str = TABLE_NAME):
        self.db_path = db_path.expanduser().resolve()
        self.table_name = table_name
        self._schema_cache: Optional[str] = None

    def _connect(self) -> sqlite3.Connection:
        if not self.db_path.exists():
            raise DatabaseError(
                f"SQLite database not found at '{self.db_path}'. "
                "Set SQLITE_DB_PATH in your .env file or place db.sqlite beside sql.py."
            )
        try:
            return sqlite3.connect(str(self.db_path))
        except sqlite3.Error as exc:
            raise DatabaseError(f"Failed to connect to database: {exc}") from exc

    def get_schema(self) -> pd.DataFrame:
        try:
            with self._connect() as conn:
                schema = pd.read_sql_query(f"PRAGMA table_info({self.table_name})", conn)
        except sqlite3.Error as exc:
            raise DatabaseError(f"Failed to read schema: {exc}") from exc

        if schema.empty:
            raise DatabaseError(
                f"Table '{self.table_name}' was not found in the SQLite database. "
                "Set SQLITE_TABLE_NAME in your .env file."
            )
        return schema

    def schema_text(self, refresh: bool = False) -> str:
        """Return a compact 'name  type' string for the LLM prompt (cached)."""
        if self._schema_cache is None or refresh:
            schema = self.get_schema()
            self._schema_cache = schema[["name", "type"]].to_string(index=False)
        return self._schema_cache

    @staticmethod
    def is_safe_select(sql_query: str) -> bool:
        """Return True only if the query is a plain SELECT with no mutating keywords."""
        normalized = re.sub(r"\s+", " ", sql_query.strip()).lower()
        forbidden = re.compile(
            r"\b(insert|update|delete|drop|alter|pragma|attach|detach|create|"
            r"replace|vacuum|truncate)\b",
            re.IGNORECASE,
        )
        return normalized.startswith("select ") and not forbidden.search(normalized)

    @staticmethod
    def apply_limit(sql_query: str) -> str:
        """
        Enforce a safe LIMIT on the query.
        - If LIMIT already present: clamp it to [1, MAX_LIMIT].
        - If absent: append DEFAULT_LIMIT.
        """
        query = sql_query.rstrip(";").strip()
        limit_match = re.search(r"\blimit\s+(\d+)\b", query, re.IGNORECASE)

        if limit_match:
            requested = int(limit_match.group(1))
            safe = min(max(requested, 1), MAX_LIMIT)
            return re.sub(r"\blimit\s+\d+\b", f"LIMIT {safe}", query, flags=re.IGNORECASE)

        return f"{query} LIMIT {DEFAULT_LIMIT}"

    def run_query(self, sql_query: str) -> pd.DataFrame:
        """Validate and execute a read-only SELECT query; return results as a DataFrame."""
        if not sql_query or not self.is_safe_select(sql_query):
            raise UnsafeSQLError("Only safe SELECT queries are allowed.")

        safe_query = self.apply_limit(sql_query)
        logger.info("Executing SQL: %s", safe_query)

        try:
            with self._connect() as conn:
                return pd.read_sql_query(safe_query, conn)
        except sqlite3.Error as exc:
            raise DatabaseError(f"Query execution failed: {exc}") from exc


# ---------------------------------------------------------------------------
# LLM Layer
# ---------------------------------------------------------------------------

class GroqLLM:
    """Wrapper around the Groq client with retry/backoff for transient failures."""

    def __init__(
        self,
        model: str = GROQ_MODEL,
        max_retries: int = MAX_RETRIES,
        base_delay: float = RETRY_BASE_DELAY,
    ):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "GROQ_API_KEY is not set. Add it to your .env file or environment."
            )
        self.client = Groq(api_key=api_key)
        self.model = model
        self.max_retries = max_retries
        self.base_delay = base_delay

    def _complete(self, messages: list[dict], temperature: float, max_tokens: int) -> str:
        """Call the Groq chat completion API with retries on transient errors."""
        last_exc: Optional[Exception] = None

        for attempt in range(1, self.max_retries + 1):
            try:
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                content = completion.choices[0].message.content
                if not content or not content.strip():
                    raise LLMError("Groq returned an empty response.")
                return content.strip()

            except (RateLimitError, APIConnectionError) as exc:
                # Transient — worth retrying with backoff
                last_exc = exc
                if attempt < self.max_retries:
                    delay = self.base_delay * (2 ** (attempt - 1))
                    logger.warning(
                        "Groq call failed (%s), retry %d/%d in %.1fs",
                        type(exc).__name__, attempt, self.max_retries, delay,
                    )
                    time.sleep(delay)
                else:
                    logger.exception("Groq call failed after %d attempts.", attempt)

            except APIError as exc:
                # Non-transient (e.g. bad request, auth) — don't retry
                logger.exception("Groq API error (non-retryable).")
                raise LLMError(f"Groq API error: {exc}") from exc

            except Exception as exc:
                last_exc = exc
                if attempt < self.max_retries:
                    delay = self.base_delay * (2 ** (attempt - 1))
                    logger.warning(
                        "Unexpected Groq error (%s), retry %d/%d in %.1fs",
                        type(exc).__name__, attempt, self.max_retries, delay,
                    )
                    time.sleep(delay)
                else:
                    logger.exception("Groq call failed after %d attempts.", attempt)

        raise LLMError(f"Groq call failed after {self.max_retries} attempts: {last_exc}")

    def generate_sql(self, question: str, schema_text: str, history_text: str) -> str:
        """Use Groq LLaMA to produce a safe SQLite SELECT query for a product question."""
        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")

        prompt = (
            f"Table: {TABLE_NAME}\n\n"
            f"Schema:\n{schema_text}\n\n"
            f"Conversation history:\n{history_text or '(none)'}\n\n"
            f"User question:\n{question.strip()}"
        )

        raw = self._complete(
            messages=[
                {"role": "system", "content": SQL_GENERATION_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            max_tokens=220,
        )

        matches = re.findall(r"<sql>(.*?)</sql>", raw, re.IGNORECASE | re.DOTALL)
        if not matches:
            logger.error("No <sql> tags found in LLM response: %s", raw)
            raise LLMError(
                "The model did not return a valid SQL query. Try rephrasing your question."
            )

        return matches[0].strip()

    def generate_answer(
        self,
        question: str,
        results: pd.DataFrame,
        sql_query: Optional[str],
        history_text: str,
    ) -> str:
        """Produce a natural-language answer from the database results via Groq."""
        if results.empty:
            return (
                "I couldn't find any matching products. "
                "Try using a broader product name, category, brand, or price range."
            )

        context = results.head(MAX_LIMIT).to_string(index=False)

        prompt = (
            f"Conversation history:\n{history_text or '(none)'}\n\n"
            f"User question:\n{question.strip()}\n\n"
            f"SQL query used:\n{sql_query or 'N/A'}\n\n"
            f"Database results:\n{context}\n\n"
            "Answer the user from these results only, using the conversation "
            "history for context if relevant."
        )

        return self._complete(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=350,
        )


# ---------------------------------------------------------------------------
# Conversation Memory
# ---------------------------------------------------------------------------

class ConversationMemory:
    """Keeps a short rolling history of (question, answer) turns for context."""

    def __init__(self, max_turns: int = MAX_HISTORY_TURNS):
        self.max_turns = max_turns
        self._turns: list[tuple[str, str]] = []

    def add(self, question: str, answer: str) -> None:
        self._turns.append((question, answer))
        if len(self._turns) > self.max_turns:
            self._turns.pop(0)

    def as_text(self) -> str:
        if not self._turns:
            return ""
        lines = []
        for q, a in self._turns:
            lines.append(f"User: {q}")
            lines.append(f"Assistant: {a}")
        return "\n".join(lines)

    def clear(self) -> None:
        self._turns.clear()


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

class ProductRAG:
    """
    Full pipeline:
        user question (+ history) -> LLM generates SQL -> SQLite query -> LLM answer

    Usage:
        rag = ProductRAG()
        answer = rag.ask("Show me laptops under 40000")
        followup = rag.ask("What about gaming ones?")  # uses memory from above
    """

    def __init__(
        self,
        db: Optional[ProductDatabase] = None,
        llm: Optional[GroqLLM] = None,
        memory: Optional[ConversationMemory] = None,
    ):
        self.db = db or ProductDatabase()
        self.llm = llm or GroqLLM()
        self.memory = memory if memory is not None else ConversationMemory()

    def generate_sql(self, question: str) -> str:
        """Return a validated, limit-applied SQL query for the given question."""
        schema_text = self.db.schema_text()
        history_text = self.memory.as_text()

        sql_query = self.llm.generate_sql(question, schema_text, history_text)
        sql_query = self.db.apply_limit(sql_query)

        if not self.db.is_safe_select(sql_query):
            logger.error("Unsafe SQL blocked: %s", sql_query)
            raise UnsafeSQLError("Generated SQL was blocked because it is not a safe SELECT query.")

        return sql_query

    def ask(self, question: str, remember: bool = True) -> str:
        """
        Run the full pipeline for a question and return a natural-language answer.
        Catches all pipeline errors and returns a user-friendly message instead
        of raising, so it's safe to call directly from a chat loop.
        """
        try:
            sql_query = self.generate_sql(question)
            results = self.db.run_query(sql_query)
            answer = self.llm.generate_answer(
                question, results, sql_query, self.memory.as_text()
            )
        except UnsafeSQLError as exc:
            logger.warning("Unsafe SQL for question %r: %s", question, exc)
            answer = "Sorry, I can't run that kind of query. Try rephrasing your question."
        except DatabaseError as exc:
            logger.exception("Database error for question: %r", question)
            answer = f"Sorry, I had trouble accessing the product database. ({exc})"
        except LLMError as exc:
            logger.exception("LLM error for question: %r", question)
            answer = f"Sorry, I couldn't process that question right now. ({exc})"
        except Exception as exc:
            logger.exception("Unexpected error for question: %r", question)
            answer = f"Sorry, something went wrong while processing your question. ({exc})"

        if remember:
            self.memory.add(question, answer)

        return answer

    def reset_conversation(self) -> None:
        """Clear conversation memory (e.g. when starting a new chat session)."""
        self.memory.clear()


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Product Assistant — type 'exit' to quit, 'reset' to clear conversation memory.\n")

    try:
        rag = ProductRAG()
    except (EnvironmentError, ProductRAGError) as exc:
        print(f"Startup error: {exc}")
        raise SystemExit(1)

    while True:
        try:
            user_question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_question:
            continue
        if user_question.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        if user_question.lower() == "reset":
            rag.reset_conversation()
            print("(conversation memory cleared)\n")
            continue

        response = rag.ask(user_question)
        print(f"Assistant: {response}\n")