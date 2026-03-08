import os
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from app.core.config import FAISS_INDEX_DIR, EMBEDDING_MODEL

# ── Load Embedding Model (runs once at startup) ────────────────────────
print("[FAISS] Loading embedding model...")
embedder = SentenceTransformer(EMBEDDING_MODEL)
print("[FAISS] Embedding model loaded!")

# ── In-memory store ────────────────────────────────────────────────────
# maps index position → {"doc_id": ..., "chunk": ..., "chunk_index": ...}
chunk_store: list[dict] = []
faiss_index = None   # will be initialized on first document


# ── Helpers ────────────────────────────────────────────────────────────

def get_embedding(text: str) -> np.ndarray:
    """Convert a single text string into a vector."""
    embedding = embedder.encode([text], convert_to_numpy=True)
    return embedding.astype("float32")


def get_embeddings(texts: list[str]) -> np.ndarray:
    """Convert a list of text strings into vectors."""
    embeddings = embedder.encode(texts, convert_to_numpy=True)
    return embeddings.astype("float32")


# ── Core FAISS Operations ──────────────────────────────────────────────

def init_index(dimension: int):
    """
    Create a new FAISS index.
    IndexFlatL2 = exact search using L2 (euclidean) distance.
    Simple and accurate — good for learning projects.
    """
    global faiss_index
    faiss_index = faiss.IndexFlatL2(dimension)
    print(f"[FAISS] Index initialized with dimension {dimension}")


def add_document_to_index(doc_id: str, chunks: list[str]):
    """
    Convert chunks to embeddings and add to FAISS index.
    Also saves chunk text to chunk_store for retrieval later.
    """
    global faiss_index, chunk_store

    if not chunks:
        raise ValueError("No chunks to add")

    print(f"[FAISS] Embedding {len(chunks)} chunks for doc {doc_id}...")

    # Convert chunks to vectors
    embeddings = get_embeddings(chunks)

    # Initialize index on first document
    if faiss_index is None:
        init_index(dimension=embeddings.shape[1])

    # Store position BEFORE adding (so we know which index = which chunk)
    start_position = len(chunk_store)

    # Add vectors to FAISS
    faiss_index.add(embeddings)

    # Save chunk text + metadata to chunk_store
    for i, chunk in enumerate(chunks):
        chunk_store.append({
            "position": start_position + i,
            "doc_id": doc_id,
            "chunk_index": i,
            "chunk": chunk
        })

    print(f"[FAISS] Added {len(chunks)} chunks. Total in index: {faiss_index.ntotal}")


def search_similar_chunks(query: str, top_k: int = 3) -> list[dict]:
    """
    Find the top_k most similar chunks to the query.

    Steps:
    1. Convert query to vector
    2. Search FAISS for closest vectors
    3. Return the matching chunk texts
    """
    global faiss_index, chunk_store

    if faiss_index is None or faiss_index.ntotal == 0:
        return []

    # Convert query to vector
    query_vector = get_embedding(query)

    # Search FAISS — returns distances and indices
    distances, indices = faiss_index.search(query_vector, top_k)

    results = []
    for distance, idx in zip(distances[0], indices[0]):
        if idx == -1:   # FAISS returns -1 if not enough results
            continue
        chunk_data = chunk_store[idx]
        results.append({
            "chunk": chunk_data["chunk"],
            "doc_id": chunk_data["doc_id"],
            "chunk_index": chunk_data["chunk_index"],
            "distance": float(distance)   # lower = more similar
        })

    return results


def get_index_stats() -> dict:
    """Return current state of the FAISS index."""
    return {
        "total_chunks": faiss_index.ntotal if faiss_index else 0,
        "total_documents": len(set(c["doc_id"] for c in chunk_store)),
        "embedding_model": EMBEDDING_MODEL
    }