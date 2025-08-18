// This file reads the variable from your .env file.
// It MUST be named VITE_BACKEND_URL in your .env file.
export const BACKEND_URL = import.meta.env.VITE_BACKEND_URL as string;

// The rest of the config...
export const ADOBE_CLIENT_ID = import.meta.env.VITE_ADOBE_EMBED_API_KEY as string;
export const MAX_SNIPPETS = 5;
export const DEFAULT_PERSONA = "General researcher";
export const DEFAULT_TASK = "Understand and compare the selected concept across documents";