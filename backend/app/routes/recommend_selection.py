from fastapi import APIRouter
from pydantic import BaseModel
from app import config
from app.services.selection_extractor_service import find_relevant_sections
from app.services.multi_doc_service import merge_and_rank
from app.utils import internet_available
from app.services.llm_service import LLMService

router = APIRouter()

class SelectionRequest(BaseModel):
    selected_text: str
    top_k: int = config.TOP_SECTIONS_COUNT

@router.post("/recommend-selection")
async def recommend_selection(payload: SelectionRequest):
    # --- Offline search ---
    same_doc_res = find_relevant_sections(payload.selected_text, config.DOCUMENTS_DIR)
    other_doc_res = find_relevant_sections(payload.selected_text, config.HISTORICAL_DIR)

    merged = merge_and_rank(same_doc_res, other_doc_res, payload.top_k)
    response = {"source": "offline", "offline": merged}

    # --- Online enrichment ---
    if config.MODE in ("online", "auto") and internet_available():
        try:
            svc = LLMService()
            offline_snips = [r["text"] for r in merged]  # merged = list of matches
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
