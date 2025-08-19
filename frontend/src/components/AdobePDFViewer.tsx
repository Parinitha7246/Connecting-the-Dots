/* global AdobeDC */
import { useEffect, useRef } from "react";
import { ADOBE_CLIENT_ID } from "../config";
import { useAppStore } from "../store/useAppStore";
import { getRecommendations, getInsights } from "../api/insights"; // <-- We need both functions
import { MAX_SNIPPETS } from "../config";
import type { Snippet } from "../api/types";

declare global {
  interface Window { 
    AdobeDC: any;
    adobeViewerAPIs?: any;
  }
}

export default function AdobePDFViewer() {
  const containerRef = useRef<HTMLDivElement>(null);
  const { 
    currentDoc, setSelectedText, setSnippets, setLoadingSnippets,
    onlineMode, setInsightsPack, resetRightPanel,
    navigationTarget, clearNavigationTarget
  } = useAppStore();

  const onlineModeRef = useRef(onlineMode);
  useEffect(() => {
    onlineModeRef.current = onlineMode;
  }, [onlineMode]);

  useEffect(() => {
    if (!currentDoc || !currentDoc.url || !containerRef.current || !window.AdobeDC) {
      return;
    }

    resetRightPanel();
    const adobeDCView = new window.AdobeDC.View({ clientId: ADOBE_CLIENT_ID, divId: "adobe-dc-view" });

    adobeDCView.previewFile({
      content: { location: { url: currentDoc.url } },
      metaData: { fileName: currentDoc.name },
    }, { 
      embedMode: "SIZED_CONTAINER", 
      showDownloadPDF: true,
      showPrintPDF: true
    })
    .then((adobeViewer: any) => adobeViewer.getAPIs())
    .then((apis: any) => {
      window.adobeViewerAPIs = apis;
      
      adobeDCView.registerCallback(
        window.AdobeDC.View.Enum.CallbackType.EVENT_LISTENER,
        async (selectionEvent: any) => {
          if (selectionEvent.type === window.AdobeDC.View.Enum.FilePreviewEvents.PREVIEW_SELECTION_END) {
            try {
              const result = await apis.getSelectedContent();
              const text = (result?.data || "").trim();
              if (!text) return;

              setSelectedText(text);
              setLoadingSnippets(true);
              
              // --- STEP 1: Get Snippets ---
              const rec = await getRecommendations(text, MAX_SNIPPETS, onlineModeRef.current);
              
              let snippets = rec?.recommendations ?? [];
              snippets = snippets.map((s: Snippet) => ({ ...s, doc_name: s.document, doc_id: s.document }));
              setSnippets(snippets);

              // --- THIS IS THE FIX ---
              // STEP 2: If in online mode, use those snippets to get insights.
              // This block of code was missing and has now been restored.
              if (onlineModeRef.current && snippets.length > 0) {
                const snippetTexts = snippets.map((s: Snippet) => s.snippet || s.text);
                const ins = await getInsights(snippetTexts); // Call the separate /insights endpoint
                
                setInsightsPack({
                    themes: ins?.parsed?.themes || [],
                    insights: ins?.parsed?.insights || [],
                    didYouKnow: ins?.parsed?.did_you_know || "",
                    contradiction: ins?.parsed?.contradictions || "",
                    connections: ins?.parsed?.connections || [],
                    examples: ins?.parsed?.examples || [],
                });
              } else {
                // If offline, ensure the insights panel is cleared.
                setInsightsPack({ themes: [], insights: [], didYouKnow: "", contradiction: "", connections: [], examples: [] });
              }

            } catch (e) {
              console.error("Error processing text selection:", e);
              // Clear panels on error to ensure no stale data is shown
              setSnippets([]);
              setInsightsPack({ themes: [], insights: [], didYouKnow: "", contradiction: "", connections: [], examples: [] });
            } finally {
              setLoadingSnippets(false);
            }
          }
        },
        { enableFilePreviewEvents: true, listenOn: [window.AdobeDC.View.Enum.FilePreviewEvents.PREVIEW_SELECTION_END] }
      );

      if (navigationTarget && navigationTarget.doc_id === currentDoc.id) {
        apis.gotoLocation(navigationTarget.page_number || 1, 0, 0);
        clearNavigationTarget();
      }
    })
    .catch((error: any) => console.error("Fatal error initializing Adobe Viewer:", error));

    return () => {
      window.adobeViewerAPIs = null;
      if (containerRef.current) containerRef.current.innerHTML = "";
    };
  }, [currentDoc, resetRightPanel, setSelectedText, setSnippets, setLoadingSnippets, setInsightsPack, navigationTarget, clearNavigationTarget]);

  useEffect(() => {
    if (navigationTarget && window.adobeViewerAPIs && navigationTarget.doc_id === currentDoc?.id) {
        window.adobeViewerAPIs.gotoLocation(navigationTarget.page_number || 1, 0, 0);
        clearNavigationTarget();
    }
  }, [navigationTarget, currentDoc?.id, clearNavigationTarget]);

  return (
    <div className="h-full">
      <div id="adobe-dc-view" ref={containerRef} className="h-full" />
    </div>
  );
}