# DocChat 🗂️
A RAG-powered document Q&A app built with FastAPI, FAISS, and Ollama.

## Stack
- FastAPI
- FAISS
- Ollama (granite3.1-dense:2b)
- sentence-transformers

## Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```