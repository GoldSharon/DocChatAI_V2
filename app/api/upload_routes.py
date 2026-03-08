import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
from app.services.document_services import (
    process_document,
    list_all_documents,
    load_document_metadata,
    get_upload_path
)
from app.services.faiss_services import (
    add_document_to_index,
    get_index_stats
)
from app.core.config import ALLOWED_TYPES

upload_router = APIRouter()


# ── Upload Document ────────────────────────────────────────────────────

@upload_router.post("/upload")
async def upload_document(file: UploadFile = File(...)):

    # Validate file type
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{ext}' not allowed. Use: {ALLOWED_TYPES}"
        )

    # Save file
    save_path = get_upload_path(file.filename)
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Process (extract + chunk + save metadata)
    try:
        result = process_document(save_path, file.filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

    # Load chunks and add to FAISS         ← NEW
    try:
        meta = load_document_metadata(result["doc_id"])
        add_document_to_index(result["doc_id"], meta["chunks"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"FAISS error: {str(e)}")

    return {
        "message": "Document uploaded, processed and indexed!",
        "doc_id": result["doc_id"],
        "filename": result["filename"],
        "chunk_count": result["chunk_count"],
        "text_length": result["text_length"]
    }


# ── List All Documents ─────────────────────────────────────────────────

@upload_router.get("/documents")
def list_documents():
    docs = list_all_documents()
    return {
        "total": len(docs),
        "documents": docs
    }


# ── Get Document Detail ────────────────────────────────────────────────

@upload_router.get("/documents/{doc_id}")
def get_document(doc_id: str):
    try:
        meta = load_document_metadata(doc_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found")
    return meta


# ── FAISS Index Stats          ← NEW ──────────────────────────────────

@upload_router.get("/index/stats")
def index_stats():
    return get_index_stats()