export type DocMeta = { id: string; name: string; url: string; pages?: number };

export type Snippet = {
  doc_id: string;
  doc_name: string;
  page_number?: number;
  text: string;
  score?: number;
  location?: { x?: number; y?: number }; // optional pointer
};

export type RecommendResponse = {
  recommendations: Snippet[];
};

export type InsightsResponse = {
  parsed: {
    // --- MODIFICATION: Added 'themes' to the expected response ---
    themes?: string[]; 
    insights: string[];
    did_you_know: string;
    contradictions: string;
    connections: string[];
  };
  raw: string;
};

export type PodcastResponse = {
  script: string;
  tts?: { url?: string; saved_path?: string };
};