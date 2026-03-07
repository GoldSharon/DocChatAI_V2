from fastapi import APIRouter, HTTPException
from app.api.models import ChatResponse,ChatRequest,HelathResponse
from app.core.config import APP_NAME,APP_VERSION
from app.services.ollama_service import get_ollama_responce


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
    try:
        answer = get_ollama_responce(question=request.question)
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Ollama error: {str(e)}. Is Ollama running ? "
        )

    return ChatResponse(
        question=request.question,
        answer=answer,
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

