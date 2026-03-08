from fastapi import APIRouter, HTTPException
from app.api.models import ChatRequest, ChatResponse
from app.core.config import APP_NAME, APP_VERSION, GROQ_MODEL
from app.services.groq_service import get_groq_response, check_groq_connection
from app.services.faiss_services import search_similar_chunks
from app.services.rag_service import get_rag_response

router = APIRouter()


# ── Health Check ───────────────────────────────────────────────────────

@router.get("/health")
def health_check():
    groq_ok = check_groq_connection()
    return {
        "status": "ok",
        "version": APP_VERSION,
        "app_name": APP_NAME,
        "groq_connected": groq_ok,
        "model": GROQ_MODEL
    }


# ── Plain Chat (Groq, no RAG) ──────────────────────────────────────────

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        answer = get_groq_response(question=request.question)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Groq error: {str(e)}")

    return ChatResponse(
        question=request.question,
        answer=answer,
        sources=[]
    )


# ── RAG Ask (FAISS + Groq) — THE MAIN ENDPOINT ────────────────────────

@router.post("/ask")
def ask(request: ChatRequest):
    """
    Full RAG pipeline:
    Upload a doc first, then ask questions about it.
    Optionally pass document_id to query a specific doc.
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        result = get_rag_response(
            question=request.question,
            doc_id=request.document_id
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"RAG error: {str(e)}")

    return result


# ── Search Chunks (debug/test) ─────────────────────────────────────────

@router.get("/search")
def search_chunks(query: str, top_k: int = 3):
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    results = search_similar_chunks(query=query, top_k=top_k)

    if not results:
        return {
            "query": query,
            "results": [],
            "message": "No documents indexed yet."
        }

    return {"query": query, "top_k": top_k, "results": results}