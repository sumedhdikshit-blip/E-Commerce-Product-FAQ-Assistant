# 🛒 AI E-Commerce Product & FAQ Assistant

An AI-powered E-Commerce Chatbot that enables users to search products, explore pricing information, check ratings and discounts, and receive intelligent answers to frequently asked questions through a conversational interface.

The application combines Retrieval-Augmented Generation (RAG), Semantic Routing, Vector Search, and Large Language Models to deliver a smart shopping assistant experience.

---

## 🚀 Features

### 📖 FAQ Assistant

* Semantic FAQ search using ChromaDB
* Vector embeddings using Sentence Transformers
* AI-generated contextual answers using Groq Llama 3.3
* Fast retrieval of customer support information

### 🛍 Product Search Assistant

* Product search from SQLite database
* Product pricing queries
* Rating-based filtering
* Discount-based filtering
* Brand-specific product search
* Product catalog exploration

### 🧠 Intelligent Routing

* Semantic Router automatically classifies user queries
* FAQ queries routed to ChromaDB
* Product queries routed to SQLite
* Improves response quality and efficiency

### 💬 Modern Chat Interface

* Responsive HTML/CSS/JavaScript frontend
* Real-time chat experience
* Quick reply suggestions
* Loading indicators
* Mobile-friendly design

---

## 🏗 System Architecture

```text
User Query
     │
     ▼
Frontend (HTML/CSS/JavaScript)
     │
     ▼
FastAPI Backend
     │
     ▼
Semantic Router
     │
 ┌───┴───────────────┐
 │                   │
 ▼                   ▼

FAQ Route       Product Route
 │                   │
 ▼                   ▼

ChromaDB         SQLite
(Vector DB)    (Product DB)

 │                   │
 ▼                   ▼

Groq Llama 3.3  Groq Llama 3.3
     │
     ▼
Final Response
```

---

## 🛠 Technology Stack

### Backend

* FastAPI
* Python 3.12

### AI & NLP

* Groq Llama 3.3
* Semantic Router
* Sentence Transformers
* all-MiniLM-L6-v2 Embeddings

### Databases

* ChromaDB (Vector Database)
* SQLite (Product Database)

### Frontend

* HTML5
* CSS3
* JavaScript (ES6)

### Additional Libraries

* Pandas
* Jinja2
* Uvicorn
* Python Dotenv

---

## 📂 Project Structure

```text
AI-ECommerce-Chatbot
│
├── app
│   ├── resources
│   │   ├── faq.py
│   │   ├── router.py
│   │   └── sql.py
│   │
│   ├── static
│   │   ├── style.css
│   │   └── script.js
│   │
│   ├── templates
│   │   └── index.html
│
├── chroma_db
├── db.sqlite
├── requirements.txt
├── main.py
└── .gitignore
```

---

## 📸 Screenshots

### Home Page

![Home Page](screenshots/home-page.png)

---

### FAQ and Product Query

![FAQ Product Query](screenshots/faq-product-query.png)

---

### Rating Query

![Rating Query](screenshots/rating-query.png)

---

## 💡 Example Queries

### FAQ Queries

```text
What is the return policy?
How long does a refund take?
What payment methods are accepted?
Can I pay using UPI?
How can I track my order?
```

### Product Queries

```text
Show products under 1000
Show products with rating above 4
Show discounted products
Show products by brand Abros
Show top rated products
```

---

## ⚙️ Installation & Setup

### 1. Clone Repository

```bash
git clone https://github.com/sumedhdikshit-blip/E-Commerce-Product-FAQ-Assistant.git
cd E-Commerce-Product-FAQ-Assistant
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

### 3. Activate Virtual Environment

#### Windows

```bash
venv\Scripts\activate
```

#### Linux / macOS

```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file in the project root.

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile
```

### 6. Run Application

```bash
uvicorn main:app --reload
```

### 7. Open Browser

```text
http://127.0.0.1:8000
```

---

## 🔍 How It Works

### FAQ Flow

1. User asks a support question.
2. Semantic Router classifies it as FAQ.
3. Relevant FAQ entries are retrieved from ChromaDB.
4. Context is passed to Groq Llama 3.3.
5. Grounded answer is generated.

### Product Flow

1. User asks about products.
2. Semantic Router classifies it as Product Query.
3. SQLite database is searched.
4. Product information is formatted.
5. Response is returned to the user.

---

## 🎯 Key Learning Outcomes

* Retrieval-Augmented Generation (RAG)
* Vector Databases
* Semantic Routing
* FastAPI Development
* LLM Integration
* Embedding Models
* Frontend-Backend Integration
* AI-powered Search Systems

---

## 🚀 Future Enhancements

* Product recommendation engine
* User authentication
* Chat history persistence
* Voice-enabled chatbot
* Multi-language support
* Docker containerization
* Cloud deployment (AWS / Azure / GCP)
* Admin dashboard
* Product comparison feature
* Analytics dashboard

---

## 👨‍💻 Author

**Sumedh Dikshit**

GitHub: https://github.com/sumedhdikshit-blip

---

## ⭐ Support

If you found this project useful, consider giving it a ⭐ on GitHub.
