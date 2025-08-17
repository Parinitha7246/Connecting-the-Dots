# backend/app/services/multi_doc_service.py
from typing import List, Dict, Any
import numpy as np
# from app.utils import clean_text, excerpt # Assuming these are available and correctly imported
import math
from collections import defaultdict
import hashlib # For robust deduplication
import datetime # For fallback for file_mtime

# Placeholder for clean_text and excerpt if they are not external utilities.
# You should ensure your 'app/utils.py' has these or equivalent functions.
def clean_text(text: str) -> str:
    """Removes extra whitespace and cleans up text."""
    if not isinstance(text, str):
        return ""
    return ' '.join(text.split()).strip()

def excerpt(text: str, max_sentences: int = 3) -> str:
    """Generates a short excerpt of text, limited by sentences."""
    if not isinstance(text, str):
        return ""
    # Simple sentence tokenizer based on period, may need refinement for complex cases
    sentences = text.replace('\n', ' ').split('.')
    relevant_sentences = [s.strip() for s in sentences if s.strip()]
    
    snippet = '. '.join(relevant_sentences[:max_sentences])
    if len(relevant_sentences) > max_sentences and snippet:
        snippet += '.' # Add a period if more sentences were truncated
    return snippet

def merge_and_rank(same_subs: List[Dict[str,Any]], other_subs: List[Dict[str,Any]], top_k: int=5) -> Dict[str, Any]:
    """
    Merge two lists (current, historical). Rank by score.
    Generate short 2–4 sentence snippets for preview.
    """
    all_subs = []
    for s in same_subs + other_subs:
        s = dict(s)
        s['text'] = clean_text(s.get('text',''))
        # Fallback score is now less critical as embed_search_in_dir provides accurate scores.
        # It's kept for robustness if some items might somehow lack a score.
        s.setdefault('score', min(1.0, 0.01 * max(10, len(s['text'].split()))))
        all_subs.append(s)

    # Deduplicate
    seen = set()
    unique = []
    for s in all_subs:
        # Improved deduplication key: use document, page_number, and a hash of the cleaned text.
        # This makes it more robust against minor text variations or different excerpt generations.
        doc = s.get('document','')
        page = s.get('page_number','')
        # Hash a significant portion of the text for robust content-based deduplication
        text_content_for_hash = s.get('text','').encode('utf-8')
        text_hash = hashlib.md5(text_content_for_hash).hexdigest()
        
        k = (doc, page, text_hash)
        
        if k in seen:
            continue
        seen.add(k)
        unique.append(s)

    # Sort by primary search score first, then by label_score (if applicable)
    unique.sort(key=lambda x: (x.get('score',0), x.get('label_score',0)), reverse=True)

    # Label classification:
    # (Limitation: This keyword-based approach is simple and fast, but can be inaccurate/brittle.
    # For higher quality and nuanced classification, consider using a dedicated text classification
    # model (e.g., fine-tuned BERT/RoBERTa) or an LLM-based labeling approach if available.)
    for u in unique:
        txt = u.get('text','').lower()
        if any(word in txt for word in ['however', 'but', 'contradict', 'contrary', 'not consistent', 'disagree', 'fail', 'limitations']):
            u['label'] = 'contradiction'
            u['label_score'] = 0.9
        elif any(word in txt for word in ['for example', 'e.g.', 'case', 'experiment', 'we evaluated', 'study shows', 'dataset']):
            u['label'] = 'example'
            u['label_score'] = 0.7
        elif len(txt.split()) > 12: # Heuristic: longer text implies more 'supporting' detail
            u['label'] = 'supporting'
            u['label_score'] = 0.5
        else:
            u['label'] = 'related'
            u['label_score'] = 0.3

    # Build time-machine
    # (Limitation: 'idea' grouping by a short excerpt is very coarse and may not accurately
    # capture semantic distinctiveness. For a more robust time-machine, consider using
    # sentence embeddings for clustering 'ideas' or relying on more structured document
    # parsing for precise topic identification.)
    time_machine = _build_time_machine(unique)

    # Build results with snippet
    result = []
    for i, u in enumerate(unique[:top_k], 1):
        snippet_text = excerpt(u.get("text",""), max_sentences=3)  # force 2–4 sentences
        result.append({
            "rank": i,
            "document": u.get("document"),
            "page_number": u.get("page_number"),
            "excerpt": u.get("excerpt") or snippet_text, # Use pre-stored excerpt if available, else generate snippet
            "snippet": snippet_text,        # explicit snippet field
            "text": u.get("text"),
            "score": float(u.get("score", 0)),
            "label": u.get("label"),
            "label_score": float(u.get("label_score", 0)),
            "file_mtime": u.get("file_mtime", "") # Ensure file_mtime is passed through for time_machine
        })
    return {"recommendations": result, "time_machine": time_machine}

def _build_time_machine(subs: List[Dict[str,Any]]) -> List[Dict[str,str]]:
    """
    For each distinct 'idea' (approx. by normalized excerpt), find first seen / latest contradiction.
    Groups by the first 100 characters of the excerpt for heuristic "idea" identification.
    """
    groups = {}
    for s in subs:
        # Use a more robust key for grouping ideas, e.g., a hash of a larger portion of the text
        key = (s.get('excerpt','')[:100]).strip().lower() # Use up to 100 chars of excerpt
        if not key: continue
        
        rec = groups.get(key, {"first_seen": None, "first_doc": None, "contradictions": []})
        
        # file_mtime should be passed from the ingest/search results.
        # It's a timestamp (float). Convert to readable format if needed for display.
        s_file_mtime = s.get("file_mtime")
        
        if s_file_mtime is not None:
             if not rec["first_seen"] or s_file_mtime < rec["first_seen"]:
                 rec["first_seen"] = s_file_mtime
                 rec["first_doc"] = s.get("document")

        # contradictions
        if s.get("label") == "contradiction" and s_file_mtime is not None:
            rec["contradictions"].append({"doc": s.get("document"), "when": s_file_mtime})
        groups[key] = rec

    # prepare array
    tm = []
    for k,v in groups.items():
        if v["first_seen"] is not None: # Only add if first_seen was populated
            # Convert timestamp back to ISO format or desired string format for output
            first_seen_iso = datetime.datetime.fromtimestamp(v["first_seen"], tz=datetime.timezone.utc).isoformat()
            latest_contradiction_info = None
            if v["contradictions"]:
                # Sort contradictions by time to get the latest
                sorted_contradictions = sorted(v["contradictions"], key=lambda x: x["when"])
                latest_contr = sorted_contradictions[-1]
                latest_contradiction_info = {
                    "doc": latest_contr.get("doc"),
                    "when": datetime.datetime.fromtimestamp(latest_contr["when"], tz=datetime.timezone.utc).isoformat()
                }

            tm.append({
                "idea_excerpt": k[:200],
                "first_seen": first_seen_iso,
                "first_doc": v.get("first_doc"),
                "latest_contradiction": latest_contradiction_info
            })
    # sort by first_seen (oldest first)
    tm = sorted(tm, key=lambda x: x.get("first_seen") or "")
    return tm