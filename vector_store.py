import os
import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import config

def _ensure_dirs():
    os.makedirs(config.EMBEDDINGS_DIR, exist_ok=True)

def _get_model(model_name=None):
    return SentenceTransformer(model_name or config.EMBEDDING_MODEL)

def create_vector_store(docs, store_path=None, metadata_path=None, model_name=None):
    """Build a new FAISS index from scratch and persist to disk."""
    _ensure_dirs()
    store_path = store_path or config.VECTOR_STORE_PATH
    metadata_path = metadata_path or config.METADATA_PATH
    model_name = model_name or config.EMBEDDING_MODEL

    model = _get_model(model_name)
    texts = [d["content"] for d in docs]
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=True)

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    with open(store_path, "wb") as f:
        pickle.dump((index, model_name), f)
    with open(metadata_path, "wb") as f:
        pickle.dump(docs, f)

def load_vector_store(store_path=None, metadata_path=None):
    store_path = store_path or config.VECTOR_STORE_PATH
    metadata_path = metadata_path or config.METADATA_PATH
    if not (os.path.exists(store_path) and os.path.exists(metadata_path)):
        raise FileNotFoundError("Vector store not found. Build it first.")
    with open(store_path, "rb") as f:
        index, model_name = pickle.load(f)
    with open(metadata_path, "rb") as f:
        docs = pickle.load(f)
    return index, docs, model_name

def save_vector_store(index, docs, model_name, store_path=None, metadata_path=None):
    _ensure_dirs()
    store_path = store_path or config.VECTOR_STORE_PATH
    metadata_path = metadata_path or config.METADATA_PATH
    with open(store_path, "wb") as f:
        pickle.dump((index, model_name), f)
    with open(metadata_path, "wb") as f:
        pickle.dump(docs, f)

def append_documents(new_docs):
    """
    Incrementally add new chunks to the existing index.
    If index doesn't exist, creates it.
    """
    try:
        index, docs, model_name = load_vector_store()
    except FileNotFoundError:
        create_vector_store(new_docs)
        return

    model = _get_model(model_name)
    texts = [d["content"] for d in new_docs]
    if not texts:
        return
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    index.add(embeddings)
    docs.extend(new_docs)
    save_vector_store(index, docs, model_name)

def search(query, top_k=None):
    top_k = top_k or config.DEFAULT_TOP_K
    index, docs, model_name = load_vector_store()
    model = _get_model(model_name)
    query_emb = model.encode([query], convert_to_numpy=True)
    D, I = index.search(query_emb, top_k)

    results = []
    for rank, i in enumerate(I[0]):
        if i == -1:
            continue
        # Similarity heuristic from L2 distance:
        score = float(1 - (D[0][rank] / 2))
        results.append({"doc": docs[i], "score": score})
    return results
