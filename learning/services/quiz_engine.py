import re
from .index_manager import load_document_index
from .gemini_client import generate_response


def generate_quiz(user_id, document_id, difficulty="medium", num_questions=5):
    index, chunks = load_document_index(user_id, document_id)

    if index is None:
        return []

    content = "\n".join(chunks[:5])
    num_questions = min(int(num_questions), 25) # Cap at 25

    prompt = f"""
    Generate {num_questions} {difficulty} level multiple choice questions.

    Format strictly:

    Question: ...
    A) ...
    B) ...
    C) ...
    D) ...
    Correct Answer: A/B/C/D

    Content:
    {content}
    """

    response = generate_response(prompt)

    if not response:
        return []

    questions = []

    pattern = r"Question:\s*(.*?)\nA\)\s*(.*?)\nB\)\s*(.*?)\nC\)\s*(.*?)\nD\)\s*(.*?)\nCorrect Answer:\s*([ABCD])"
    matches = re.findall(pattern, response, re.DOTALL)

    for match in matches:
        questions.append({
            "question": match[0].strip(),
            "A": match[1].strip(),
            "B": match[2].strip(),
            "C": match[3].strip(),
            "D": match[4].strip(),
            "correct": match[5].strip()
        })

    return questions