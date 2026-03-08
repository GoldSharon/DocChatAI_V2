import os 
import uuid
import json
from pathlib import Path
from PyPDF2 import PdfReader
from app.core.config import UPLOAD_DIR, CHUNK_SIZE, CHUNK_OVERLAP, ALLOWED_TYPES


def genearate_document_id()-> str:
    """"
        Generate a Unique ID
    """

    return str(uuid.uuid4())[:8]

def get_upload_path(filename: str)-> str:
    """
    Return full path where file will be saved
    """

    return os.path.join(UPLOAD_DIR,filename)


def extract_text_from_pdf(filepath: str)-> str:

    """
        Extract all text from a PDF file
    """

    reader = PdfReader(filepath)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text
    return text.strip()

def extract_text_from_txt(filepath: str)-> str:

    """
    Extract all text from a TXT file.
    """

    with open(filepath, "r", encoding="utf-8") as f:
        return f.read().strip()

def extract_text(filepath: str)-> str:

    """
    Auto-detect file type and extract text
    """

    ext = Path(filepath).suffix.lower()

    if ext == ".pdf":
        return extract_text_from_pdf(filepath)
    
    elif ext== ".txt":
        return extract_text_from_txt(filepath)
    
    else:
        raise ValueError(f"Unsupported file type: {ext}. Allowed: {ALLOWED_TYPES}")
    
def chunk_text(text: str)-> list[str]:

    """
    Split text into overlapping chunks.
    
    Example with CHUNK_SIZE=20, CHUNK_OVERLAP=5:
    text = "Hello world this is a test of chunking logic here"
    
    chunk 1: "Hello world this is a"      (0 to 20)
    chunk 2: "is a test of chunking"      (15 to 35)  ← starts 5 back
    chunk 3: "chunking logic here"        (30 to 50)
    """

    chunks = []

    start = 0

    while start < len(text):

        end = start + CHUNK_SIZE
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks

def save_document_metadata(doc_id: str, filename: str, chunks: list[str]):
    """
    Save document info to a simple JSON file.
    """
    os.makedirs("data", exist_ok=True)
    metadata = {
        "doc_id": doc_id,
        "filename": filename,
        "chunk_count": len(chunks),
        "chunks": chunks
    }
    path = f"data/{doc_id}_metadata.json"

    # ← THIS WAS MISSING — actually write the file!
    with open(path, "w") as f:
        json.dump(metadata, f, indent=2)

    return path

def load_document_metadata(doc_id: str) -> dict:
    """
    Load a document's metadata by its ID.
    """
    path = f"data/{doc_id}_metadata.json"
    if not os.path.exists(path):
        raise FileNotFoundError(f"Document {doc_id} not found")  # ← fixed error type
    with open(path, "r") as f:
        return json.load(f)
    
def list_all_documents()-> list[dict]:

    os.makedirs("data", exist_ok=True)
    docs = []
    for file in os.listdir("data"):
        if file.endswith("_metadata.json"):
            with open(f"data/{file}") as f:
                meta = json.load(f)
                docs.append(
                    {
                        "doc_id": meta["doc_id"],
                        "filename": meta["filename"],
                        "chunk_count": meta["chunk_count"]
                    }
                )

    return docs 



def process_document(filepath: str, filename: str)-> dict:

    """
    Full pipeline:
    1. Extract text
    2. Chunk it
    3. Save metadata
    4. Return summary
    
    """

    doc_id = genearate_document_id()

    print(f"[DocService] Extracting text from {filename}...")

    text = extract_text(filepath)

    print(f"[DocService] Extracted {len(text)} chunks")

    chunks = chunk_text(text)

    print(f"[DocService] Created {len(chunks)} chunks")

    save_document_metadata(doc_id, filename, chunks)

    print(f"[DocService] SAved metadata for doc_id: {doc_id}")

    return {

        "doc_id": doc_id,
        "filename": filename,
        "chunk_count": len(chunks),
        "text_length": len(text)

    }