from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import APP_NAME,APP_VERSION
from app.api.routes import router


app = FastAPI(
        title=APP_NAME,
        version=APP_VERSION,
        description="RAG-powered document Q&A app" 
)


app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_methods = ["*"],
    allow_headers=["*"],

)

app.include_router(router,prefix="/api/v1")

@app.get("/")
def root():
    return {
        'message' : f"Welcome to {APP_NAME}!",
        "docs" : "/docs",
        "heath" : "/api/v1/health"
    }

