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

A RAG-powered document Q&A application. Upload any PDF or TXT document and ask questions about it — powered by FAISS vector search and Groq LLM.

## 🔗 Live Demo
👉 **https://huggingface.co/spaces/GoldSharon/docchat-ai/**

> ⚠️ Hosted on Render free tier — first load may take 30–60 seconds to wake up.

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python) |
| LLM | Groq API (gpt-oss-20b) |
| Vector DB | FAISS (in-memory) |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Frontend | HTML + CSS + Vanilla JS |
| Deployment | Render (free tier) |

---

## ✨ Features

- 📄 Upload PDF or TXT documents
- 🔍 Semantic search using FAISS vector embeddings
- 🤖 Context-aware answers using RAG pipeline
- 💬 General chat mode when no document is selected
- 📐 Markdown rendering in responses
- 🗑 Auto session clear on server restart

---

## 🚀 Run Locally

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/docchat.git
cd docchat
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

### 5. Run the app
```bash
uvicorn app.main:app --reload
```

### 6. Open in browser
```
http://localhost:8000
```

---

## 📁 Project Structure
```
docchat/
├── app/
│   ├── api/
│   │   ├── routes.py          # /chat, /ask, /search endpoints
│   │   └── upload_routes.py   # /upload, /documents endpoints
│   ├── core/
│   │   └── config.py          # environment config
│   ├── services/
│   │   ├── groq_service.py    # Groq LLM integration
│   │   ├── faiss_service.py   # vector index + similarity search
│   │   ├── document_service.py# PDF/TXT parsing + chunking
│   │   └── rag_service.py     # full RAG pipeline
│   ├── static/
│   │   ├── index.html         # frontend UI
│   │   ├── style.css          # styling
│   │   └── app.js             # frontend logic
│   └── main.py                # FastAPI app entry point
├── .env.example
├── render.yaml
├── requirements.txt
└── README.md
```

---

## 🔑 Environment Variables

| Variable | Description | Default |
|---|---|---|
| `GROQ_API_KEY` | Your Groq API key | required |
| `GROQ_MODEL` | Groq model to use | `openai/gpt-oss-20b` |
| `MIN_RELEVANCE_SCORE` | FAISS distance threshold | `3.0` |
| `CHUNK_SIZE` | Characters per chunk | `500` |
| `CHUNK_OVERLAP` | Overlap between chunks | `50` |

Get a free Groq API key at 👉 https://console.groq.com

---

## 🧠 How RAG Works
```
User uploads document
        ↓
Text extracted → split into chunks
        ↓
Chunks → embeddings (sentence-transformers)
        ↓
Embeddings stored in FAISS index
        ↓
User asks question
        ↓
Question → embedding → FAISS similarity search
        ↓
Top matching chunks retrieved as context
        ↓
Context + question → Groq LLM → answer
```

---

## 📸 Screenshot

> Upload a document → select it → ask questions → get answers with sources

---

## 🤝 Contributing

1. Fork the repo
2. Create a branch (`git checkout -b feature/my-feature`)
3. Commit changes (`git commit -m "add my feature"`)
4. Push branch (`git push origin feature/my-feature`)
5. Open a Pull Request

---

## 📜 License

MIT License — free to use and modify.

---

