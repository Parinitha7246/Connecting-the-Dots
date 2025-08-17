import os
from app.services.embed_service import embed_text, embed_search_in_dir

def find_relevant_sections(query_text: str, dir_path: str):
    if not os.path.exists(dir_path):
        return []
    # embed query
    query_vec = embed_text(query_text)
    # search all sections/snippets in this dir
    results = embed_search_in_dir(query_vec, dir_path)
    return results
