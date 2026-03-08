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
        system_prompt = """You are a helpful assistant that answers questions 
based strictly on the provided document context.
If the answer is not found in the context, say: 
'I could not find the answer in the provided documents.'
Do not make up answers. Be concise and precise."""

        user_message = f"""Context from documents:
{context}

Question: {question}

Answer based on the context above:"""

    else:
        # Plain chat — no context
        system_prompt = """You are a helpful assistant. 
Answer clearly and concisely in 2-3 sentences maximum."""

        user_message = question

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_message}
        ],
        temperature=0.2,    # low = more factual, less creative
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
