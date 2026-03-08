import os
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from app.core.config import FAISS_INDEX_DIR, EMBEDDING_MODEL

print("[FAISS] Loading embedding model...")
embedder = SentenceTransformer(EMBEDDING_MODEL)
print("[FAISS] Embedding model loaded!")

chunk_store: list[dict] = []
faiss_index = None

INDEX_PATH      = "data/faiss.index"
CHUNK_STORE_PATH = "data/chunk_store.json"


def get_embedding(text: str) -> np.ndarray:
    return embedder.encode([text], convert_to_numpy=True).astype("float32")


def get_embeddings(texts: list[str]) -> np.ndarray:
    return embedder.encode(texts, convert_to_numpy=True).astype("float32")


def save_index():
    """Save FAISS index and chunk store to disk."""
    if faiss_index is None:
        return
    os.makedirs("data", exist_ok=True)
    faiss.write_index(faiss_index, INDEX_PATH)
    with open(CHUNK_STORE_PATH, "w") as f:
        json.dump(chunk_store, f)
    print("[FAISS] Index saved to disk")


def load_index():
    """Load FAISS index and chunk store from disk on startup."""
    global faiss_index, chunk_store
    if os.path.exists(INDEX_PATH) and os.path.exists(CHUNK_STORE_PATH):
        faiss_index = faiss.read_index(INDEX_PATH)
        with open(CHUNK_STORE_PATH, "r") as f:
            chunk_store = json.load(f)
        print(f"[FAISS] Loaded index from disk: {faiss_index.ntotal} chunks")
    else:
        print("[FAISS] No saved index found, starting fresh")


def init_index(dimension: int):
    global faiss_index
    faiss_index = faiss.IndexFlatL2(dimension)
    print(f"[FAISS] New index created with dimension {dimension}")


def add_document_to_index(doc_id: str, chunks: list[str]):
    global faiss_index, chunk_store

    if not chunks:
        raise ValueError("No chunks to add")

    print(f"[FAISS] Embedding {len(chunks)} chunks for doc {doc_id}...")
    embeddings = get_embeddings(chunks)

    if faiss_index is None:
        init_index(dimension=embeddings.shape[1])

    start_position = len(chunk_store)
    faiss_index.add(embeddings)

    for i, chunk in enumerate(chunks):
        chunk_store.append({
            "position": start_position + i,
            "doc_id": doc_id,
            "chunk_index": i,
            "chunk": chunk
        })

    save_index()   # ← persist after every upload
    print(f"[FAISS] Total chunks in index: {faiss_index.ntotal}")


def search_similar_chunks(query: str, top_k: int = 3) -> list[dict]:
    global faiss_index, chunk_store

    if faiss_index is None or faiss_index.ntotal == 0:
        return []

    query_vector = get_embedding(query)
    distances, indices = faiss_index.search(query_vector, top_k)

    results = []
    for distance, idx in zip(distances[0], indices[0]):
        if idx == -1:
            continue
        chunk_data = chunk_store[idx]
        results.append({
            "chunk": chunk_data["chunk"],
            "doc_id": chunk_data["doc_id"],
            "chunk_index": chunk_data["chunk_index"],
            "distance": float(distance)
        })

    return results


def get_index_stats() -> dict:
    return {
        "total_chunks": faiss_index.ntotal if faiss_index else 0,
        "total_documents": len(set(c["doc_id"] for c in chunk_store)),
        "embedding_model": EMBEDDING_MODEL
    }


# Load on startup automatically
load_index()