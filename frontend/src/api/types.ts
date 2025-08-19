// Blueprint for a single snippet object from the backend
export type Snippet = {
  document: string;
  page_number?: number;
  excerpt: string;
  snippet: string;
  text: string;
  score: number;
  doc_id: string; 
  doc_name: string;
  // --- THIS IS THE FIX ---
  // We are adding "supporting" as a valid, expected value for relation_type.
  relation_type?: "overlap" | "example" | "contradiction" | "related" | "supporting";
};

// Blueprint for a single document object
export type DocMeta = { id: string; name: string; url: string; pages?: number };

// Blueprint for the full response from the /recommend endpoint
export type HybridResponse = {
  source: string;
  recommendations: Snippet[];
  online?: string | {
    themes?: string[]; 
    insights?: string[];
    did_you_know?: string;
    contradictions?: string;
    connections?: string[];
    examples?: string[];
  };
  online_error?: string;
};

// Blueprint for the response from the /insights endpoint
export type InsightsResponse = {
  source: string;
  parsed: {
    themes?: string[]; 
    insights?: string[];
    did_you_know?: string;
    contradictions?: string;
    connections?: string[];
    examples?: string[];
  };
  raw?: string;
};

// Blueprint for the response from the /podcast endpoint
export type PodcastResponse = {
  script: string;
  tts?: { url?: string; audio_path?: string };
};