# 📄 Project Documentation

## AI E-Commerce Product & FAQ Assistant

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Project Structure](#2-project-structure)
3. [How the System Works](#3-how-the-system-works)
4. [Semantic Routing](#4-semantic-routing)
5. [FAQ Pipeline (RAG)](#5-faq-pipeline-rag)
6. [Product Pipeline (SQL)](#6-product-pipeline-sql)
7. [API Reference](#7-api-reference)
8. [Database Schema](#8-database-schema)
9. [Frontend](#9-frontend)
10. [Environment Variables](#10-environment-variables)

---

## 1. Project Overview

This project is a full-stack AI chatbot built for an e-commerce platform. It handles two distinct types of user queries:

- **FAQ queries** — questions about return policy, refunds, payments, shipping, and account management
- **Product queries** — browsing, filtering, and searching the product catalog by price, brand, rating, or discount

The system uses a **Semantic Router** to automatically classify incoming queries and forward them to the appropriate pipeline — either a **RAG-based FAQ engine** (ChromaDB + Groq LLM) or a **SQL-based product engine** (SQLite + Groq LLM).

---

## 2. Project Structure

```
E-Commerce-Product-FAQ-Assistant/
│
├── app/
│   ├── resources/
│   │   ├── __init__.py
│   │   ├── faq_data.csv          # FAQ knowledge base (questions + answers)
│   │   ├── faq.py                # ChromaDB vector store + RAG chain
│   │   ├── router.py             # Semantic Router definition and logic
│   │   └── sql.py                # SQLite product search + LLM integration
│   │
│   ├── static/
│   │   ├── script.js             # Frontend chat logic
│   │   └── style.css             # UI styling
│   │
│   └── templates/
│       └── index.html            # Main chat interface (served by FastAPI)
│
├── screenshots/                  # UI screenshots for README
├── chroma_db/                    # Persisted ChromaDB vector store (auto-generated)
├── db.sqlite                     # SQLite product database
├── main.py                       # FastAPI app entry point
├── requirements.txt              # Python dependencies
├── .env                          # Environment variables (not committed)
└── .gitignore
```

---

## 3. How the System Works

Every user message goes through the following flow:

```
User Message
     │
     ▼
POST /chat  (FastAPI)
     │
     ▼
Semantic Router  (router.py)
     │
     ├──── "faq"  ────▶  ChromaDB Vector Search  ──▶  Groq LLM  ──▶  Answer
     │
     ├──── "sql"  ────▶  SQLite Product Search   ──▶  Groq LLM  ──▶  Answer
     │
     └──── None   ────▶  Fallback message (out of scope)
```

**Step-by-step:**

1. The frontend sends the user's message to `POST /chat`
2. `main.py` calls `get_route(query)` from `router.py`
3. The Semantic Router classifies the query as `faq`, `sql`, or `None`
4. Based on the route, the query is handled by either `faq.py` or `sql.py`
5. The response is returned to the frontend as JSON

---

## 4. Semantic Routing

**File:** `app/resources/router.py`

The router uses the `semantic-router` library with a `HuggingFaceEncoder` (`all-MiniLM-L6-v2`) to classify queries based on semantic similarity — not keyword matching.

### Two Routes Defined

| Route | Name | Purpose |
|---|---|---|
| `faq_route` | `"faq"` | Handles policy, refund, payment, shipping, and account queries |
| `sql_route` | `"sql"` | Handles product search, filtering, brand, price, and catalog queries |

### How It Works

Each route is defined with a list of **utterances** — example sentences that represent that intent. The encoder converts both the utterances and the incoming query into vector embeddings and finds the closest match.

```python
result = router(query)
return result.name  # returns "faq", "sql", or None
```

If no route matches above the confidence threshold, `None` is returned and a fallback message is shown to the user.

### Encoder

```python
encoder = HuggingFaceEncoder()  # uses all-MiniLM-L6-v2 locally (no API cost)
```

The encoder runs locally — no external API calls are needed for routing.

---

## 5. FAQ Pipeline (RAG)

**File:** `app/resources/faq.py`

The FAQ pipeline uses **Retrieval-Augmented Generation (RAG)**:

### How RAG Works Here

```
User FAQ Query
      │
      ▼
ChromaDB Vector Search
(finds top-k similar FAQ entries from faq_data.csv)
      │
      ▼
Retrieved context injected into prompt
      │
      ▼
Groq Llama 3.3 generates final answer
      │
      ▼
Response returned to user
```

### Components

| Component | Tool Used |
|---|---|
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` (HuggingFace, free, local) |
| Vector Store | ChromaDB (persisted locally in `chroma_db/` folder) |
| LLM | Groq Llama 3.3 70B (`llama-3.3-70b-versatile`) |
| Knowledge Base | `faq_data.csv` (FAQ question-answer pairs) |

### Knowledge Base

`faq_data.csv` contains pre-written FAQ entries covering:
- Return & exchange policy
- Refund timelines
- Payment methods (UPI, cards, COD, EMI)
- Order tracking & cancellation
- Shipping & delivery
- Account & customer support

---

## 6. Product Pipeline (SQL)

**File:** `app/resources/sql.py`

The product pipeline uses a `ProductRAG` class that translates natural language queries into SQLite database queries with the help of Groq LLM.

### How It Works

```
User Product Query
      │
      ▼
Groq LLM generates SQL query
(based on user's natural language input)
      │
      ▼
SQL executed on db.sqlite
      │
      ▼
Results formatted and returned to user
```

### Supported Query Types

| Query Type | Example |
|---|---|
| Price filter | "Show products under ₹1000" |
| Rating filter | "Show products with rating above 4" |
| Brand filter | "Show Abros products" |
| Discount filter | "Show discounted products" |
| Category browse | "Show me laptops" |
| Stock check | "Which products are in stock?" |
| Sort/ranking | "Show top rated items" |

---

## 7. API Reference

**Base URL:** `http://127.0.0.1:8000`

---

### `GET /`

Returns the main chat interface (HTML page).

**Response:** `text/html` — renders `index.html`

---

### `POST /chat`

Main chat endpoint. Accepts a user message and returns an AI-generated response.

**Request Body:**
```json
{
  "message": "What is the return policy?"
}
```

**Response:**
```json
{
  "response": "You can return most items within 7 days of delivery..."
}
```

**Error Responses:**

| Status Code | Reason |
|---|---|
| `400` | Empty message sent |
| `500` | Internal server error |

---

### `GET /health`

Health check endpoint to verify the server is running.

**Response:**
```json
{
  "status": "ok"
}
```

---

## 8. Database Schema

### SQLite — `db.sqlite`

Stores the product catalog. The `products` table structure:

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER | Primary key |
| `name` | TEXT | Product name |
| `brand` | TEXT | Brand name |
| `category` | TEXT | Product category |
| `price` | REAL | Price in ₹ |
| `rating` | REAL | Average rating (0–5) |
| `discount` | REAL | Discount percentage |
| `in_stock` | INTEGER | 1 = in stock, 0 = out of stock |

### ChromaDB — `chroma_db/`

Stores vector embeddings of FAQ entries from `faq_data.csv`. Auto-generated on first run and persisted locally — no re-embedding needed on restart.

---

## 9. Frontend

**Files:** `app/static/script.js`, `app/static/style.css`, `app/templates/index.html`

The frontend is a single-page chat interface served directly by FastAPI using Jinja2 templates.

### Features
- Sends messages to `POST /chat` via `fetch()` API
- Displays user and bot messages in a chat bubble layout
- Shows quick reply suggestion buttons for common queries
- Handles loading states and error responses gracefully

### Communication Flow

```
User types message
       │
       ▼
script.js sends POST /chat with { message: "..." }
       │
       ▼
Receives { response: "..." }
       │
       ▼
Appends bot message to chat window
```

---

## 10. Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | Your API key from [console.groq.com](https://console.groq.com) |
| `GROQ_MODEL` | Groq model to use (default: `llama-3.3-70b-versatile`) |

> ⚠️ **Never commit your `.env` file.** Make sure `.env` is listed in `.gitignore`.

---

*Documentation written for the AI E-Commerce Product & FAQ Assistant by Sumedh Dikshit.*