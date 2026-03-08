from app.services.faiss_services import search_similar_chunks
from app.services.groq_service import get_groq_response
from app.core.config import TOP_K_CHUNKS, MIN_RELEVANCE_SCORE


def build_context(chunks: list[dict]) -> str:
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        context_parts.append(f"[Chunk {i} | Doc: {chunk['doc_id']}]\n{chunk['chunk']}")
    return "\n\n".join(context_parts)


def get_rag_response(question: str, doc_id: str = None) -> dict:
    raw_results = search_similar_chunks(query=question, top_k=TOP_K_CHUNKS)

    if doc_id:
        raw_results = [r for r in raw_results if r["doc_id"] == doc_id]

    relevant_chunks = [r for r in raw_results if r["distance"] <= MIN_RELEVANCE_SCORE]

    print(f"[RAG] Question: {question}")
    print(f"[RAG] Chunks found: {len(relevant_chunks)}, distances: {[round(r['distance'],3) for r in relevant_chunks]}")

    if not relevant_chunks:
        # ← fallback to plain Groq instead of hardcoded message
        print(f"[RAG] No relevant chunks — falling back to plain Groq")
        answer = get_groq_response(question=question, context="")
        return {
            "question": question,
            "answer": answer,
            "sources": [],
            "chunks_used": 0
        }

    context = build_context(relevant_chunks)
    answer = get_groq_response(question=question, context=context)

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