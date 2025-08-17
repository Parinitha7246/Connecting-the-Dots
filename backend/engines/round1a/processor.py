#!/usr/bin/env python3
"""
Improved Final Ground Truth Processor with Fallbacks
- Original Round-1A logic preserved
- Adds TOC and font-size based fallback so outline is never empty
"""

import os
import re
import json
import fitz
from collections import Counter

# =============================
# Utility Functions
# =============================

def clean_text(text):
    """Removes extra whitespace and non-printable characters."""
    return re.sub(r'\s+', ' ', str(text).strip())

def get_font_statistics(pdf_path):
    """Analyze PDF fonts to find common sizes."""
    doc = fitz.open(pdf_path)
    font_sizes = Counter()
    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    size = round(span["size"], 1)
                    font_sizes[size] += 1
    most_common_size = font_sizes.most_common(1)[0][0] if font_sizes else 0
    heading_sizes = [size for size, _ in font_sizes.most_common() if size > most_common_size]
    top_font_sizes = sorted(heading_sizes, reverse=True)[:3]
    while len(top_font_sizes) < 3:
        top_font_sizes.append(top_font_sizes[-1] if top_font_sizes else most_common_size)
    return {
        "body_text_size": most_common_size,
        "top_font_sizes": top_font_sizes
    }

# =============================
# Core Processing Classes
# =============================

class TextBlock:
    """A block of text with metadata."""
    def __init__(self, block, page_num):
        self.bbox = fitz.Rect(block['bbox'])
        self.page_num = page_num
        self.y0 = self.bbox.y0
        self.text = ""
        self.size = 0
        self.is_bold = False
        self.word_count = 0
        self.starts_with_list_marker = False

        lines = block.get('lines', [])
        if lines:
            span_texts = [s.get('text', '') for line in lines for s in line.get('spans', [])]
            self.text = clean_text(" ".join(span_texts))
            self.word_count = len(self.text.split())

            spans = lines[0].get('spans', [])
            if spans:
                self.size = round(spans[0]['size'])
                if "bold" in spans[0]['font'].lower() or "black" in spans[0]['font'].lower():
                    self.is_bold = True

        if self.text:
            self.starts_with_list_marker = bool(re.match(r'^\s*(\d+\.|[a-z][\.\)]|\([a-z]\)|•)\s', self.text, re.IGNORECASE))

def is_valid_report_heading(block, profile):
    """Filters headings in standard reports."""
    if block.size <= profile['body_size']:
        return False
    if block.starts_with_list_marker or block.text.endswith(':'):
        return False
    if block.word_count > 25:
        return False
    if not block.is_bold and block.size < profile['body_size'] + 2:
        return False
    return True

# =============================
# Document Structure Extraction
# =============================

def extract_document_structure(pdf_path):
    doc = fitz.open(pdf_path)
    if not doc.page_count:
        return {"title": "", "outline": []}

    # --- Pass 1: Extract features ---
    all_blocks = []
    list_marker_count = 0
    for page_num, page in enumerate(doc, start=1):
        for b in page.get_text("dict")['blocks']:
            if b['type'] == 0:
                block = TextBlock(b, page_num)
                if block.text:
                    all_blocks.append(block)
                    if block.starts_with_list_marker:
                        list_marker_count += 1

    if not all_blocks:
        return {"title": "", "outline": []}

    # --- Pass 2: Classify doc ---
    doc_type = 'REPORT'
    list_marker_ratio = list_marker_count / len(all_blocks)
    if list_marker_ratio > 0.15:
        doc_type = 'FORM'
    elif len(all_blocks) < 40:
        doc_type = 'FLYER'

    # --- Pass 3: Extract title & outline ---
    title = ""
    outline = []
    body_size_counter = Counter(b.size for b in all_blocks if b.word_count > 10)
    body_size = body_size_counter.most_common(1)[0][0] if body_size_counter else 10
    doc_profile = {'body_size': body_size}

    if doc_type == 'FORM':
        page1_top_blocks = [b for b in all_blocks if b.page_num == 1 and b.y0 < doc[0].rect.height * 0.2]
        title = max(page1_top_blocks, key=lambda b: b.size).text if page1_top_blocks else all_blocks[0].text

    elif doc_type == 'FLYER':
        max_size = max(b.size for b in all_blocks)
        main_headings = [b for b in all_blocks if b.size == max_size]
        outline = [{"level": "H1", "text": h.text, "page": h.page_num - 1} for h in main_headings]

    elif doc_type == 'REPORT':
        heading_candidates = [b for b in all_blocks if is_valid_report_heading(b, doc_profile)]
        page1_candidates = sorted([h for h in heading_candidates if h.page_num == 1], key=lambda h: h.y0)

        if page1_candidates:
            title_blocks = [page1_candidates[0]]
            last_y1 = page1_candidates[0].bbox.y1
            for i in range(1, len(page1_candidates)):
                if (page1_candidates[i].y0 - last_y1) < 20 and page1_candidates[i].size >= title_blocks[0].size - 2:
                    title_blocks.append(page1_candidates[i])
                    last_y1 = page1_candidates[i].bbox.y1
                else:
                    break
            title = " ".join(b.text for b in title_blocks)
            heading_candidates = [h for h in heading_candidates if h not in title_blocks]

        if heading_candidates:
            unique_sizes = sorted(list(set(h.size for h in heading_candidates)), reverse=True)
            size_to_level_map = {size: f"H{i+1}" for i, size in enumerate(unique_sizes)}
            for h in heading_candidates:
                if h.size in size_to_level_map:
                    outline.append({"level": size_to_level_map[h.size], "text": h.text, "page": h.page_num - 1})

    if outline:
        outline.sort(key=lambda x: (x['page'], [b.y0 for b in all_blocks if b.text == x['text']][0]))

    # =============================
    # Fallback 1: Use TOC if no outline
    # =============================
    if not outline:
        toc = doc.get_toc(simple=True)
        if toc:
            outline = [{"level": f"H{lvl}", "text": clean_text(t), "page": p - 1} for lvl, t, p in toc]

    # =============================
    # Fallback 2: Guess from font size if still empty
    # =============================
    if not outline:
        for b in all_blocks:
            if b.size > body_size + 1 and b.word_count <= 20:
                outline.append({
                    "level": "H2",
                    "text": b.text,
                    "page": b.page_num - 1
                })

    return {"title": clean_text(title), "outline": outline}

# =============================
# CLI Runner
# =============================

if __name__ == "__main__":
    input_dir = "/app/input"
    output_dir = "/app/output"
    os.makedirs(output_dir, exist_ok=True)

    print("📄 Running Improved 'Ground Truth' Engine...")

    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(input_dir, filename)
            print(f"   -> Processing {filename}")
            result = extract_document_structure(pdf_path)

            output_filename = filename.rsplit(".", 1)[0] + ".json"
            output_path = os.path.join(output_dir, output_filename)

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=4, ensure_ascii=False)

    print("✅ Analysis complete.")
