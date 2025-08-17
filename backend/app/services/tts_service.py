import os
import uuid
from pathlib import Path
from app import config
from google.cloud import texttospeech

# Online: Google Cloud TTS
def synthesize_google_tts(text: str, voice: str = "en-US-Neural2-C", speaking_rate: float = 1.0):
    """
    Requires:
      - TTS_PROVIDER=google
      - GOOGLE_APPLICATION_CREDENTIALS=/app/xxx.json (mounted)
      - google-cloud-texttospeech installed
    """
    try:
        from google.cloud import texttospeech
    except Exception as e:
        return {"error": f"google-cloud-texttospeech not installed: {e}"}

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

        return {"audio_path": str(outpath), "provider": "google"}
    except Exception as e:
        return {"error": f"Google TTS failed: {e}"}

# Offline fallback: no audio, just transcript
def synthesize_local_tts(text: str):
    """
    Offline fallback: write transcript to output and return info.
    (No audio generation to avoid heavy deps / device constraints in Docker.)
    """
    out_dir = Path(config.OUTPUT_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = f"podcast_{uuid.uuid4().hex}.txt"
    outpath = out_dir / filename
    with open(outpath, "w", encoding="utf-8") as f:
        f.write(text)
    return {
        "audio_path": None,
        "transcript_path": str(outpath),
        "provider": "local",
        "note": "Offline mode: audio not generated; transcript saved instead."
    }



def synthesize_google_tts(text: str, voice: str = "en-US-Neural2-C", speaking_rate: float = 1.0):
    client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=text)

    voice_params = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name=voice
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=speaking_rate
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

    return {"audio_path": str(outpath), "provider": "google"}
def synthesize_azure_ssml(ssml: str):
    # existing implementation you had earlier (post to Azure TTS)
    key = os.getenv("AZURE_TTS_KEY")
    endpoint = os.getenv("AZURE_TTS_ENDPOINT")
    if not key or not endpoint:
        return {"error": "Azure TTS not configured."}
    # you had a working impl earlier — reuse it here
    from . import _azure_tts_impl
    return _azure_tts_impl(ssml)

