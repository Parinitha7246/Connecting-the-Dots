# app/services/hybrid_service.py
from app.services import persona_extractor_service, llm_service
from app.services.multi_doc_service import merge_and_rank
from app.utils import internet_available
from app import config

def hybrid_search(persona, job, top_k):
    # Always run offline fast
    same_doc_res = persona_extractor_service.run_persona_extractor(persona, job, config.DOCUMENTS_DIR)
    other_doc_res = persona_extractor_service.run_persona_extractor(persona, job, config.HISTORICAL_DIR)
    offline_merged = merge_and_rank(
        same_doc_res.get("subsection_analysis", []),
        other_doc_res.get("subsection_analysis", []),
        top_k
    )

    if config.MODE == "offline":
        return {"source": "offline", "recommendations": offline_merged}

    if config.MODE == "online" or (config.MODE == "auto" and internet_available()):
        # Pass offline results into LLM for enrichment
        enriched = llm_service.enrich_with_context(offline_merged, persona, job)
        return {"source": "hybrid", "offline": offline_merged, "online": enriched}

    # Fallback
    return {"source": "offline-fallback", "recommendations": offline_merged}
