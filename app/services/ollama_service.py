import ollama 
from app.core.config import OLLAMA_MODEL 

def get_ollama_responce(question: str="", context: str= ""):
    """
    Send a Question to Ollama and get a responce  .
    If context is provided, use it (RAG mode).
    If not, just answer directly (plain chat mode).
    """
    

    if context.strip():

        prompt =    f"""You are a helpful assistant. Use the following 
                        context to answer the question.If the answer is 
                        not in the context, say "I don't know based on 
                        the provided documents."

                        Context:
                        {context}

                        Question: {question}

                        Answer:"""
    else:
        # Plain chat prompt — used in Phase 3
        prompt = f"""You are a helpful assistant.
                    Answer the following question clearly and concisely.

                    Question: {question}

                    Answer:"""
        

    response = ollama.chat(
        model = OLLAMA_MODEL,
        messages=[
            {
                "role":"user",
                "context":prompt
            }
        ]
    )

    return response["message"]["content"]