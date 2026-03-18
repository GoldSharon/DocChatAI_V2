# app/services/memory_service.py

conversation_memory = {}


def get_memory(session_id: str):
    return conversation_memory.get(session_id, [])


def add_to_memory(session_id: str, question: str, answer: str):
    if session_id not in conversation_memory:
        conversation_memory[session_id] = []

    conversation_memory[session_id].append({
        "question": question,
        "answer": answer
    })

    # keep last 5 turns only
    conversation_memory[session_id] = conversation_memory[session_id][-5:]
