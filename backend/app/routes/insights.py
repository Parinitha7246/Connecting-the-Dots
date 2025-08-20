from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.services.llm_service import LLMService, LLMError
from app.utils import internet_available
from app import config
import json

router = APIRouter()

class InsightsRequest(BaseModel):
    texts: list[str]
    persona: str = "General Researcher"
    task: str = "Find connections and insights in the provided text."

@router.post("/insights")
async def insights(payload: InsightsRequest):
    if not (config.MODE in ("online", "auto") and internet_available()):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
            detail="Cannot generate insights: Online mode is disabled."
        )
    if not payload.texts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot generate insights: 'texts' field cannot be empty."
        )

    try:
        svc = LLMService()
        # The enrich_with_context function will now handle parsing and return a dictionary
        parsed_json = svc.enrich_with_context(
            payload.texts,
            payload.persona,
            payload.task
        )
        
        return { "source": "online", "parsed": parsed_json }
        
    except LLMError as e:
        # This catches errors from the LLM service, including parsing failures
        print(f"[ERROR] LLMError in /insights: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=str(e)
        )
    except Exception as e:
        # Catch any other unexpected errors
        print(f"[ERROR] An unexpected error occurred in /insights: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )
