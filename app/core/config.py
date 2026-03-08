from dotenv import load_dotenv
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

APP_NAME    = "DocChat"
APP_VERSION = "0.1.0"
DEBUG       = True



# Ollama (keeping for local fallback)
OLLAMA_MODEL    = os.getenv("OLLAMA_MODEL", "llama3.2")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Groq                              ← NEW
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL   = os.getenv("GROQ_MODEL", "llama3-8b-8192")

# Document settings
UPLOAD_DIR    = "uploads"
CHUNK_SIZE    = 500
CHUNK_OVERLAP = 50
ALLOWED_TYPES = [".pdf", ".txt"]

# FAISS + Embeddings
FAISS_INDEX_DIR = "data/faiss"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# RAG settings                      ← NEW
TOP_K_CHUNKS        = 3     # how many chunks to retrieve
MIN_RELEVANCE_SCORE = 1.5   # max distance allowed (lower = stricter)