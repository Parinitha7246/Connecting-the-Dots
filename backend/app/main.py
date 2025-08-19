from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes import ingest, recommend, documents, insights, podcast, recommend_selection, document_chat
from app import config
import os

app = FastAPI(title="PersonaExtractor Hybrid Backend", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Ensure directories exist ---
os.makedirs(config.DOCUMENTS_DIR, exist_ok=True)
os.makedirs(config.HISTORICAL_DIR, exist_ok=True)
os.makedirs(config.OUTPUT_DIR, exist_ok=True)  # Added so podcast/audio files are stored safely

# --- Static file serving ---
# Makes documents, historical archives, and generated podcasts accessible via URL
app.mount("/static/documents", StaticFiles(directory=config.DOCUMENTS_DIR), name="static_docs")
app.mount("/static/historical", StaticFiles(directory=config.HISTORICAL_DIR), name="static_hist")
app.mount("/static/output", StaticFiles(directory=config.OUTPUT_DIR), name="static_output")

# --- Routers ---
app.include_router(ingest.router, prefix="", tags=["Ingest"])
app.include_router(recommend.router, prefix="", tags=["Recommend"])
app.include_router(documents.router, prefix="", tags=["Documents"])
app.include_router(insights.router, prefix="", tags=["Insights"])
app.include_router(document_chat.router, prefix="", tags=["AI Chat"])
app.include_router(podcast.router, prefix="", tags=["Podcast"])
app.include_router(recommend_selection.router, prefix="", tags=["Recommend Selection"])

@app.get("/")
def root():
    return {
        "message": "PersonaExtractor Hybrid Backend is running",
        "status": "ok",
        "docs_url": "/docs"
    }
