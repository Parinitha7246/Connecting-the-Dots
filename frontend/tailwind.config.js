/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#4f46e5', // Indigo 600
          hover: '#4338ca',   // Indigo 700
          light: '#eef2ff',  // Indigo 50
        },
        accent: {
          DEFAULT: '#10b981', // Emerald 500
          light: '#ecfdf5',  // Emerald 50
        },
        // --- UPDATED GRAY PALETTE ---
        surface: {
          DEFAULT: '#ffffff', // Pure white for cards
          ground: '#f8fafc',  // Slate 50 - The main background
          inset: '#f1f5f9',   // Slate 100 - For inset elements like chat bubbles
        },
        content: {
          DEFAULT: '#334155', // Slate 700 - Main text
          subtle: '#64748b',  // Slate 500 - Subtitles and muted text
        },
      },
    },
  },
  plugins: [],
};