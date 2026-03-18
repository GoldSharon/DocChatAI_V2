from groq import Groq
from app.core.config import GROQ_API_KEY, GROQ_MODEL

client = Groq(api_key=GROQ_API_KEY)


def get_groq_response(question: str, context: str = "", memory: list = None) -> str:
    """
    Strict grounded response with optional memory.
    """

    memory_text = ""
    if memory:
        memory_text = "\nPrevious conversation:\n"
        for m in memory:
            memory_text += f"Q: {m['question']}\nA: {m['answer']}\n"

    if context.strip():
        # 🔥 STRICT RAG PROMPT (fix hallucination)
        system_prompt = """
You are a strict document question answering system.

Rules:
- Answer ONLY from the provided context
- Do NOT add external knowledge
- Do NOT assume anything
- If answer is not found, say: "Not found in document"
- Use exact phrases from context when possible
- Keep answer concise and factual
"""

        user_message = f"""
{memory_text}

Context:
{context}

Question:
{question}

Answer:
"""

    else:
        system_prompt = """
You are a helpful assistant.
Answer clearly and concisely.
"""

        user_message = question

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": user_message.strip()}
        ],
        temperature=0.2  # 🔥 lower = less hallucination
        
    )

    return response.choices[0].message.content
    
def check_groq_connection() -> bool:
    """Test if Groq API is reachable."""
    try:
        get_groq_response("Say OK")
        return True
    except Exception:
        return False
