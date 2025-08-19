# backend/app/routes/ingest.py
from fastapi import APIRouter, File, UploadFile, Form
from app import config
import os
import shutil
import json
from datetime import datetime
from typing import List, Dict, Any, Union
from app.services.pdf_parser_service import parse_pdf
from app.services.embed_service import embed_text
from engines.round1a.processor import extract_document_structure

router = APIRouter()

def normalize_sections(parsed_structure: Dict[str, Any], pdf_path: str) -> List[Dict[str, Any]]:
    sections = []

    if parsed_structure.get("sections"):
        for sec in parsed_structure["sections"]:
            text = sec.get("text", "").strip()
            if text:
                sections.append({
                    "text": text,
                    "page_number": sec.get("page_number"),
                    "excerpt": sec.get("excerpt", text[:200]),
                    "document": parsed_structure.get("title") or os.path.basename(pdf_path)
                })

    if not sections:
        combined_text = parsed_structure.get("text", "")
        if not combined_text and parsed_structure.get("outline"):
            combined_text = " ".join([h.get("text","") for h in parsed_structure["outline"]])
        if combined_text.strip():
            sections.append({
                "text": combined_text.strip(),
                "page_number": 1,
                "excerpt": combined_text.strip()[:200],
                "document": parsed_structure.get("title") or os.path.basename(pdf_path)
            })

    return sections

def save_embedding_index(section_list: List[Dict[str, Any]], save_path: str, document_info: Dict[str, Any]):
    index_data = []
    doc_name = document_info.get("title", os.path.splitext(os.path.basename(save_path))[0].replace('_embeddings',''))
    file_mtime = document_info.get("file_mtime", datetime.utcnow().timestamp())

    for section in section_list:
        text = section.get("text", "").strip()
        if not text:
            continue
        vec = embed_text(text)
        if vec is None or (hasattr(vec, "size") and vec.size == 0):
            print(f"[WARN] Empty vector for text section: {text[:50]}... Skipping.")
            continue

        index_data.append({
            "text": text,
            "vector": vec.tolist(),
            "document": section.get("document", doc_name),
            "page_number": section.get("page_number"),
            "excerpt": section.get("excerpt", text[:200]),
            "file_mtime": file_mtime
        })

    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)

    print(f"[INFO] Saved {len(index_data)} embeddings → {save_path}")

@router.post("/ingest")
async def ingest(
    files: List[UploadFile] = File(...),
    kind: str = Form("current")  # "current" → single file, "historical" → multiple files
):
    is_historical = kind.lower() == "historical"
    target_dir = config.HISTORICAL_DIR if is_historical else config.DOCUMENTS_DIR
    target_dir = os.path.normpath(target_dir)
    os.makedirs(target_dir, exist_ok=True)
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)

    # Historical → all files, Current → only one file
    upload_files = files if is_historical else files[:1]

    responses = []

    for file in upload_files:
        # Ensure valid filename
        filename = os.path.basename(file.filename) or f"upload_{datetime.utcnow().timestamp()}.pdf"
        pdf_path = os.path.join(target_dir, filename)

        file.file.seek(0)
        with open(pdf_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)


        try:
            parsed_structure = parse_pdf(pdf_path)
            outline_data = extract_document_structure(pdf_path)
            parsed_structure["outline"] = outline_data.get("outline", [])
            parsed_structure["title"] = outline_data.get("title", os.path.splitext(file.filename)[0])
            parsed_structure["file_mtime"] = os.path.getmtime(pdf_path)

            parsed_structure["sections"] = normalize_sections(parsed_structure, pdf_path)
            parsed_structure["uploaded_at"] = datetime.utcnow().isoformat()
            parsed_structure["source_pdf"] = pdf_path

        except Exception as e:
            responses.append({
                "status": "error",
                "filename": file.filename,
                "message": f"Failed to parse PDF: {e}"
            })
            continue

        # Save structure JSON
        structure_filename = f"{os.path.splitext(file.filename)[0]}_structure.json"
        structure_path = os.path.join(target_dir, structure_filename)
        with open(structure_path, "w", encoding="utf-8") as f:
            json.dump(parsed_structure, f, ensure_ascii=False, indent=2)

        output_structure_path = os.path.join(config.OUTPUT_DIR, structure_filename)
        shutil.copyfile(structure_path, output_structure_path)

        # Save embeddings JSON
        embeddings_filename = f"{os.path.splitext(file.filename)[0]}_embeddings.json"
        embeddings_path = os.path.join(target_dir, embeddings_filename)
        save_embedding_index(
            parsed_structure.get("sections", []),
            embeddings_path,
            document_info={
                "title": parsed_structure.get("title"),
                "file_mtime": parsed_structure.get("file_mtime")
            }
        )

        output_embeddings_path = os.path.join(config.OUTPUT_DIR, embeddings_filename)
        shutil.copyfile(embeddings_path, output_embeddings_path)

        responses.append({
            "status": "ok",
            "filename": file.filename,
            "storage_dir": target_dir,
            "structure_path": structure_path,
            "output_structure_path": output_structure_path,
            "embeddings_path": embeddings_path,
            "output_embeddings_path": output_embeddings_path
        })

    return responses

