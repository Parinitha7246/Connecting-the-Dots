import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { DocMeta, Snippet } from "../api/types";

type State = {
  onlineMode: boolean;
  docs: DocMeta[];
  currentDoc?: DocMeta;
  selectedText: string;
  snippets: Snippet[];
  loadingSnippets: boolean;
  insights: string[];
  didYouKnow?: string;
  contradiction?: string;
  connections: string[];
  audioUrl?: string;
  navigationTarget: Snippet | null;
  themes: string[];
  selectedSnippetId: string | null;
  latestCurrentDocId: string | null;
  examples: string[];
};

type Actions = {
  setOnline: (v: boolean) => void;
  setDocs: (d: DocMeta[]) => void;
  setCurrentDoc: (d?: DocMeta) => void;
  setSelectedText: (t: string) => void;
  setSnippets: (s: Snippet[]) => void;
  setLoadingSnippets: (v: boolean) => void;
  setInsightsPack: (p: Partial<State>) => void;
  setAudioUrl: (u?: string) => void;
  resetRightPanel: () => void;
  navigateToSnippet: (targetSnippet: Snippet) => void;
  clearNavigationTarget: () => void;
  setSelectedSnippetId: (id: string | null) => void;
  setLatestCurrentDocId: (id: string | null) => void;
  removeDocument: (docId: string) => void;
};

export const useAppStore = create<State & Actions>()(
  persist(
    (set, get) => ({
      // --- State ---
      onlineMode: true,
      docs: [],
      currentDoc: undefined,
      selectedText: "",
      snippets: [],
      loadingSnippets: false,
      insights: [],
      didYouKnow: undefined,
      contradiction: undefined,
      connections: [],
      audioUrl: undefined,
      navigationTarget: null,
      themes: [],
      selectedSnippetId: null,
      latestCurrentDocId: null,
      examples: [],

      // --- Actions ---
      setOnline: (v) => set({ onlineMode: v }),
      setDocs: (d) => set({ docs: d }),
      setCurrentDoc: (d) => set({ currentDoc: d }),
      setSelectedText: (t) => set({ selectedText: t }),
      setSnippets: (s) => set({ snippets: s }),
      setLoadingSnippets: (v) => set({ loadingSnippets: v }),
      setInsightsPack: (p) => set(p),
      setAudioUrl: (u) => set({ audioUrl: u }),

      resetRightPanel: () =>
        set({
          themes: [],
          snippets: [],
          insights: [],
          didYouKnow: "",
          contradiction: "",
          connections: [],
          examples: [],
          audioUrl: undefined,
          selectedSnippetId: null,
        }),

      // --- Jump-to-snippet logic with logging ---
      navigateToSnippet: (targetSnippet) => {
        console.log("--- JUMP PROCESS STEP 2: STORE ACTION RECEIVED ---");
        console.log("Target Snippet's doc_id:", targetSnippet.doc_id);

        const { docs, currentDoc } = get();
        console.log("Current document in viewer:", currentDoc?.id);

        if (targetSnippet.doc_id !== currentDoc?.id) {
          console.log("Decision: Need to switch documents.");

          const docToSwitchTo = docs.find((d) => d.id === targetSnippet.doc_id);

          if (docToSwitchTo) {
            console.log("SUCCESS: Found matching document in the store:", docToSwitchTo);
            set({ currentDoc: docToSwitchTo, navigationTarget: targetSnippet });
          } else {
            console.error("FAILURE: Could not find a document with ID:", targetSnippet.doc_id);
            console.log("Available document IDs in store are:", docs.map((d) => d.id));
          }
        } else {
          console.log("Decision: Document is already open. Setting navigation target.");
          set({ navigationTarget: targetSnippet });
        }
      },

      clearNavigationTarget: () => set({ navigationTarget: null }),
      setSelectedSnippetId: (id) => set({ selectedSnippetId: id }),
      setLatestCurrentDocId: (id) => set({ latestCurrentDocId: id }),

      removeDocument: (docId) => {
        const { docs, currentDoc, latestCurrentDocId } = get();
        const newDocs = docs.filter((doc) => doc.id !== docId);

        if (docId === latestCurrentDocId) set({ latestCurrentDocId: null });

        if (currentDoc?.id === docId) {
          set({
            docs: newDocs,
            currentDoc: newDocs.length > 0 ? newDocs[0] : undefined,
          });
        } else {
          set({ docs: newDocs });
        }
      },
    }),
    {
      name: "docuwise-app-storage",
      partialize: (state) => ({
        onlineMode: state.onlineMode,
        latestCurrentDocId: state.latestCurrentDocId,
      }),
    }
  )
);
