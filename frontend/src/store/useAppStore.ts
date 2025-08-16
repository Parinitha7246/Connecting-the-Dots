import { create } from "zustand";
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
};

export const useAppStore = create<State & Actions>((set, get) => ({
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
  
  setOnline: (v) => set({ onlineMode: v }),
  setDocs: (d) => set({ docs: d }),
  setCurrentDoc: (d) => set({ currentDoc: d }),
  setSelectedText: (t) => set({ selectedText: t }),
  setSnippets: (s) => set({ snippets: s }),
  setLoadingSnippets: (v) => set({ loadingSnippets: v }),
  setInsightsPack: (p) => set(p),
  setAudioUrl: (u) => set({ audioUrl: u }),
  resetRightPanel: () => set({ themes: [], snippets: [], insights: [], didYouKnow: "", contradiction: "", connections: [], audioUrl: undefined, selectedSnippetId: null }),
  
  navigateToSnippet: (targetSnippet) => {
    const { docs, currentDoc } = get();
    if (targetSnippet.doc_id !== currentDoc?.id) {
      const docToSwitchTo = docs.find(d => d.id === targetSnippet.doc_id);
      if (docToSwitchTo) {
        set({ currentDoc: docToSwitchTo, navigationTarget: targetSnippet });
      }
    } else {
      set({ navigationTarget: targetSnippet });
    }
  },

  clearNavigationTarget: () => set({ navigationTarget: null }),
  setSelectedSnippetId: (id) => set({ selectedSnippetId: id }),
}));