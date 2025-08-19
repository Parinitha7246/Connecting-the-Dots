import { api } from "./client";
import type { PodcastResponse } from "./types";

/**
 * Sends a request to the backend to generate a podcast.
 * @param section_texts An array of strings (from the snippets) to be used as context.
 * @param persona The desired persona for the podcast.
 * @param task A description of the task for the podcast generation.
 */
export async function createPodcast(payload: {
  section_texts: string[];
  persona: string;
  task: string;
}): Promise<PodcastResponse> {
  // The payload here now perfectly matches the new Pydantic model in podcast.py
  const { data } = await api.post<PodcastResponse>("/podcast", payload);
  return data;
}