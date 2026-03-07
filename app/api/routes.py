from fastapi import APIRouter, HTTPException
from app.api.models import ChatResponse,ChatRequest,HelathResponse
from app.core.config import APP_NAME,APP_VERSION


router = APIRouter()

@router.get("/health",response_model=HelathResponse)
def health_check():
    return HelathResponse(
        status="ok",
        version=APP_VERSION,
        app_name=APP_NAME
    )

@router.post("/chat",response_model=ChatResponse)
def chat(request: ChatRequest):

    if not request.question.strip():
        raise HTTPException(
            status_code = 400,
            detail= "Question cannot be empty"
        )
    dummy_answer = f"You asked: '{request.question}'. Ollama will answer this in Phase 3!"

    return ChatResponse(
        question=request.question,
        answer=dummy_answer,
        sources=[]
    )

@router.get("/documents")
def list_documents():
    return {
        "documents": [],
        "message" : "NO documents uploads yet. Coming in Phase 4!"

    }

@router.post("/ask")
def ask(request:ChatRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
        
    return {
        "question": request.question,
        "answer" : "FUll RAG answer coming in Phase 5!",
        "document_id" : request.document_id or None,
        "source": []
    }

