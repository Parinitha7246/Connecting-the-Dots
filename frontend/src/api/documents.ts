import { api } from "./client";
import type { DocMeta } from "./types";

/**
 * Fetches the list of all available documents from the backend.
 */
export async function listDocuments(): Promise<DocMeta[]> {
  const { data } = await api.get("/documents");
  return data?.documents ?? [];
}

/**
 * Uploads one or more documents to the backend in a single request.
 * @param files - An array of File objects to upload.
 * @param historical - A boolean flag indicating if the documents are historical.
 */
export async function ingestDocuments(files: File[], historical = false) {
  const form = new FormData();

  const kind = historical ? "historical" : "current";
  form.append("kind", kind);

  for (const file of files) {
    form.append("files", file);
  }
  
  // The API call is wrapped in a try/catch for robust error handling.
  try {
    const response = await api.post("/ingest", form, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response;
  } catch (error) {
    console.error("CRITICAL ERROR in ingestDocuments API call:", error);
    throw error;
  }
}

/**
 * Sends a request to the backend to delete a specific document.
 * @param docId - The ID of the document to delete (which is its filename).
 */
export async function deleteDocument(docId: string) {
  // We assume the backend expects the document ID in the URL, e.g., DELETE /documents/MyFile.pdf
  // The filename might contain spaces or special characters, so we must encode it.
  const encodedId = encodeURIComponent(docId);
  return api.delete(`/documents/${encodedId}`);
}