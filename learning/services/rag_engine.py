import numpy as np
from sentence_transformers import SentenceTransformer
from .index_manager import load_document_index
from .gemini_client import generate_response

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

def generate_rag_answer(user_id, document_id, query):
    from learning.models import StudyDocument
    doc = StudyDocument.objects.get(id=document_id)
    
    if not doc.file:
        prompt = f"""
        You are an AI Study Buddy assistant.
        The user is asking a general question without any specific document context.
        Provide a helpful and clear response.
        Use bullet points where helpful.
        
        Question:
        {query}
        """
        return generate_response(prompt)

    index, chunks = load_document_index(user_id, document_id)

    if index is None:
        return "Index not found for this document."

    query_vector = embedding_model.encode([query])
    D, I = index.search(np.array(query_vector), 3) #noqa

    context = "\n".join([chunks[i] for i in I[0]])

    prompt = f"""
    You are an exam-oriented AI tutor.

    Use the provided context to answer clearly.
    Focus on exam-relevant explanation.
    Use bullet points where helpful.

    Context:
    {context}

    Question:
    {query}
    """

    return generate_response(prompt)