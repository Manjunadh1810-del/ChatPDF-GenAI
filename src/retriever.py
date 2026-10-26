import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

def build_index(chunks: list[dict]):
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    texts = [chunk["text"] for chunk in chunks]
    vectors = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True,
                           show_progress_bar=False).astype("float32")
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)
    return index, model

def retrieve(question: str, chunks: list[dict], index, model, top_k: int = 4) -> list[dict]:
    query_vector = model.encode([question], convert_to_numpy=True,
                                normalize_embeddings=True).astype("float32")
    scores, ids = index.search(query_vector, min(top_k, len(chunks)))
    results = []
    for score, idx in zip(scores[0], ids[0]):
        if idx < 0:
            continue
        item = dict(chunks[int(idx)])
        item["score"] = float(score)
        results.append(item)
    return results
