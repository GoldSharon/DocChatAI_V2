from dotenv import load_dotenv
import os

load_dotenv()

APP_NAME = "DocChat"
APP_VERSION = "0.1.0"
DEBUG = True

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL","granite3.1-dense:2b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL","http://localhost:11434")

UPLOAD_DIR      = "uploads"
CHUNK_SIZE      = 500    # characters per chunk
CHUNK_OVERLAP   = 50     # overlap between chunks (avoids cutting sentences)
ALLOWED_TYPES   = [".pdf", ".txt"]