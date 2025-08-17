# backend/app/routes/podcast.py
from fastapi import APIRouter
from pydantic import BaseModel
from app import config
from app.utils import internet_available
from app.services.selection_extractor_service import find_relevant_sections
from app.services.tts_service import synthesize_google_tts, synthesize_azure_ssml
import pyttsx3
import os
import uuid

router = APIRouter()

class PodcastReq(BaseModel):
    selected_text: str
    top_k: int = 5

@router.post("/podcast")
async def podcast(req: PodcastReq):
    selected_text = req.selected_text
    top_k = req.top_k

    # --- Offline search (get relevant sections from docs + historical) ---
    try:
        same_doc_res = find_relevant_sections(selected_text, config.DOCUMENTS_DIR)
        other_doc_res = find_relevant_sections(selected_text, config.HISTORICAL_DIR)
        subs = (same_doc_res + other_doc_res)[:top_k]
    except Exception as e:
        return {"error": f"Section extraction failed: {e}"}

    # Build key sections
    key_points = [s.get("excerpt") or s.get("text") for s in subs[:3] if s.get("text")]
    contradictions = [
        s.get("excerpt") or s.get("text")
        for s in subs if "however" in s.get("text", "").lower()
    ][:2]

    # --- Script building ---
    intro = f"Hello. This is a short podcast briefing based on your selected text: '{selected_text}'."
    body = "Key points:\n" + "\n".join(f"- {kp}" for kp in key_points) if key_points else "No key points found."
    contra = "Contradictions noted:\n" + "\n".join(f"- {c}" for c in contradictions) if contradictions else "No direct contradictions found."
    outro = "That's it. For more, open the related documents in the app."

    script = "\n\n".join([intro, body, contra, outro])

    # --- Online TTS (Google / Azure) ---
    if config.MODE in ("online", "auto") and internet_available() and os.getenv("TTS_PROVIDER"):
        tts_provider = os.getenv("TTS_PROVIDER").lower()
        if tts_provider == "azure":
            ssml = synthesize_azure_ssml(script)
            return {"script": script, "tts": ssml}
        elif tts_provider == "google":
            google_resp = synthesize_google_tts(script)
            return {"script": script, "tts": google_resp}
        # fallback handled below

    # --- Offline TTS using pyttsx3 ---
    try:
        engine = pyttsx3.init()
        outname = f"podcast_offline_{uuid.uuid4().hex}.mp3"
        outpath = os.path.join(config.OUTPUT_DIR, outname)
        engine.save_to_file(script, outpath)
        engine.runAndWait()
        return {"script": script, "tts": {"audio_path": outpath}}
    except Exception as e:
        return {"script": script, "tts_error": f"pyttsx3 failed: {e}"}
