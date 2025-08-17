# backend/app/routes/recommend.py
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

@router.post("/recommend")
async def recommend(payload: RecommendRequest):
    # --- Offline embedding search ---
    same_doc_res = find_relevant_sections(payload.selected_text, config.DOCUMENTS_DIR)
    other_doc_res = find_relevant_sections(payload.selected_text, config.HISTORICAL_DIR)

    merged = merge_and_rank(same_doc_res, other_doc_res, payload.top_k)

    # Add explicit snippets (2–4 sentences extracts from section text)
    for rec in merged["recommendations"]:
        rec["snippet"] = excerpt(rec.get("text", ""), max_sentences=3)

    response = {
        "source": "offline",
        "offline": merged  # merged already contains recommendations + time_machine
    }

    # --- Online enrichment ---
    if config.MODE in ("online", "auto") and internet_available():
        try:
            svc = LLMService()
            offline_snips = [r["snippet"] for r in merged["recommendations"]]
            enriched = svc.enrich_with_context(
                offline_snips,
                "AutoPersona",
                f"Analyze selection: {payload.selected_text}"
            )
            response["source"] = "hybrid"
            response["online"] = enriched
        except Exception as e:
            response["online_error"] = str(e)

    return response
