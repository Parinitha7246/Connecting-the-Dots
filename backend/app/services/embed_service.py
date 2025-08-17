# backend/app/services/embed_service.py
import os
import numpy as np
from sentence_transformers import SentenceTransformer
import json
import hashlib
import time
from typing import Dict, List, Tuple, Any


_model = None
# Cache for preloaded embeddings (no Annoy)
_embeddings_cache: Dict[str, Tuple[List[Dict[str, Any]], float]] = {}

def get_model():
    """Lazy load SentenceTransformer model."""
    global _model
    if _model is None:
        model_name = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")
        print(f"Loading SentenceTransformer model: {model_name}")
        _model = SentenceTransformer(model_name)
    return _model

def embed_text(text: str) -> np.ndarray:
    model = get_model()
    text = text.strip()
    if not text:
        # return a small random vector to prevent empty embeddings (optional)
        return np.zeros(model.get_sentence_embedding_dimension())
    return model.encode(text, convert_to_numpy=True)


def _load_dir_embeddings(dir_path: str) -> List[Dict[str, Any]]:
    """
    Load all embeddings JSON files in a directory into memory.
    Cache results and reload if files change (by mtime).
    """
    cache_key = hashlib.md5(dir_path.encode("utf-8")).hexdigest()
    latest_mtime = 0
    for file in os.listdir(dir_path):
        if file.endswith("_embeddings.json"):
            latest_mtime = max(latest_mtime, os.path.getmtime(os.path.join(dir_path, file)))

    if cache_key in _embeddings_cache:
        cached_data, cached_mtime = _embeddings_cache[cache_key]
        if latest_mtime <= cached_mtime:
            return cached_data  # use cache

    # Reload embeddings
    all_sections = []
    for file in os.listdir(dir_path):
        if not file.endswith("_embeddings.json"):
            continue
        filepath = os.path.join(dir_path, file)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                for section in data:
                    vec = np.array(section.get("vector", []))
                    if vec.size == 0:
                        continue
                    all_sections.append({
                        "text": section.get("text", ""),
                        "document": section.get("document", file.replace("_embeddings.json", "")),
                        "page_number": section.get("page_number"),
                        "excerpt": section.get("excerpt", ""),
                        "source_file": file.replace("_embeddings.json", ""),
                        "file_mtime": os.path.getmtime(filepath),
                        "vector": vec
                    })
        except Exception as e:
            print(f"Error loading {filepath}: {e}")

    _embeddings_cache[cache_key] = (all_sections, latest_mtime)
    return all_sections

def embed_search_in_dir(query_vec: np.ndarray, dir_path: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Perform cosine similarity search using NumPy (fallback without Annoy).
    """
    all_sections = _load_dir_embeddings(dir_path)
    if not all_sections:
        return []

    if not isinstance(query_vec, np.ndarray) or query_vec.size == 0:
        print("Warning: Empty or invalid query vector")
        return []

    # Normalize query
    query_norm = np.linalg.norm(query_vec)
    if query_norm == 0:
        return []

    results = []
    for section in all_sections:
        vec = section["vector"]
        sim = float(np.dot(query_vec, vec) / (query_norm * np.linalg.norm(vec)))
        item = dict(section)
        item.pop("vector", None)  # don’t return big vectors
        item["score"] = sim
        results.append(item)

    results = sorted(results, key=lambda x: x["score"], reverse=True)
    return results[:top_k]
