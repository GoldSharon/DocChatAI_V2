import os 
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
from app.services.document_services import(
    process_document,
    list_all_documents,
    load_document_metadata,
    get_upload_path
)

from app.core.config import ALLOWED_TYPES

upload_router = APIRouter()

@upload_router.post("/upload")
async def upload_document(file: UploadFile= File(...)):
    """
    Accept PDF and txt files and processes it
    """

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{ext}' not allowed. Use: {ALLOWED_TYPES}"
        )
    save_path = get_upload_path(file.filename)
    with open(save_path,"wb") as buffer:
        shutil.copyfileobj(file.file,buffer)

    print(f"[Upload] Saved file to {save_path}")

    try:
        result = process_document(save_path,file.filename)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail= f"Processing error: {str(e)}"
        )
    
    return {
        "message" : "Document uploaded and processes successfully!",
        "doc_id" : result["doc_id"],
        "filename" : result["filename"],
        "chunk_count" : result["chunk_count"],
        "text_length" : result["text_length"]

    }

@upload_router.get("/documents")
def list_document():
    """
        Return all uploaded document
    """

    docs = list_all_documents()
    return {
        "total" : len(docs),
        "documents": docs 
    }

@upload_router.get("/documents/{doc_id}")
def get_documnets(doc_id: str):

    """
        Return full metadata + chunks for a document.
    """

    try:
        meta = load_document_metadata(doc_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found")
    return meta 