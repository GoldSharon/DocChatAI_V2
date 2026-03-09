---

title: Docchat AI
emoji: 💻
colorFrom: blue
colorTo: indigo
sdk: docker
app_file: app/main.py
pinned: false
license: mit
short_description: AI chat with documents using RAG
---
---------------------------------------------------

# DocChat AI 📄

A **Retrieval-Augmented Generation (RAG)** powered document Q&A application.
Upload **PDF or TXT documents** and ask questions about them using **semantic search + LLM reasoning**.

The system retrieves relevant document chunks using **FAISS vector search** and generates answers using the **Groq LLM API**.

---

# 🔗 Live Demo

👉 https://huggingface.co/spaces/GoldSharon/docchat-ai

> ⚠️ Hosted on Hugging Face Spaces (free CPU tier).
> The app may take **20–60 seconds to start** if the Space is sleeping.

---

# 🛠 Tech Stack

| Layer           | Technology                   |
| --------------- | ---------------------------- |
| Backend         | FastAPI (Python)             |
| LLM             | Groq API                     |
| Vector Database | FAISS                        |
| Embeddings      | sentence-transformers        |
| Frontend        | HTML + CSS + Vanilla JS      |
| Deployment      | Hugging Face Spaces (Docker) |

---

# ✨ Features

• Upload **PDF or TXT documents**
• **Semantic search** using FAISS vector embeddings
• **Context-aware answers** via RAG pipeline
• **General chat mode** when no document is selected
• **Markdown formatted responses**
• **Automatic session reset** on restart

---

# 🚀 Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/docchat.git
cd docchat
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

Windows:

```bash
venv\Scripts\activate
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Set environment variables

Create `.env`

```env
GROQ_API_KEY=your_api_key_here
GROQ_MODEL=openai/gpt-oss-20b
```

You can get a free key from
👉 https://console.groq.com

---

### 5. Run the application

```bash
uvicorn app.main:app --reload
```

---

### 6. Open the browser

```
http://localhost:8000
```

---

# 📁 Project Structure

```
docchat/
├── app/
│   ├── api/
│   │   ├── routes.py
│   │   └── upload_routes.py
│   ├── core/
│   │   └── config.py
│   ├── services/
│   │   ├── groq_service.py
│   │   ├── faiss_service.py
│   │   ├── document_service.py
│   │   └── rag_service.py
│   ├── static/
│   │   ├── index.html
│   │   ├── style.css
│   │   └── app.js
│   └── main.py
├── Dockerfile
├── requirements.txt
└── README.md
```

---

# 🔑 Environment Variables

| Variable            | Description                |
| ------------------- | -------------------------- |
| GROQ_API_KEY        | API key for Groq LLM       |
| GROQ_MODEL          | Model used for generation  |
| MIN_RELEVANCE_SCORE | FAISS similarity threshold |
| CHUNK_SIZE          | Document chunk size        |
| CHUNK_OVERLAP       | Overlap between chunks     |

---

# 🧠 How the RAG Pipeline Works

```
User uploads document
        ↓
Text extracted and split into chunks
        ↓
Chunks converted to embeddings
        ↓
Stored in FAISS vector index
        ↓
User asks a question
        ↓
Question converted to embedding
        ↓
FAISS retrieves relevant chunks
        ↓
Context + question sent to LLM
        ↓
LLM generates final answer
```

---

# ☁️ Deployment

This project is deployed on **Hugging Face Spaces using Docker**.

Steps used:

1. Create a Space
2. Select **Docker SDK**
3. Add `Dockerfile`
4. Push project via Git
5. Add secrets in Space settings:

```
GROQ_API_KEY
GROQ_MODEL
```

The Space automatically builds and deploys the application.

---

# 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to your fork
5. Open a Pull Request

---

# 📜 License

MIT License — free to use and modify.
