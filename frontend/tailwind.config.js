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
          light: '#a7f3d0',   // Emerald-200 (lighter background)
          dark: '#065f46',    // Emerald-800 (contrast text)
        },
        surface: {
          DEFAULT: '#ffffff', // Pure white for cards
          ground: '#f8fafc',  // Slate 50 - The main background
          inset: '#f1f5f9',   // Slate 100 - For inset elements
        },
        content: {
          DEFAULT: '#334155', // Slate 700 - Main text
          subtle: '#64748b',  // Slate 500 - Subtitles and muted text
        },

        // --- NEW RELATION HIGHLIGHT COLORS ---
        relation: {
          overlap: {
            light: '#dbeafe', // blue-100
            dark: '#3b82f6',  // blue-500
          },
          example: {
            light: '#d1fae5', // green-100
            dark: '#10b981',  // green-500
          },
          contradiction: {
            light: '#fee2e2', // red-100
            dark: '#ef4444',  // red-500
          },
        },
      },
    },
  },
  plugins: [],
};
