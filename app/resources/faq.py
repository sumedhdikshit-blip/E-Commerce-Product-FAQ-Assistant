import pandas as pd
import chromadb
from chromadb.utils import embedding_functions
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

# ChromaDB Persistent Client
chroma_client = chromadb.PersistentClient(path="./chroma_db")

collection_name_faq = "faqs"

# Groq Client
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Embedding Model
ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)


def ingest_faq_data(path):
    """Ingest FAQ CSV into ChromaDB. Skips if already loaded."""

    collections = [c.name for c in chroma_client.list_collections()]

    if collection_name_faq in collections:
        print("FAQ collection already exists. Skipping ingestion.")
        return

    collection = chroma_client.get_or_create_collection(
        name=collection_name_faq,
        embedding_function=ef
    )

    df = pd.read_csv(path)

    # Validate required columns
    if "question" not in df.columns or "answer" not in df.columns:
        raise ValueError("CSV must have 'question' and 'answer' columns.")

    docs = df["question"].tolist()
    metadatas = [{"answer": answer} for answer in df["answer"].tolist()]
    ids = [str(i) for i in range(len(docs))]

    collection.add(
        documents=docs,
        metadatas=metadatas,
        ids=ids
    )

    print(f"{len(docs)} FAQs ingested successfully.")


# Auto-ingest on import if collection doesn't exist
_faq_path = os.path.join(os.path.dirname(__file__), "faq_data.csv")
ingest_faq_data(_faq_path)


def get_relevant_qa(query, n_results=2, distance_threshold=1.0):
    """
    Retrieve top matching FAQs for a query.
    Filters out results with distance above threshold (low relevance).
    Lower distance = more similar in ChromaDB (cosine distance).
    """

    collection = chroma_client.get_collection(
        name=collection_name_faq,
        embedding_function=ef
    )

    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )

    filtered = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        if dist <= distance_threshold:
            filtered.append({
                "question": doc,
                "answer": meta["answer"],
                "distance": round(dist, 4)
            })

    return filtered


def generate_answer(query, context):
    """Call Groq LLM to generate a grounded answer from retrieved context."""

    if not context.strip():
        return "I'm sorry, I don't have information on that. Please contact our support team."

    prompt = f"""You are a helpful and polite customer support assistant for a Flipkart-like e-commerce platform.
Answer the customer's question using ONLY the information provided in the context below.
If the context does not contain enough information, say: "I'm sorry, I don't have that information. Please contact support."
Do NOT make up any information.

CONTEXT:
{context}

CUSTOMER QUESTION:
{query}

ANSWER:"""

    response = groq_client.chat.completions.create(
        model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        messages=[
            {
                "role": "system",
                "content": "You are a helpful customer support assistant. Answer only from the given context."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=300,
        temperature=0.2
    )

    return response.choices[0].message.content.strip()


def faq_chain(query):
    """Full RAG pipeline: retrieve relevant FAQs → generate grounded answer."""

    relevant_faqs = get_relevant_qa(query)

    if not relevant_faqs:
        return "I'm sorry, I couldn't find a relevant answer. Please contact our support team."

    # Build context from retrieved Q&A pairs
    context_parts = []
    for item in relevant_faqs:
        context_parts.append(f"Q: {item['question']}\nA: {item['answer']}")

    context = "\n\n".join(context_parts)

    answer = generate_answer(query, context)

    return answer


if __name__ == "__main__":
    faq_path = os.path.join(os.path.dirname(__file__), "faq_data.csv")

    # Ingest only if not already done
    ingest_faq_data(faq_path)

    # Test queries
    test_queries = [
        "What is the return policy?",
        "How long does a refund take?",
        "Do you have any ongoing discounts?",
        "Can I pay using UPI?",
    ]

    for query in test_queries:
        print(f"\n{'='*50}")
        print(f"User: {query}")
        answer = faq_chain(query)
        print(f"Bot:  {answer}")