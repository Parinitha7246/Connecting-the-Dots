# backend/app/services/pdf_parser_service.py
import fitz
import re
from app.utils import clean_text, excerpt

HEADING_PATTERN = re.compile(r"^(\d+(\.\d+)*)\s+|^(ABSTRACT|INTRODUCTION|CONCLUSION|REFERENCES)$", re.I)

def parse_pdf(pdf_path: str):
    """
    Parse PDF into structured sections.
    Skips cover/title pages, filters metadata, and builds clean sections with snippets.
    """
    doc = fitz.open(pdf_path)
    sections = []
    current = {"heading": None, "content": []}

    for page_num, page in enumerate(doc, start=1):
        text = page.get_text("text")
        lines = [clean_text(l) for l in text.split("\n") if l.strip()]

        # --- Heuristic: Skip likely cover/title pages ---
        if page_num <= 2:  # check first 2 pages
            # many ALLCAPS or "submitted by" → skip
            caps_ratio = sum(1 for l in lines if l.isupper()) / max(1, len(lines))
            if caps_ratio > 0.4 or any("submitted by" in l.lower() or "college" in l.lower() for l in lines):
                continue

        for line in lines:
            if not line or any(x in line.lower() for x in ["submitted by", "guided by", "roll no", "college", "address"]):
                continue  # skip metadata

            # --- Detect new heading ---
            if HEADING_PATTERN.match(line):
                # save old section if any
                if current["heading"] and current["content"]:
                    text_block = " ".join(current["content"])
                    sections.append({
                        "heading": current["heading"],
                        "page_number": page_num,
                        "text": text_block,
                        "snippet": excerpt(text_block, max_sentences=3)
                    })
                # start new
                current = {"heading": line, "content": []}
            else:
                current["content"].append(line)

    # flush last
    if current["heading"] and current["content"]:
        text_block = " ".join(current["content"])
        sections.append({
            "heading": current["heading"],
            "page_number": page_num,
            "text": text_block,
            "snippet": excerpt(text_block, max_sentences=3)
        })

    return {"title": doc.metadata.get("title") or "Untitled", "outline": sections}
