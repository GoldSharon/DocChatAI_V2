from fastapi import FastAPI
from app.core.config import APP_NAME,APP_VERSION

app = FastAPI(
        title=APP_NAME,
        version=APP_VERSION
)

@app.get("/")
def root():
    return {
        'message' : f"Welcome to {APP_NAME}!"
    }

@app.get("/health")
def health():
    return {
        "status": "ok",
        "version": APP_VERSION
    }