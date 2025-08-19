/* global AdobeDC */
import { useEffect, useRef } from "react";
import { ADOBE_CLIENT_ID, MAX_SNIPPETS } from "../config";
import { useAppStore } from "../store/useAppStore";
import { getRecommendations, getInsights } from "../api/insights";

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

  const onlineModeRef = useRef(onlineMode);
  useEffect(() => {
    onlineModeRef.current = onlineMode;
  }, [onlineMode]);

  // This main effect ONLY runs when the document changes, to initialize the viewer.
  useEffect(() => {
    if (!currentDoc || !currentDoc.url || !containerRef.current || !window.AdobeDC) return;

    // --- THIS IS THE FIX ---
    // The call to resetRightPanel() has been REMOVED from this hook.
    // The panel will no longer be cleared just because the document changes.

    const adobeDCView = new window.AdobeDC.View({
      clientId: ADOBE_CLIENT_ID,
      divId: "adobe-dc-view",
    });

    adobeDCView.previewFile({
      content: { location: { url: currentDoc.url } },
      metaData: { id: currentDoc.id, fileName: currentDoc.name },
    }, { 
      embedMode: "SIZED_CONTAINER",
      enableAnnotationAPIs: true, 
    })
    .then((adobeViewer: any) => adobeViewer.getAPIs())
    .then((apis: any) => {
      window.adobeViewerAPIs = apis;

      // Listen for text selection events
      adobeDCView.registerCallback(
        window.AdobeDC.View.Enum.CallbackType.EVENT_LISTENER,
        async (event: any) => {
          if (event.type === window.AdobeDC.View.Enum.FilePreviewEvents.PREVIEW_SELECTION_END) {
            try {
              // --- THIS IS THE FIX ---
              // We now call resetRightPanel() HERE.
              // This means the panel is only cleared when the user makes a NEW selection.
              resetRightPanel();

              const result = await apis.getSelectedContent();
              const text = (result?.data || "").trim();
              if (!text) return;

              setSelectedText(text);
              setLoadingSnippets(true);

              const rec = await getRecommendations(text, MAX_SNIPPETS, onlineModeRef.current);
              let snippets = rec?.recommendations ?? [];
              // The backend now provides consistent doc_id and doc_name, so we trust it
              setSnippets(snippets);

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
              }
            } catch (e) {
              console.error("Error processing text selection:", e);
              setSnippets([]);
              setInsightsPack({ themes: [], insights: [], didYouKnow: "", contradiction: "", connections: [], examples: [] });
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

    return () => {
      window.adobeViewerAPIs = undefined;
      if (containerRef.current) containerRef.current.innerHTML = "";
    };
  }, [currentDoc]); // This effect correctly ONLY depends on the currentDoc

  // This effect handles jump-to-location and is correct as is.
  useEffect(() => {
    if (navigationTarget && window.adobeViewerAPIs && navigationTarget.doc_id === currentDoc?.id) {
      window.adobeViewerAPIs.gotoLocation(navigationTarget.page_number || 1, 0, 0)
        .catch((e: any) => console.error("gotoLocation failed:", e))
        .finally(() => clearNavigationTarget());
    }
  }, [navigationTarget, currentDoc?.id, clearNavigationTarget]);

  return (
    <div className="h-full">
      <div id="adobe-dc-view" ref={containerRef} className="h-full" />
    </div>
  );
}
