# 🛒 AI E-Commerce Product & FAQ Assistant

[![Python](https://img.shields.io/badge/Python-3.12-blue)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)]()
[![Groq](https://img.shields.io/badge/Groq-LLM-orange)]()
[![ChromaDB](https://img.shields.io/badge/ChromaDB-VectorDB-purple)]()
[![SQLite](https://img.shields.io/badge/SQLite-Database-lightgrey)]()

An AI-powered E-Commerce Chatbot that combines **Semantic Routing**, **Vector Search**, **RAG (Retrieval-Augmented Generation)**, and **Large Language Models** to provide intelligent FAQ assistance and product search capabilities.

---

## 🚀 Features

### 📖 FAQ Assistant
- Semantic FAQ Retrieval
- ChromaDB Vector Search
- Context-Aware AI Responses
- Groq Llama 3.3 Integration

### 🛍 Product Search
- SQLite Product Database
- Product Filtering
- Rating-Based Search
- Discount Search
- Brand Search
- Price-Based Search

### 🧠 AI Routing
- Semantic Router
- Intent Classification
- Dynamic Query Routing

### 💬 Chat Interface
- Modern UI
- Responsive Design
- Real-Time Responses
- Quick Reply Suggestions

---

## 🏗 Architecture

```text
User Query
    │
    ▼
Frontend (HTML/CSS/JS)
    │
    ▼
FastAPI Backend
    │
    ▼
Semantic Router
 ┌──────────────┬──────────────┐
 │              │
 ▼              ▼

FAQ Route   Product Route

 │              │
 ▼              ▼

ChromaDB     SQLite

 │              │
 ▼              ▼

Groq LLM    Groq LLM

 │
 ▼

Response
```

---

## 🛠 Tech Stack

### Backend
- Python
- FastAPI

### AI & NLP
- Groq Llama 3.3
- Semantic Router
- Sentence Transformers
- all-MiniLM-L6-v2

### Database
- SQLite
- ChromaDB

### Frontend
- HTML
- CSS
- JavaScript

---

## 📸 Screenshots

### Home Page

![Home Page](screenshots/home-page.png)

---

### FAQ & Product Search

![FAQ Product Query](screenshots/faq-product-query.png)

---

### Product Rating Query

![Rating Query](screenshots/rating-query.png)

---

## 💡 Example Queries

### FAQ Queries

```text
What is the return policy?
How long does a refund take?
What payment methods are accepted?
Can I pay using UPI?
```

### Product Queries

```text
Show products under 1000
Show products with rating above 4
Show discounted products
Show Abros products
```

---

## ⚙ Installation

### Clone Repository

```bash
git clone https://github.com/sumedhdikshit-blip/E-Commerce-Product-FAQ-Assistant.git
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

Create `.env`

```env
GROQ_API_KEY=YOUR_API_KEY
GROQ_MODEL=llama-3.3-70b-versatile
```

### Run

```bash
uvicorn main:app --reload
```

### Open

```text
http://127.0.0.1:8000
```

---

## 📚 Learning Outcomes

- Retrieval Augmented Generation (RAG)
- Vector Databases
- Semantic Search
- FastAPI Development
- LLM Integration
- Frontend-Backend Integration

---

## 🚀 Future Enhancements

- Product Recommendation Engine
- User Authentication
- Chat History
- Voice Assistant
- Docker Support
- Cloud Deployment
- Multi-Language Support

---

## 👨‍💻 Author

**Sumedh Dikshit**

GitHub: https://github.com/sumedhdikshit-blip

---

⭐ If you found this project useful, consider starring the repository.
