from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.services.llm_service import LLMService
from app.utils import internet_available
from app import config
import json
import re

router = APIRouter()

# This is the correct Pydantic model for this endpoint.
# It expects a list of texts (the snippets from the frontend) to be sent for analysis.
class InsightsRequest(BaseModel):
    texts: list[str]
    persona: str = "General Researcher"
    task: str = "Find connections and insights in the provided text."

@router.post("/insights")
async def insights(payload: InsightsRequest):
    """
    This endpoint performs ONE job: It takes a list of text snippets, sends them to a
    Language Model (like Gemini), and returns structured JSON insights. It does NO offline searching.
    """
    
    # First, check if the application is in a mode that allows online calls.
    if not (config.MODE in ("online", "auto") and internet_available()):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
            detail="Cannot generate insights: Online mode is disabled or internet is unavailable."
        )

    # Validate that the frontend sent some text to be processed.
    if not payload.texts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot generate insights: The 'texts' field in the request cannot be empty."
        )

    try:
        # Initialize the LLM service (e.g., Gemini).
        svc = LLMService()
        
        # Call the LLM with the provided context from the frontend.
        enriched_string = svc.enrich_with_context(
            payload.texts,
            payload.persona,
            payload.task
        )
        
        # The LLM often returns a JSON string wrapped in markdown. We must clean and parse it.
        json_match = re.search(r'\{.*\}', enriched_string, re.DOTALL)
        if json_match:
            parsed_json = json.loads(json_match.group(0))
            # Return the clean, structured JSON object as the 'parsed' key.
            return { "source": "online", "parsed": parsed_json }
        else:
            # If the LLM response is not valid JSON, raise an error.
            raise json.JSONDecodeError("No valid JSON object found in LLM response", enriched_string, 0)
        
    except json.JSONDecodeError as e:
        print(f"[ERROR] Failed to parse LLM response: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to parse the response from the Language Model."
        )
    except Exception as e:
        # Catch any other errors from the LLM service (e.g., API key, connection issues).
        print(f"[ERROR] An error occurred while generating insights: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"An error occurred while generating insights: {str(e)}"
        )