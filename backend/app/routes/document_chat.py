# backend/app/routes/doc_chat.py
from fastapi import APIRouter
from pydantic import BaseModel
from app import config
from app.services.llm_service import LLMService, LLMError
from app.services.embed_service import embed_text, embed_search_in_dir
import numpy as np

router = APIRouter()

class DocChatReq(BaseModel):
    message: str
    top_k: int = 5

@router.post("/doc-chat")
async def doc_chat(req: DocChatReq):
    message = req.message.strip()
    top_k = req.top_k

    if not message:
        return {"response": "Empty query", "mode": "error"}

    # --- Load relevant sections from documents + historical ---
    try:
        docs_sections = []
        for dir_path in [config.DOCUMENTS_DIR, config.HISTORICAL_DIR]:
            query_vec = embed_text(message)
            if query_vec.size == 0:
                continue
            top_sections = embed_search_in_dir(query_vec, dir_path, top_k=top_k)
            docs_sections.extend(top_sections)
    except Exception as e:
        return {"response": "Failed to search documents", "error": str(e), "mode": "error"}

    if not docs_sections:
        # fallback: no document context
        return {"response": "Out of context", "mode": "online"}

    # --- Prepare context for LLM ---
    # Soft threshold: include top-k matches regardless of score
    context_snippets = []
    for s in docs_sections[:top_k]:
        text = s.get("text") or s.get("excerpt") or ""
        score = s.get("score", 0)
        context_snippets.append(f"- {text.strip()} (score: {score:.2f})")

    context_str = "\n".join(context_snippets)

    # --- Structured prompt for Gemini ---
    prompt = f"""
You are a document-grounded AI assistant. Only answer based on the provided context.
Do NOT hallucinate or provide information outside of it.  

Context:
{context_str}

User question:
{message}

Instructions:
- Give a concise answer strictly based on the context.
- If the context does not contain relevant information, respond: "I could not find information in the documents."
- Include a short reference to which excerpts were used.
"""

    # --- Generate answer via Gemini ---
    try:
        llm = LLMService()
        answer = llm.generate(prompt, max_tokens=400, temperature=0.2)
    except LLMError as e:
        return {"response": "Failed to get LLM response", "error": str(e), "mode": "online_error"}
    except Exception as e:
        return {"response": "Failed to get LLM response", "error": str(e), "mode": "online_error"}

    # --- Return structured response ---
    return {
        "response": answer.strip(),
        "context_used": context_snippets,
        "mode": "online",
        "query": message
    }
