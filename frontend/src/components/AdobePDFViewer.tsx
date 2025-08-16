/* global AdobeDC */
import { useEffect, useRef } from "react";
import { ADOBE_CLIENT_ID } from "../config";
import { useAppStore } from "../store/useAppStore";
import { recommendBySelection } from "../api/documents";
import { getInsights } from "../api/insights";
import { MAX_SNIPPETS } from "../config";

declare global {
  interface Window { 
    AdobeDC: any;
    adobeViewerAPIs?: any;
  }
}

export default function AdobePDFViewer() {
  const containerRef = useRef<HTMLDivElement>(null);
  const { currentDoc, setSelectedText, setSnippets, setLoadingSnippets,
          onlineMode, setInsightsPack, resetRightPanel,
          navigationTarget, clearNavigationTarget
        } = useAppStore();

  useEffect(() => {
    // This check is crucial for the live version.
    if (!currentDoc || !containerRef.current || !window.AdobeDC) return;

    resetRightPanel();

    const view = new window.AdobeDC.View({
      clientId: ADOBE_CLIENT_ID,
      divId: "adobe-dc-view",
    });

    // --- THIS IS THE LIVE, DYNAMIC CODE ---
    // It now uses the URL from the currently selected document.
    const previewFilePromise = view.previewFile({
      content: { location: { url: currentDoc.url } },
      metaData: { fileName: currentDoc.name },
    }, { embedMode: "SIZED_CONTAINER" });

    previewFilePromise.then((adobeViewer: any) => {
      adobeViewer.getAPIs().then((apis: any) => {
        window.adobeViewerAPIs = apis;
        
        // ... (The rest of the logic for navigation and event handling is already correct) ...

        const opts = {
          enableFilePreviewEvents: true,
          listenOn: [ 
            window.AdobeDC.View.Enum.FilePreviewEvents.PREVIEW_SELECTION_END,
            window.AdobeDC.View.Enum.FilePreviewEvents.PAGES_IN_VIEW_CHANGE
          ],
        };

        view.registerCallback(window.AdobeDC.View.Enum.CallbackType.EVENT_LISTENER,
          async (event: any) => {
            if (event?.type === window.AdobeDC.View.Enum.FilePreviewEvents.PREVIEW_SELECTION_END) {
              try {
                const result = await apis.getSelectedContent();
                const text = (result?.data || "").trim();
                if (!text) return;

                setSelectedText(text);
                setLoadingSnippets(true);

                // --- Live API Call for Snippets ---
                const rec = await recommendBySelection(text, MAX_SNIPPETS, onlineMode);
                const snippets = rec?.recommendations ?? [];
                setSnippets(snippets);

                const texts = snippets.map(s => s.text).filter(Boolean).slice(0, 6);
                if (texts.length) {
                  // --- Live API Call for Insights ---
                  const ins = await getInsights(texts);
                  setInsightsPack({
                    themes: ins?.parsed?.themes || [],
                    insights: ins?.parsed?.insights || [],
                    didYouKnow: ins?.parsed?.did_you_know || "",
                    contradiction: ins?.parsed?.contradictions || "",
                    connections: ins?.parsed?.connections || [],
                  });
                }
              } finally {
                setLoadingSnippets(false);
              }
            }

            if (event?.type === window.AdobeDC.View.Enum.FilePreviewEvents.PAGES_IN_VIEW_CHANGE) {
              console.log("User is now viewing pages:", event.data);
            }

          }, opts);
      });
    });

    return () => {
      window.adobeViewerAPIs = null;
      if (containerRef.current) containerRef.current.innerHTML = "";
    };
  }, [currentDoc?.id, onlineMode]); // Simplified dependencies for live version

  // ... (The second useEffect for navigation remains the same) ...
  useEffect(() => {
    if (navigationTarget && window.adobeViewerAPIs && navigationTarget.doc_id === currentDoc?.id) {
        // ...
    }
  }, [navigationTarget]);

  return (
    <div className="h-full">
      <div id="adobe-dc-view" ref={containerRef} className="h-full min-h-[70vh]" />
    </div>
  );
}