from fastapi import APIRouter
from pydantic import BaseModel
from app import config
from app.services.selection_extractor_service import find_relevant_sections
from app.services.multi_doc_service import merge_and_rank
from app.utils import internet_available, excerpt
from app.services.llm_service import LLMService

router = APIRouter()

class RecommendRequest(BaseModel):
    selected_text: str
    top_k: int = config.TOP_SECTIONS_COUNT
    online: bool = False

@router.post("/recommend")
async def recommend(payload: RecommendRequest):
    # --- Step 1: Offline embedding search ---
    same_doc_res = find_relevant_sections(payload.selected_text, config.DOCUMENTS_DIR)
    other_doc_res = find_relevant_sections(payload.selected_text, config.HISTORICAL_DIR)

    merged = merge_and_rank(same_doc_res, other_doc_res, payload.top_k)
    recommendations = merged.get("recommendations", [])
    
    for rec in recommendations:
        if not rec.get("snippet"):
            rec["snippet"] = excerpt(rec.get("text", ""), max_sentences=3)

    # --- Step 2 (NEW): Use LLM for Relation Classification ---
    if payload.online and config.MODE in ("online", "auto") and internet_available():
        try:
            print("[INFO] Performing LLM classification for snippet relations...")
            llm = LLMService()
            # This call adds the 'relation_type' key to each snippet in the list
            recommendations = llm.classify_snippet_relations(payload.selected_text, recommendations)
            source = "hybrid"
        except Exception as e:
            print(f"[WARN] LLM classification failed during /recommend: {e}")
            source = "offline_classification_failed"
    else:
        source = "offline"

    # --- Step 3: Ensure every snippet has a relation_type for the frontend ---
    for rec in recommendations:
        if 'relation_type' not in rec:
            rec['relation_type'] = 'related' # Default if offline or if LLM failed

    # The 'online' part for general insights is removed, as that is now in /insights
    return {
        "source": source,
        "recommendations": recommendations,
    }