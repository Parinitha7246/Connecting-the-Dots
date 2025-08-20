import os
import subprocess
import requests
from pathlib import Path
import uuid

# Base URL for constructing web-accessible file URLs
BASE_URL = "http://127.0.0.1:8000"

def generate_audio(text: str, output_dir: str, provider: str = None, voice: str = None) -> dict:
    """
    Unified function to generate audio from text. It dispatches to the correct provider
    based on the TTS_PROVIDER environment variable, matching the hackathon's test script.

    Args:
        text (str): Text to convert to speech.
        output_dir (str): The directory to save the final audio file in.
        provider (str, optional): Override the TTS_PROVIDER env var.
        voice (str, optional): Override the default voice for the chosen provider.
    
    Returns:
        dict: A dictionary containing the 'url' to the audio file or an 'error'.
    """
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")
    
    provider = (provider or os.getenv("TTS_PROVIDER", "local")).lower()
    
    # Ensure the output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    filename = f"podcast_{provider}_{uuid.uuid4().hex}.mp3"
    output_file = os.path.join(output_dir, filename)

    try:
        if provider == "azure":
            _generate_azure_tts(text, output_file, voice)
        elif provider == "gcp":
            _generate_gcp_tts(text, output_file, voice)
        elif provider == "local":
            _generate_local_tts(text, output_file, voice)
        else:
            raise ValueError(f"Unsupported TTS_PROVIDER: {provider}")
        
        # If successful, return the full, web-accessible URL
        full_url = f"{BASE_URL}/static/output/{filename}"
        return {"url": full_url, "provider": provider}

    except Exception as e:
        print(f"[ERROR] TTS generation failed for provider '{provider}': {e}")
        return {"error": f"TTS generation failed: {e}"}

def _generate_azure_tts(text, output_file, voice=None):
    """Generates audio using Azure OpenAI TTS."""
    api_key = os.getenv("AZURE_TTS_KEY")
    endpoint = os.getenv("AZURE_TTS_ENDPOINT")
    deployment = os.getenv("AZURE_TTS_DEPLOYMENT", "tts")
    api_version = os.getenv("AZURE_TTS_API_VERSION", "2024-02-15-preview")
    voice = voice or os.getenv("AZURE_TTS_VOICE", "alloy")
    
    if not api_key or not endpoint:
        raise ValueError("AZURE_TTS_KEY and AZURE_TTS_ENDPOINT must be set.")
    
    headers = {"api-key": api_key, "Content-Type": "application/json"}
    payload = {"model": deployment, "input": text, "voice": voice}
    
    response = requests.post(
        f"{endpoint}/openai/deployments/{deployment}/audio/speech?api-version={api_version}",
        headers=headers, json=payload, timeout=60
    )
    response.raise_for_status()
    
    with open(output_file, "wb") as f:
        f.write(response.content)
    print(f"Azure TTS audio saved to: {output_file}")

def _generate_gcp_tts(text, output_file, voice=None):
    """Generates audio using Google Cloud Text-to-Speech."""
    from google.cloud import texttospeech
    
    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        raise ValueError("GOOGLE_APPLICATION_CREDENTIALS must be set for Google Cloud TTS.")

    client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice_params = texttospeech.VoiceSelectionParams(
        language_code=os.getenv("GCP_TTS_LANGUAGE", "en-US"),
        name=voice or os.getenv("GCP_TTS_VOICE", "en-US-Neural2-C")
    )
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
    
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice_params, audio_config=audio_config
    )
    with open(output_file, "wb") as f:
        f.write(response.audio_content)
    print(f"Google Cloud TTS audio saved to: {output_file}")

def _generate_local_tts(text, output_file, voice=None):
    """Generates audio using local pyttsx3."""
    import pyttsx3
    engine = pyttsx3.init()
    engine.save_to_file(text, output_file)
    engine.runAndWait()
    print(f"Local TTS (pyttsx3) audio saved to: {output_file}")