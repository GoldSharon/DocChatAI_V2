
---
title: Docchat Ai
emoji: 💻
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
license: mit
short_description: Chat with your documents using AI (PDF, DOCX, TXT) with FAIS
---

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference
=======
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

