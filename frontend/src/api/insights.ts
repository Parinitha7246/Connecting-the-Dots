import { api } from "./client";
import type { HybridResponse, InsightsResponse } from "./types";

/**
 * Fetches both snippets and insights from the backend in a single call to /recommend.
 */
export async function getRecommendations(
  selectedText: string, 
  top_k: number, 
  online: boolean 
): Promise<HybridResponse> {
  
  const payload = {
    selected_text: selectedText,
    top_k: top_k,
    online: online,
  };
  const { data } = await api.post<HybridResponse>("/recommend", payload);
  return data;
}

/**
 * Fetches AI-generated insights based on a list of text sections.
 * This is used ONLY as a fallback by the chat function.
 */
export async function getInsights(
  section_texts: string[], 
  persona: string = "General Researcher", 
  task: string = "Find connections and insights"
): Promise<InsightsResponse> {
  const payload = { 
    texts: section_texts, 
    persona: persona, 
    task: task,
  };
  const { data } = await api.post<InsightsResponse>("/insights", payload);
  return data;
}

/**
 * Sends a message to the chat endpoint with context.
 */
export async function chat(message: string, context: string[]) {
  try {
    const { data } = await api.post("/chat", { message, context });
    return { text: data?.text ?? "Sorry, I couldn't process that." };
  } catch (error) {
    console.error("Chat endpoint failed, falling back to insights:", error);
    const i = await getInsights(context, "Chat user", message);
    const text = i?.parsed?.insights?.join("\n• ") || i?.raw || "No response available.";
    return { text };
  }
}

/**
 * Sends a message to the document chat endpoint.
 * Used in the AI Chat tab.
 */
export async function docChat(message: string) {
  const payload = {
    message,
    top_k: 5, // configurable later
  };
  const { data } = await api.post("/doc-chat", payload);
  return data; // e.g. { response: "...", context_used: [...] }
}
