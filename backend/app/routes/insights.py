# backend/app/routes/insights.py
from fastapi import APIRouter
from pydantic import BaseModel
from app.services.selection_extractor_service import find_relevant_sections
from app.services.llm_service import LLMService
from app.utils import internet_available
from app import config

router = APIRouter()

class InsightsRequest(BaseModel):
    selected_text: str
    top_k: int = config.TOP_SECTIONS_COUNT

@router.post("/insights")
async def insights(payload: InsightsRequest):
    # Offline search for relevant sections
    same_doc_res = find_relevant_sections(payload.selected_text, config.DOCUMENTS_DIR)
    other_doc_res = find_relevant_sections(payload.selected_text, config.HISTORICAL_DIR)

    merged = same_doc_res + other_doc_res
    response = {"source": "offline", "offline": merged[:payload.top_k]}

    # Online enrichment (LLM)
    if config.MODE in ("online", "auto") and internet_available():
        try:
            svc = LLMService()
            offline_snips = [r["text"] for r in merged[:payload.top_k]]
            enriched = svc.enrich_with_context(
                offline_snips,
                "AutoPersona",
                f"Generate insights from: {payload.selected_text}"
            )
            response["source"] = "hybrid"
            response["online"] = enriched
        except Exception as e:
            response["online_error"] = str(e)

    return response
