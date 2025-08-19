import os
import uuid
from pathlib import Path
from app import config

# Base URL for constructing web-accessible file URLs
BASE_URL = "http://127.0.0.1:8000"


def synthesize_google_tts(text: str, voice: str = "en-US-Neural2-C", speaking_rate: float = 1.0):
    """
    Synthesizes text to speech using Google Cloud TTS and returns a full URL.
    Requires:
      - TTS_PROVIDER=google
      - GOOGLE_APPLICATION_CREDENTIALS=/app/xxx.json (mounted)
      - google-cloud-texttospeech installed
    """
    try:
        from google.cloud import texttospeech
    except ImportError:
        return {"error": "google-cloud-texttospeech is not installed."}

    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        return {"error": "GOOGLE_APPLICATION_CREDENTIALS is not set."}

    try:
        client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=text)

        voice_params = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name=voice
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=float(speaking_rate)
        )

        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice_params,
            audio_config=audio_config
        )

        out_dir = Path(config.OUTPUT_DIR)
        out_dir.mkdir(parents=True, exist_ok=True)
        filename = f"podcast_{uuid.uuid4().hex}.mp3"
        outpath = out_dir / filename

        with open(outpath, "wb") as f:
            f.write(response.audio_content)

        # Return a full web-accessible URL
        full_url = f"{BASE_URL}/static/output/{filename}"
        return {"url": full_url, "provider": "google"}

    except Exception as e:
        return {"error": f"Google TTS failed: {e}"}


def synthesize_local_tts(text: str):
    """
    Synthesizes text using pyttsx3 as a fallback and returns a full URL.
    """
    try:
        import pyttsx3
        engine = pyttsx3.init()

        out_dir = Path(config.OUTPUT_DIR)
        out_dir.mkdir(parents=True, exist_ok=True)
        filename = f"podcast_local_{uuid.uuid4().hex}.mp3"
        outpath = out_dir / filename

        engine.save_to_file(text, str(outpath))
        engine.runAndWait()

        # Return a full web-accessible URL
        full_url = f"{BASE_URL}/static/output/{filename}"
        return {"url": full_url, "provider": "local"}

    except Exception as e:
        return {"error": f"Local TTS failed: {e}"}


def synthesize_azure_ssml(ssml: str):
    """
    Synthesizes speech using Azure TTS (to be implemented).
    Must return a full URL like the others.
    """
    key = os.getenv("AZURE_TTS_KEY")
    endpoint = os.getenv("AZURE_TTS_ENDPOINT")
    if not key or not endpoint:
        return {"error": "Azure TTS not configured."}

    try:
        from . import _azure_tts_impl
        return _azure_tts_impl(ssml)
    except Exception as e:
        return {"error": f"Azure TTS failed: {e}"}
