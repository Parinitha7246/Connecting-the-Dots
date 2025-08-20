from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app import config
from app.services.tts_service import generate_audio # <-- Import the new, single unified function

router = APIRouter()

# The Pydantic model is correct and expects the data from the frontend.
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

    # --- Script building logic (this is correct) ---
    intro = f"Hello, and welcome to this audio briefing. Based on your recent document selection, here are the key points and connections we've found."
    body_points = [f"Point {i+1}: {text}" for i, text in enumerate(req.section_texts)]
    body = "\n".join(body_points)
    outro = "This concludes the briefing. For a deeper dive, please refer to the documents in the application."
    script = "\n\n".join([intro, body, outro])

    # --- THIS IS THE NEW, CLEANER, AND CORRECT WAY TO GENERATE AUDIO ---
    # We now make a single call to the unified 'generate_audio' function.
    # It will automatically handle the logic of checking the TTS_PROVIDER environment variable
    # and calling the correct service (Azure, GCP, or local).
    
    print(f"[INFO] Generating podcast with script: '{script[:100]}...'")
    
    # We pass the script and the directory where the audio file should be saved.
    tts_result = generate_audio(script, config.OUTPUT_DIR)
    
    # Check if the TTS service returned an error.
    if "error" in tts_result:
        # If there was an error, return a 500 status code with the error message.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=tts_result["error"]
        )
        
    # If successful, return the script and the TTS result (which contains the URL).
    return {"script": script, "tts": tts_result}