import os
import shutil
from pathlib import Path


import socket
import re
from datetime import datetime


def save_upload_file_tmp(upload_file, destination_path: str):
    """Save FastAPI UploadFile to destination_path"""
    with open(destination_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    upload_file.file.close()
    return destination_path

def list_pdfs_in_dir(path):
    return [f for f in os.listdir(path) if f.lower().endswith(".pdf")]

def read_json(path):
    import json
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
    

def internet_available(host="8.8.8.8", port=53, timeout=2):
    try:
        socket.create_connection((host, port), timeout=timeout)
        return True
    except OSError:
        return False

def clean_text(t: str) -> str:
    if not t:
        return ""
    # basic cleanup
    t = re.sub(r'\s+', ' ', str(t)).strip()
    return t

import re

def excerpt(text: str, max_chars: int = 300, max_sentences: int = None) -> str:
    """
    Returns a cleaned excerpt from text.
    - If max_sentences is provided → return up to that many sentences.
    - Else fallback to character limit.
    """
    text = re.sub(r"\s+", " ", text).strip()

    if not text:
        return ""

    if max_sentences:
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return " ".join(sentences[:max_sentences])

    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0] + "..."


def file_mtime_iso(path: str) -> str:
    try:
        return datetime.utcfromtimestamp(os.path.getmtime(path)).isoformat() + "Z"
    except Exception:
        return ""

