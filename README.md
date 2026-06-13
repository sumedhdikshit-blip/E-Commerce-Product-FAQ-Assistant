# 🛒 AI E-Commerce Product & FAQ Assistant

> An AI-powered E-Commerce Chatbot combining **Semantic Routing**, **Vector Search**, **RAG (Retrieval-Augmented Generation)**, and **Large Language Models** to deliver intelligent FAQ assistance and product discovery.

<br>

## 📸 Screenshots

<table>
  <tr>
    <td align="center">
      <img src="screenshots/home-page.png" alt="Home Page" width="300"/><br/>
      <b>Home Page</b>
    </td>
    <td align="center">
      <img src="screenshots/faq-product-query.png" alt="FAQ & Product Search" width="300"/><br/>
      <b>FAQ & Product Search</b>
    </td>
    <td align="center">
      <img src="screenshots/rating-query.png" alt="Product Rating Query" width="300"/><br/>
      <b>Rating-Based Query</b>
    </td>
  </tr>
</table>

<br>

---

## 🚀 Features

### 📖 FAQ Assistant
- Semantic FAQ Retrieval using ChromaDB Vector Search
- Context-aware AI responses powered by Groq Llama 3.3

### 🛍️ Product Search
- SQLite product database with rich filtering
- Search by **rating**, **discount**, **brand**, and **price**

### 🧠 AI Routing
- Semantic Router for automatic intent classification
- Dynamic query routing between FAQ and Product pipelines

### 💬 Chat Interface
- Modern, responsive UI with real-time responses
- Quick reply suggestions for common queries

---

## 🏗️ Architecture

```
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
 │                             │
 ▼                             ▼
FAQ Route               Product Route
 │                             │
 ▼                             ▼
ChromaDB                    SQLite
 │                             │
 ▼                             ▼
Groq LLM                  Groq LLM
 │
 ▼
Response
```

---

## 🛠️ Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Backend** | Python, FastAPI |
| **AI / NLP** | Groq Llama 3.3, Semantic Router, Sentence Transformers (`all-MiniLM-L6-v2`) |
| **Databases** | SQLite, ChromaDB |
| **Frontend** | HTML, CSS, JavaScript |

---

## 💡 Example Queries

**FAQ Queries**
```
What is the return policy?
How long does a refund take?
What payment methods are accepted?
Can I pay using UPI?
```

**Product Queries**
```
Show products under 1000
Show products with rating above 4
Show discounted products
Show Abros products
```

---

## ⚙️ Installation

### 1. Clone Repository
```bash
git clone https://github.com/sumedhdikshit-blip/E-Commerce-Product-FAQ-Assistant.git
cd E-Commerce-Product-FAQ-Assistant
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the project root:
```env
GROQ_API_KEY=YOUR_API_KEY
GROQ_MODEL=llama-3.3-70b-versatile
```

### 4. Run
```bash
uvicorn main:app --reload
```

### 5. Open in Browser
```
http://127.0.0.1:8000
```

---

## 📚 Learning Outcomes

- Retrieval-Augmented Generation (RAG)
- Vector Databases & Semantic Search
- FastAPI Backend Development
- LLM Integration with Groq
- Semantic Routing & Intent Classification
- Full-stack Frontend–Backend Integration

---

## 🚀 Future Enhancements

- [ ] Product Recommendation Engine
- [ ] User Authentication & Chat History
- [ ] Voice Assistant Support
- [ ] Docker Support & Cloud Deployment
- [ ] Multi-Language Support

---

## 👨‍💻 Author

**Sumedh Dikshit**  
GitHub: [@sumedhdikshit-blip](https://github.com/sumedhdikshit-blip)

---

⭐ *If you found this project useful, consider starring the repository!*
