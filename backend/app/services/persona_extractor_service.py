# backend/app/services/persona_extractor_service.py
import os, json
from typing import Dict, Any, List
from app import config
from app.utils import clean_text, excerpt, file_mtime_iso

# We expect engines/round1b/persona_extractor.py to export process_pdfs(persona, job).
# The wrapper will call it and normalize structure to have:
# { metadata:..., subsection_analysis: [ {document, refined_text, page_number, score?} ] }

ENG_ROUND1B = "engines.round1b.persona_extractor"

def run_persona_extractor(persona: str, job: str, input_dir: str) -> Dict[str, Any]:
    # Monkeypatch input dir if round1b uses global constants:
    # Some versions of your round1b use INPUT_DIR/OUTPUT_FILE constants; we set env or attributes if required.
    import importlib
    try:
        module = importlib.import_module(ENG_ROUND1B)
    except Exception as e:
        raise RuntimeError(f"Could not import round1b engine ({ENG_ROUND1B}): {e}")

    # If the module exposes process_pdfs(persona,job) use it
    if hasattr(module, "process_pdfs"):
        # Some modules expect INPUT_DIR and OUTPUT_FILE constants; set attributes if present
        setattr(module, "INPUT_DIR", input_dir)
        setattr(module, "OUTPUT_FILE", os.path.join(config.OUTPUT_DIR, "persona_temp_output.json"))
        # Call and retrieve file-based or returned result
        result = module.process_pdfs(persona, job)
        # If the module wrote to OUTPUT_FILE, try to read it
        if isinstance(result, dict):
            return _normalize_result(result, input_dir)
        else:
            # some older code writes file but returns None
            outf = getattr(module, "OUTPUT_FILE", None)
            if outf and os.path.exists(outf):
                with open(outf, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return _normalize_result(data, input_dir)
            return {"metadata": {}, "subsection_analysis": []}
    else:
        raise RuntimeError("Round1b engine must export process_pdfs(persona, job)")

def _normalize_result(raw: Dict[str, Any], input_dir: str) -> Dict[str, Any]:
    # raw expected keys: metadata, subsection_analysis
    meta = raw.get("metadata", {})
    subs = raw.get("subsection_analysis", [])
    norm_subs = []
    for s in subs:
        # s might be {document, refined_text, page_number}
        doc = s.get("document") or ""
        text = s.get("refined_text") or s.get("content") or s.get("text") or ""
        page = s.get("page_number") or s.get("page") or None
        score = float(s.get("score", 0)) if s.get("score") is not None else 0.0
        # store file mtime so time-machine can use it
        docpath = os.path.join(input_dir, doc) if doc else ""
        mtime = file_mtime_iso(docpath) if docpath and os.path.exists(docpath) else ""
        norm_subs.append({
            "document": doc,
            "page_number": page,
            "text": clean_text(text),
            "excerpt": excerpt(text, max_chars=300),
            "score": score,
            "file_mtime": mtime
        })
    return {"metadata": meta, "subsection_analysis": norm_subs}
