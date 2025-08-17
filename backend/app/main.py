from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import ingest, recommend, documents, insights, podcast,recommend_selection,document_chat

app = FastAPI(title="PersonaExtractor Hybrid Backend", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(ingest.router, prefix="", tags=["Ingest"])
app.include_router(recommend.router, prefix="", tags=["Recommend"])
app.include_router(documents.router, prefix="", tags=["Documents"])
app.include_router(insights.router, prefix="", tags=["Insights"])
app.include_router(document_chat.router,prefix="",tags=["ai chat"])
app.include_router(podcast.router, prefix="", tags=["Podcast"])
app.include_router(recommend_selection.router, prefix="", tags=["Recommend Selection"])

@app.get("/")
def root():
    return {
        "message": "PersonaExtractor Hybrid Backend is running",
        "status": "ok",
        "docs_url": "/docs"
    }

