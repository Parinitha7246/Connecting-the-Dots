from fastapi import APIRouter
from app import config
import os, json

router = APIRouter()

@router.get("/documents")
def list_documents():
    docs = []
    for folder in [config.DOCUMENTS_DIR, config.HISTORICAL_DIR]:
        for f in os.listdir(folder):
            if f.lower().endswith(".pdf"):
                docs.append({"filename": f, "path": os.path.join(folder, f)})
    # list generated structure files too
    structures = [f for f in os.listdir(config.OUTPUT_DIR) if f.endswith("_structure.json")]
    return {"documents": docs, "structures": structures}
