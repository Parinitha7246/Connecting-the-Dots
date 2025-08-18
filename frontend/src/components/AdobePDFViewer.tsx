/* global AdobeDC */
import { useEffect, useRef } from "react";
import { ADOBE_CLIENT_ID } from "../config";
import { useAppStore } from "../store/useAppStore";
// --- This is the corrected import. We get 'getRecommendations' from 'insights.ts' ---
import { getRecommendations, getInsights } from "../api/insights";
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
    if (!currentDoc || !containerRef.current || !window.AdobeDC) return;

    resetRightPanel();

    const view = new window.AdobeDC.View({
      clientId: ADOBE_CLIENT_ID,
      divId: "adobe-dc-view",
    });

    const previewFilePromise = view.previewFile({
      content: { location: { url: currentDoc.url } },
      metaData: { fileName: currentDoc.name },
    }, { embedMode: "SIZED_CONTAINER" });

    previewFilePromise.then((adobeViewer: any) => {
      adobeViewer.getAPIs().then((apis: any) => {
        window.adobeViewerAPIs = apis;
        
        // Navigation logic
        if (navigationTarget && navigationTarget.doc_id === currentDoc.id) {
            // ...
        }

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

                // --- THIS IS THE CORRECTED API CALL ---
                // We use the getRecommendations function, which correctly calls the /recommend endpoint.
                const rec = await getRecommendations("General", text.slice(0, 120), MAX_SNIPPETS);
                const snippets = rec?.recommendations ?? [];
                setSnippets(snippets);

                const texts = snippets.map(s => s.text).filter(Boolean).slice(0, 6);
                if (texts.length) {
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
}, [currentDoc?.id, onlineMode]);

  useEffect(() => {
    if (navigationTarget && window.adobeViewerAPIs && navigationTarget.doc_id === currentDoc?.id) {
        window.adobeViewerAPIs.gotoLocation(navigationTarget.page_number || 1, 0, 0);
        clearNavigationTarget();
    }
  }, [navigationTarget]);

  return (
    <div className="h-full">
      <div id="adobe-dc-view" ref={containerRef} className="h-full min-h-[70vh]" />
    </div>
  );
}