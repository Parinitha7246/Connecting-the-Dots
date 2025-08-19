from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app import config
from app.utils import internet_available
from app.services.tts_service import synthesize_google_tts, synthesize_azure_ssml, synthesize_local_tts
import os
import uuid

router = APIRouter()

# --- THIS IS THE FIX ---
# The Pydantic model now correctly expects a list of texts from the frontend.
class PodcastRequest(BaseModel):
    section_texts: list[str]
    persona: str = "Narrator"
    task: str = "Create a short podcast summary"

@router.post("/podcast")
async def podcast(req: PodcastRequest):
    if not req.section_texts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot generate podcast: 'section_texts' cannot be empty."
        )

    # --- Script building is now simpler and more direct ---
    # We use the rich context already provided by the frontend.
    intro = f"Hello, and welcome to this audio briefing. Based on your recent document selection, here are the key points and connections we've found."
    
    # Create a bulleted list from the snippet texts
    body_points = [f"Point {i+1}: {text}" for i, text in enumerate(req.section_texts)]
    body = "\n".join(body_points)
    
    outro = "This concludes the briefing. For a deeper dive, please refer to the documents in the application."

    script = "\n\n".join([intro, body, outro])

    # --- TTS Generation Logic ---
    # This part remains mostly the same, but we add a check for the provider.
    tts_provider = (os.getenv("TTS_PROVIDER") or "local").lower()
    
    try:
        if tts_provider == "azure" and internet_available():
            print("[INFO] Synthesizing with Azure TTS...")
            # Note: You would need to create a simple SSML string here if needed.
            # For now, we'll assume synthesize_azure_ssml can handle plain text.
            tts_result = synthesize_azure_ssml(script)
            return {"script": script, "tts": tts_result}

        elif tts_provider == "google" and internet_available():
            print("[INFO] Synthesizing with Google TTS...")
            tts_result = synthesize_google_tts(script)
            return {"script": script, "tts": tts_result}
            
        else:
            # --- Offline/Default TTS using pyttsx3 or local file save ---
            print("[INFO] Using local TTS for podcast generation...")
            tts_result = synthesize_local_tts(script)
            return {"script": script, "tts": tts_result}

    except Exception as e:
        print(f"[ERROR] TTS generation failed: {e}")
        return {"script": script, "tts_error": f"TTS synthesis failed: {e}"}