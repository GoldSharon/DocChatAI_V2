import numpy as np
from app.services.faiss_services import search_similar_chunks, get_embedder
from app.services.groq_service import get_groq_response
from app.core.config import TOP_K_CHUNKS, MIN_RELEVANCE_SCORE
from app.services.memory_service import get_memory, add_to_memory

# ── Semantic Summary Intent Detection ─────────────────────────────────

SUMMARY_INTENT_PHRASES = [
    "summarize this document",
    "what is in this file",
    "give me an overview",
    "what is this document about",
    "describe the contents of this file",
    "tell me about this document",
    "what topics are covered",
    "explain what this file contains",
    "what did I upload",
    "give me a brief idea of the document",
]

_summary_embeddings = None


def _get_summary_embeddings() -> np.ndarray:
    global _summary_embeddings
    if _summary_embeddings is None:
        _summary_embeddings = get_embedder().encode(
            SUMMARY_INTENT_PHRASES, convert_to_numpy=True
        ).astype("float32")
    return _summary_embeddings


def is_summary_question(question: str) -> bool:
    embedder = get_embedder()
    q_vec = embedder.encode([question], convert_to_numpy=True).astype("float32")

    summary_vecs = _get_summary_embeddings()

    q_norm = q_vec / (np.linalg.norm(q_vec) + 1e-10)
    s_norms = summary_vecs / (np.linalg.norm(summary_vecs, axis=1, keepdims=True) + 1e-10)

    similarities = s_norms @ q_norm.T
    max_score = float(similarities.max())

    print(f"[RAG] Summary intent score: {max_score:.3f}")
    return max_score > 0.55


# ── NEW: Question Type Detection ──────────────────────────────────────

def is_person_question(q: str) -> bool:
    q = q.lower()
    return any(x in q for x in ["who", "person", "about him", "about her", "candidate"])


# ── Improved Context Builder ──────────────────────────────────────────

def build_context(chunks: list[dict]) -> str:
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        context_parts.append(
            f"Source {i}:\n\"\"\"\n{chunk['chunk']}\n\"\"\""
        )
    return "\n\n".join(context_parts)


# ── NEW: Strict Prompt Builder ────────────────────────────────────────

def build_prompt(question: str, context: str) -> str:
    instruction = ""

    if is_person_question(question):
        instruction = "Extract and describe ONLY the person details from context."

    prompt = f"""
You are a strict document question answering system.

Instructions:
- Answer ONLY using the provided context
- Do NOT add external knowledge
- Do NOT assume anything
- If not found, say: "Not found in document"
- Use exact phrases from context when possible
- Keep answer concise and factual
- Do NOT expand technologies unless mentioned

{instruction}

Context:
{context}

Question:
{question}

Answer:
"""
    return prompt.strip()


# ── MAIN RAG FUNCTION ────────────────────────────────────────────────

def get_rag_response(question: str, doc_id: str = None, session_id: str = None) -> dict:
    # ── Import memory here (if not already at top) ──

    # ── Detect summary intent ──
    if is_summary_question(question):
        top_k = 10
        threshold = 999  # no filtering
    else:
        top_k = TOP_K_CHUNKS
        threshold = MIN_RELEVANCE_SCORE

    # ── Retrieve chunks ──
    raw_results = search_similar_chunks(query=question, top_k=top_k)

    # ── Filter by document ──
    if doc_id:
        raw_results = [r for r in raw_results if r["doc_id"] == doc_id]

    # ── Apply relevance threshold ──
    relevant_chunks = [r for r in raw_results if r["distance"] <= threshold]

    print(f"[RAG] Question: {question}")
    print(f"[RAG] Chunks found: {len(relevant_chunks)}, distances: {[round(r['distance'],3) for r in relevant_chunks]}")

    # ── Get memory (if session exists) ──
    memory = get_memory(session_id) if session_id else []

    # ── Fallback (no chunks) ──
    if not relevant_chunks:
        print(f"[RAG] No relevant chunks — falling back to plain Groq")

        answer = get_groq_response(
            question=question,
            context="",
            memory=memory
        )

        # store memory
        if session_id:
            add_to_memory(session_id, question, answer)

        return {
            "question": question,
            "answer": answer,
            "sources": [],
            "chunks_used": 0
        }

    # ── Build context ──
    context = build_context(relevant_chunks)
    print("[RAG] Context length:", len(context)) 

    # ── LLM call (with memory) ──
    answer = get_groq_response(
        question=question,
        context=context,
        memory=memory
    )

    # ── Store memory ──
    if session_id:
        add_to_memory(session_id, question, answer)

    # ── Prepare sources ──
    sources = [
        {
            "doc_id": chunk["doc_id"],
            "chunk_index": chunk["chunk_index"],
            "relevance_distance": round(chunk["distance"], 4),
            "preview": chunk["chunk"][:100] + "..."
        }
        for chunk in relevant_chunks
    ]

    return {
        "question": question,
        "answer": answer,
        "sources": sources,
        "chunks_used": len(relevant_chunks)
    }
