import re
from .index_manager import load_document_index
from .gemini_client import generate_response

def generate_flashcards(user_id, document_id):
    index, chunks = load_document_index(user_id, document_id)

    if index is None:
        return []

    # Use first few chunks as content base
    content = "\n".join(chunks[:5])

    prompt = f"""
    Generate 8 concise revision flashcards from the following study material.

    Format strictly:
    Q: Question text
    A: Answer text

    Content:
    {content}
    """

    response = generate_response(prompt)

    if not response:
        return []

    # Parse flashcards
    flashcards = []
    pairs = re.findall(r"Q:\s*(.*?)\nA:\s*(.*?)(?=\nQ:|\Z)", response, re.DOTALL)

    for q, a in pairs:
        flashcards.append({
            "question": q.strip(),
            "answer": a.strip()
        })

    return flashcards
