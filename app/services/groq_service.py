from groq import Groq
from app.core.config import GROQ_API_KEY, GROQ_MODEL

# Initialize client once at startup
client = Groq(api_key=GROQ_API_KEY)


def get_groq_response(question: str, context: str = "") -> str:
    """
    Send question + context to Groq and get a response.
    If context is empty → plain chat.
    If context provided → RAG mode.
    """

    if context.strip():
        # RAG prompt — context injected here
        system_prompt = """You are a helpful assistant analyzing documents.
Answer the question using the provided context.
Summarize and explain what you find in a clear, conversational way.
If the context contains partial information, use it to give the best possible answer.
Only say you cannot find the answer if the context is completely unrelated to the question."""

        user_message = f"""Context from documents:
{context}

Question: {question}

Answer based on the context above:"""

    else:
        # Plain chat — no context
        system_prompt = """You are a helpful assistant.
Answer clearly and conversationally.
For factual questions like math, give direct answers.
For general questions, be concise and helpful."""

        user_message = question

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_message}
        ],
        temperature=0.3,
        max_tokens=512
    )

    return response.choices[0].message.content


def check_groq_connection() -> bool:
    """Test if Groq API is reachable."""
    try:
        get_groq_response("Say OK")
        return True
    except Exception:
        return False