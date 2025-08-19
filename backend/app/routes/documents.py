# backend/app/routes/documents.py
from fastapi import APIRouter, HTTPException, status
from app import config
import os
import urllib.parse

router = APIRouter()


@router.get("/documents")
def list_documents():
    """
    List all available documents in 'current' and 'historical' storage.
    Each entry includes an ID (the simple filename), display name, and URL.
    """
    docs = []
    base_url = "http://127.0.0.1:8000"

    # current
    if os.path.exists(config.DOCUMENTS_DIR):
        for filename in os.listdir(config.DOCUMENTS_DIR):
            if filename.lower().endswith(".pdf"):
                docs.append({
                    "id": filename,  # ✅ matches embeddings' source_file
                    "name": filename,
                    "url": f"{base_url}/static/documents/{urllib.parse.quote(filename)}"
                })

    # historical
    if os.path.exists(config.HISTORICAL_DIR):
        for filename in os.listdir(config.HISTORICAL_DIR):
            if filename.lower().endswith(".pdf"):
                docs.append({
                    "id": filename,  # ✅ same convention
                    "name": filename,
                    "url": f"{base_url}/static/historical/{urllib.parse.quote(filename)}"
                })

    return {"documents": docs}


@router.delete("/documents/{filename}")
def delete_document(filename: str):
    """
    Delete a document (PDF + structure + embeddings) from storage and output directories.
    The `filename` must match what /documents returns.
    """
    decoded_filename = urllib.parse.unquote(filename)

    # Locate storage dir
    if os.path.exists(os.path.join(config.DOCUMENTS_DIR, decoded_filename)):
        storage_dir = config.DOCUMENTS_DIR
    elif os.path.exists(os.path.join(config.HISTORICAL_DIR, decoded_filename)):
        storage_dir = config.HISTORICAL_DIR
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document not found: {decoded_filename}"
        )

    base_filename, _ = os.path.splitext(decoded_filename)
    files_to_delete = [
        os.path.join(storage_dir, decoded_filename),  # PDF
        os.path.join(storage_dir, f"{base_filename}_structure.json"),
        os.path.join(storage_dir, f"{base_filename}_embeddings.json"),
        os.path.join(config.OUTPUT_DIR, f"{base_filename}_structure.json"),
        os.path.join(config.OUTPUT_DIR, f"{base_filename}_embeddings.json"),
    ]

    deleted_count = 0
    errors = []

    for file_path in files_to_delete:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"[INFO] Deleted: {file_path}")
                deleted_count += 1
        except Exception as e:
            msg = f"Failed to delete {file_path}: {e}"
            print(f"[ERROR] {msg}")
            errors.append(msg)

    if deleted_count == 0 and errors:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No files found for: {decoded_filename}"
        )

    if errors:
        return {
            "status": "partial_success",
            "message": f"Deleted {deleted_count} files, but some errors occurred.",
            "errors": errors
        }

    return {
        "status": "ok",
        "message": f"Successfully deleted '{decoded_filename}' and associated files."
    }
