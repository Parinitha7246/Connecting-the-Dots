from fastapi import APIRouter, HTTPException, status
from app import config
import os
import urllib.parse

router = APIRouter()

@router.get("/documents")
def list_documents():
    docs = []
    base_url = "http://127.0.0.1:8000"

    # Process the "current" documents directory
    if os.path.exists(config.DOCUMENTS_DIR):
        for filename in os.listdir(config.DOCUMENTS_DIR):
            if filename.lower().endswith(".pdf"):
                docs.append({
                    "id": f"doc_{filename}",
                    "name": filename,
                    "url": f"{base_url}/static/documents/{urllib.parse.quote(filename)}"
                })
            
    # Process the "historical" documents directory
    if os.path.exists(config.HISTORICAL_DIR):
        for filename in os.listdir(config.HISTORICAL_DIR):
            if filename.lower().endswith(".pdf"):
                docs.append({
                    "id": f"hist_{filename}",
                    "name": filename,
                    "url": f"{base_url}/static/historical/{urllib.parse.quote(filename)}"
                })

    return {"documents": docs}


# --- THIS IS THE NEW DELETE ENDPOINT ---
@router.delete("/documents/{doc_id}")
def delete_document(doc_id: str):
    # The frontend sends an ID like "doc_MyFile.pdf" or "hist_MyFile.pdf".
    # We need to decode it and get the original filename.
    decoded_id = urllib.parse.unquote(doc_id)

    # Determine if it's a "current" or "historical" doc
    if decoded_id.startswith("doc_"):
        filename = decoded_id[4:]
        storage_dir = config.DOCUMENTS_DIR
    elif decoded_id.startswith("hist_"):
        filename = decoded_id[5:]
        storage_dir = config.HISTORICAL_DIR
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid document ID format.")

    # Define all the files that need to be deleted
    base_filename, _ = os.path.splitext(filename)
    files_to_delete = [
        os.path.join(storage_dir, filename), # The PDF itself
        os.path.join(storage_dir, f"{base_filename}_structure.json"),
        os.path.join(storage_dir, f"{base_filename}_embeddings.json"),
        os.path.join(config.OUTPUT_DIR, f"{base_filename}_structure.json"),
        os.path.join(config.OUTPUT_DIR, f"{base_filename}_embeddings.json"),
    ]

    deleted_count = 0
    errors = []

    # Loop through and delete each file, checking if it exists first
    for file_path in files_to_delete:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"[INFO] Deleted file: {file_path}")
                deleted_count += 1
        except Exception as e:
            error_message = f"Failed to delete {file_path}: {e}"
            print(f"[ERROR] {error_message}")
            errors.append(error_message)

    if deleted_count == 0 and errors:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No files found for document: {filename}")
    
    if errors:
        return {"status": "partial_success", "message": f"Deleted {deleted_count} files, but some errors occurred.", "errors": errors}

    return {"status": "ok", "message": f"Successfully deleted document '{filename}' and associated files."}