from app.services.faiss_services import search_similar_chunks
from app.services.groq_service import get_groq_response
from app.core.config import TOP_K_CHUNKS, MIN_RELEVANCE_SCORE


def build_context(chunks: list[dict]) -> str:
    """
    Join retrieved chunks into a single context string.
    Numbers each chunk so the LLM can reference them.
    """
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        context_parts.append(f"[Chunk {i} | Doc: {chunk['doc_id']}]\n{chunk['chunk']}")
    return "\n\n".join(context_parts)


def get_rag_response(question: str, doc_id: str = None) -> dict:
    """
    Full RAG pipeline:
    1. Search FAISS for relevant chunks
    2. Filter by relevance score
    3. Build context string
    4. Send to Groq with context
    5. Return answer + sources
    """

    # Step 1: Retrieve similar chunks
    raw_results = search_similar_chunks(
        query=question,
        top_k=TOP_K_CHUNKS
    )

    # Step 2: Filter by doc_id if specified
    if doc_id:
        raw_results = [r for r in raw_results if r["doc_id"] == doc_id]

    # Step 3: Filter by relevance (remove chunks too far away)
    relevant_chunks = [
        r for r in raw_results
        if r["distance"] <= MIN_RELEVANCE_SCORE
    ]

    # Step 4: Handle no relevant chunks found
    if not relevant_chunks:
        return {
            "question": question,
            "answer": "I could not find relevant information in the uploaded documents.",
            "sources": [],
            "chunks_used": 0
        }

    # Step 5: Build context
    context = build_context(relevant_chunks)

    # Step 6: Get answer from Groq
    answer = get_groq_response(question=question, context=context)

    # Step 7: Build sources list for response
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