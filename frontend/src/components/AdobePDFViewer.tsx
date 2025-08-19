/* global AdobeDC */
import { useEffect, useRef } from "react";
import { ADOBE_CLIENT_ID, MAX_SNIPPETS } from "../config";
import { useAppStore } from "../store/useAppStore";
import { getRecommendations, getInsights } from "../api/insights";
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
    currentDoc,
    onlineMode,
    resetRightPanel,
    navigationTarget,
    clearNavigationTarget,
    setSnippets,
    setSelectedText,
    setLoadingSnippets,
    setInsightsPack,
  } = useAppStore();

  // Keep latest onlineMode in ref (avoids stale closure in asyncs)
  const onlineModeRef = useRef(onlineMode);
  useEffect(() => {
    onlineModeRef.current = onlineMode;
  }, [onlineMode]);

  // --- Initialize / reinitialize viewer on doc change ---
  useEffect(() => {
    if (!currentDoc || !currentDoc.url || !containerRef.current || !window.AdobeDC) return;

    console.log("--- VIEWER INIT ---");
    resetRightPanel();

    const adobeDCView = new window.AdobeDC.View({
      clientId: ADOBE_CLIENT_ID,
      divId: "adobe-dc-view",
    });

    const viewerConfig = {
      embedMode: "SIZED_CONTAINER",
      enableAnnotationAPIs: true,
      showDownloadPDF: true,
      showPrintPDF: true,
      showAnnotationTools: false,
      includePDFAnnotations: false,
    };

    adobeDCView
      .previewFile(
        {
          content: { location: { url: currentDoc.url } },
          metaData: {
            fileName: currentDoc.name,
            id: currentDoc.id,
          },
        },
        viewerConfig
      )
      .then((adobeViewer: any) => adobeViewer.getAPIs())
      .then((apis: any) => {
        window.adobeViewerAPIs = apis;

        // --- Listen for selection end → fetch selected text ---
        adobeDCView.registerCallback(
          window.AdobeDC.View.Enum.CallbackType.EVENT_LISTENER,
          async (event: any) => {
            if (event.type === window.AdobeDC.View.Enum.FilePreviewEvents.PREVIEW_SELECTION_END) {
              try {
                const result = await apis.getSelectedContent();
                const text = (result?.data || "").trim();
                if (!text) return;

                setSelectedText(text);
                setLoadingSnippets(true);

                // --- STEP 1: Get Snippets ---
                const rec = await getRecommendations(text, MAX_SNIPPETS, onlineModeRef.current);
                let snippets: Snippet[] = rec?.recommendations ?? [];
                snippets = snippets.map((s: Snippet) => ({
                  ...s,
                  doc_name: s.document,
                  doc_id: s.document,
                }));
                setSnippets(snippets);

                // --- STEP 2: If online, fetch insights from snippet texts ---
                if (onlineModeRef.current && snippets.length > 0) {
                  const snippetTexts = snippets.map((s) => s.snippet || s.text);
                  const ins = await getInsights(snippetTexts);

                  setInsightsPack({
                    themes: ins?.parsed?.themes || [],
                    insights: ins?.parsed?.insights || [],
                    didYouKnow: ins?.parsed?.did_you_know || "",
                    contradiction: ins?.parsed?.contradictions || "",
                    connections: ins?.parsed?.connections || [],
                    examples: ins?.parsed?.examples || [],
                  });
                } else {
                  // Offline mode → clear insights
                  setInsightsPack({
                    themes: [],
                    insights: [],
                    didYouKnow: "",
                    contradiction: "",
                    connections: [],
                    examples: [],
                  });
                }
              } catch (e) {
                console.error("Error processing text selection:", e);
                setSnippets([]);
                setInsightsPack({
                  themes: [],
                  insights: [],
                  didYouKnow: "",
                  contradiction: "",
                  connections: [],
                  examples: [],
                });
              } finally {
                setLoadingSnippets(false);
              }
            }
          },
          {
            enableFilePreviewEvents: true,
            listenOn: [window.AdobeDC.View.Enum.FilePreviewEvents.PREVIEW_SELECTION_END],
          }
        );
      })
      .catch((error: any) => console.error("Fatal error initializing Adobe Viewer:", error));

    // --- Cleanup ---
    return () => {
      console.log("--- Viewer cleanup triggered ---");
      window.adobeViewerAPIs = undefined;
      if (containerRef.current) containerRef.current.innerHTML = "";
    };
  }, [
    currentDoc,
    resetRightPanel,
    setSnippets,
    setLoadingSnippets,
    setInsightsPack,
    setSelectedText,
  ]);

  // --- Listen for navigation target ---
  useEffect(() => {
    console.log("--- JUMP PROCESS LISTENER ---");
    console.log("Current navigationTarget:", navigationTarget);
    console.log("Is adobeViewerAPIs available?", !!window.adobeViewerAPIs);

    if (navigationTarget && window.adobeViewerAPIs && navigationTarget.doc_id === currentDoc?.id) {
      console.log("Jumping to page:", navigationTarget.page_number);
      window.adobeViewerAPIs
        .gotoLocation(navigationTarget.page_number || 1, 0, 0)
        .then(() => console.log("Jump successful!"))
        .catch((e: any) => console.error("Jump failed with error:", e))
        .finally(() => clearNavigationTarget());
    } else if (navigationTarget) {
      console.log("Jump conditions NOT met.");
      if (!window.adobeViewerAPIs) console.error("Reason: adobeViewerAPIs not available.");
      if (navigationTarget.doc_id !== currentDoc?.id) {
        console.error("Reason: Target doc ID does not match current doc ID.", {
          target: navigationTarget.doc_id,
          current: currentDoc?.id,
        });
      }
    }
  }, [navigationTarget, currentDoc?.id, clearNavigationTarget]);

  return (
    <div className="h-full">
      <div id="adobe-dc-view" ref={containerRef} className="h-full" />
    </div>
  );
}
