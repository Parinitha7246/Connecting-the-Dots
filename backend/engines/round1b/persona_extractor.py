#!/usr/bin/env python3
"""
Universal Offline PersonaExtractor (Hybrid-Balanced Version)
- Fully offline, works for ANY PDFs and ANY persona/job
- Dynamically extracts important keywords from persona & job
- Uses hybrid ranking: relevance priority + balanced PDF mix
- Writes ONLY to output/output.json
"""

import os
import re
import json
import fitz  # PyMuPDF
import numpy as np
from datetime import datetime
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Ensure NLTK data is downloaded
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

# =============================
# CONFIGURATION
# =============================
INPUT_DIR = "input/docs"
OUTPUT_FILE = "output/output.json"
TOP_SECTIONS_COUNT = 5
MIN_CHUNK_LEN = 100
MAX_CHUNK_LEN = 2000

STOPWORDS = set(stopwords.words('english'))

# =============================
# HELPER FUNCTIONS
# =============================
def extract_keywords(text: str) -> List[str]:
    """Extract meaningful keywords from persona and job text."""
    words = word_tokenize(text.lower())
    return list(set([w for w in words if w.isalpha() and w not in STOPWORDS]))

def clean_text(text: str) -> str:
    """Clean and normalize text."""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s\-.,;:!?()\[\]{}\'\"/@#$%&*+=<>|\\~`]', '', text)
    return text.strip()

def chunk_text(text: str, min_len=MIN_CHUNK_LEN, max_len=MAX_CHUNK_LEN) -> List[str]:
    """Split text into chunks of reasonable size."""
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) > max_len:
            if len(current_chunk) >= min_len:
                chunks.append(current_chunk.strip())
            current_chunk = sentence
        else:
            current_chunk += " " + sentence
    if len(current_chunk.strip()) >= min_len:
        chunks.append(current_chunk.strip())
    return chunks

# =============================
# PDF PROCESSOR
# =============================
def detect_page_heading(doc, page_num: int) -> str:
    """
    Detect most likely heading for a page using font sizes and position.
    """
    page = doc[page_num]
    blocks = page.get_text("dict")["blocks"]
    largest_font = 0
    candidate = None

    for b in blocks:
        if "lines" in b:
            for l in b["lines"]:
                for s in l["spans"]:
                    txt = s["text"].strip()
                    if not txt:
                        continue
                    if txt.endswith(('.', '!', '?')):
                        continue
                    if len(txt.split()) > 12:
                        continue
                    if s["size"] > largest_font and l["bbox"][1] < 200:
                        largest_font = s["size"]
                        candidate = txt

    if candidate:
        return candidate

    # Fallback: first short line
    text_lines = [l.strip() for l in page.get_text().split("\n") if l.strip()]
    for line in text_lines:
        if 2 <= len(line.split()) <= 12 and not line.endswith(('.', '!', '?')):
            return line

    return "Untitled Section"

def extract_chunks_from_pdf(pdf_path: str) -> List[Dict[str, Any]]:
    chunks = []
    filename = os.path.basename(pdf_path)
    try:
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            text = doc[page_num].get_text()
            text = clean_text(text)
            if not text:
                continue

            page_heading = detect_page_heading(doc, page_num)
            page_chunks = chunk_text(text)
            for ch in page_chunks:
                chunks.append({
                    "document": filename,
                    "page_number": page_num + 1,
                    "title": page_heading,
                    "content": ch
                })
        doc.close()
    except Exception as e:
        print(f"⚠️ Error reading {pdf_path}: {e}")
    return chunks

