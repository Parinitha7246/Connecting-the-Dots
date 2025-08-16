import { api } from "./client";
import type { DocMeta, RecommendResponse } from "./types";

// GET list of uploaded docs (expects your backend route /documents)
export async function listDocuments(): Promise<DocMeta[]> {
  const { data } = await api.get("/documents");
  return data?.documents ?? [];
}

// POST /ingest: upload file
export async function ingestDocument(file: File, historical = false) {
  const form = new FormData();
  form.append("file", file);
  form.append("historical", String(historical));
  return api.post("/ingest", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
}

// POST recommend by selected text (preferred). If your friend only has /recommend,
// switch to that in this function.
export async function recommendBySelection(selectedText: string, top_k = 5, online = true) {
  // Preferred new route:
  try {
    const form = new FormData();
    form.append("selected_text", selectedText);
    form.append("top_k", String(top_k));
    form.append("online", String(online));
    const { data } = await api.post<RecommendResponse>("/recommend_by_selection", form);
    return data;
  } catch {
    // Fallback to legacy /recommend (Round 1B style) with dummy persona/task
    const form = new FormData();
    form.append("persona", "General");
    form.append("job", selectedText.slice(0, 120));
    form.append("top_k", String(top_k));
    const { data } = await api.post<RecommendResponse>("/recommend", form);
    return data;
  }
}

// GET a file URL by doc id if your backend supports it
export async function getDocUrl(docId: string): Promise<string | null> {
  try {
    const { data } = await api.get(`/documents/${docId}`);
    return data?.url ?? null;
  } catch {
    return null;
  }
}
