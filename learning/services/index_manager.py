import os
import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from django.conf import settings

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')


def chunk_text(text, chunk_size=500):
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]



def build_and_save_index(user_id, document_id, text):
    chunks = chunk_text(text)
    embeddings = embedding_model.encode(chunks)

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))

    index_path = os.path.join(
        settings.MEDIA_ROOT,
        "indices",
        f"user_{user_id}_doc_{document_id}.index"
    )

    chunk_path = os.path.join(
        settings.MEDIA_ROOT,
        "indices",
        f"user_{user_id}_doc_{document_id}_chunks.pkl"
    )

    faiss.write_index(index, index_path)

    with open(chunk_path, "wb") as f:
        pickle.dump(chunks, f)


def load_document_index(user_id, document_id):
    index_path = os.path.join(
        settings.MEDIA_ROOT,
        "indices",
        f"user_{user_id}_doc_{document_id}.index"
    )

    chunk_path = os.path.join(
        settings.MEDIA_ROOT,
        "indices",
        f"user_{user_id}_doc_{document_id}_chunks.pkl"
    )

    if not os.path.exists(index_path) or not os.path.exists(chunk_path):
        return None, None   

    index = faiss.read_index(index_path)

    with open(chunk_path, "rb") as f:
        chunks = pickle.load(f)

    return index, chunks