# =============================
# RANKING
# =============================
def rank_chunks(chunks: List[Dict[str, Any]], persona: str, job: str, model) -> List[Dict[str, Any]]:
    """Rank chunks based on semantic similarity + keyword match."""
    reference_text = f"Persona: {persona}. Task: {job}"
    reference_embedding = model.encode(reference_text, convert_to_tensor=False)
    boost_keywords = extract_keywords(persona + " " + job)

    ranked = []
    for chunk in chunks:
        emb = model.encode(chunk["content"], convert_to_tensor=False)
        sim_score = float(np.dot(reference_embedding, emb) /
                          (np.linalg.norm(reference_embedding) * np.linalg.norm(emb)))
        keyword_boost = sum(1 for kw in boost_keywords if kw in chunk["content"].lower())
        final_score = sim_score + (0.02 * keyword_boost)
        chunk["relevance_score"] = final_score
        ranked.append(chunk)

    ranked.sort(key=lambda x: x["relevance_score"], reverse=True)
    return ranked

# =============================
# HYBRID SELECTION
# =============================
def select_hybrid_top_chunks(ranked_chunks: List[Dict[str, Any]], top_n: int) -> List[Dict[str, Any]]:
    """
    Select top N chunks prioritizing relevance but ensuring diversity.
    No single PDF can take more than 50% of slots unless there are fewer PDFs.
    """
    selected = []
    used_docs_count = {}
    max_per_doc = max(1, top_n // 2)  # allow max 50% from one doc

    for chunk in ranked_chunks:
        doc = chunk["document"]
        if used_docs_count.get(doc, 0) < max_per_doc:
            selected.append(chunk)
            used_docs_count[doc] = used_docs_count.get(doc, 0) + 1
        if len(selected) >= top_n:
            break

    # If still not enough, fill with remaining highest-ranked chunks regardless of doc
    if len(selected) < top_n:
        for chunk in ranked_chunks:
            if chunk not in selected:
                selected.append(chunk)
                if len(selected) >= top_n:
                    break

    return selected


# =============================
# REFINEMENT
# =============================
def refine_chunk_text(content: str) -> str:
    """Short, relevant summary for the chunk."""
    sentences = re.split(r'(?<=[.!?]) +', content)
    return " ".join(sentences[:3]).strip()

# =============================
# MAIN PIPELINE
# =============================
def process_pdfs(persona: str, job: str) -> None:
    print("\n🔍 Loading local embedding model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')

    pdf_files = [os.path.join(INPUT_DIR, f) for f in os.listdir(INPUT_DIR) if f.lower().endswith(".pdf")]
    print(f"📄 Found {len(pdf_files)} PDFs in {INPUT_DIR}")

    all_chunks = []
    for pdf in pdf_files:
        all_chunks.extend(extract_chunks_from_pdf(pdf))

    if not all_chunks:
        raise ValueError("❌ No content extracted from PDFs.")

    ranked_chunks = rank_chunks(all_chunks, persona, job, model)
    top_chunks = select_hybrid_top_chunks(ranked_chunks, TOP_SECTIONS_COUNT)

    extracted_sections = []
    subsection_analysis = []

    for i, ch in enumerate(top_chunks, 1):
        extracted_sections.append({
            "document": ch["document"],
            "section_title": ch["title"],
            "importance_rank": i,
            "page_number": ch["page_number"]
        })
        subsection_analysis.append({
            "document": ch["document"],
            "refined_text": refine_chunk_text(ch["content"]),
            "page_number": ch["page_number"]
        })

    result = {
        "metadata": {
            "input_documents": [os.path.basename(p) for p in pdf_files],
            "persona": persona,
            "job_to_be_done": job,
            "processing_timestamp": datetime.now().isoformat()
        },
        "extracted_sections": extracted_sections,
        "subsection_analysis": subsection_analysis
    }

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"✅ Extraction complete. Output written to {OUTPUT_FILE}")

# =============================
# ENTRY POINT
# =============================
if __name__ == "__main__":
    print("=== Offline PersonaExtractor (Hybrid-Balanced) ===\n")
    persona = input("Enter persona: ").strip()
    job = input("Enter job to be done: ").strip()
    process_pdfs(persona, job)
