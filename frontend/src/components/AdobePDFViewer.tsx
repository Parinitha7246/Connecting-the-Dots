/* global AdobeDC */
import { useEffect, useRef } from "react";
import { ADOBE_CLIENT_ID } from "../config";
import { useAppStore } from "../store/useAppStore";
import { getRecommendations } from "../api/insights";
import { MAX_SNIPPETS } from "../config";

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
    .then((adobeViewer: any) => {
      console.log("Adobe Viewer is ready.");
      return adobeViewer.getAPIs();
    })
    .then((apis: any) => {
      console.log("Adobe APIs are ready.");
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
              
              const rec = await getRecommendations(text, MAX_SNIPPETS, onlineModeRef.current);
              
              let snippets = rec?.offline?.recommendations ?? [];
              snippets = snippets.map(s => ({ ...s, doc_name: s.document, doc_id: s.document }));
              setSnippets(snippets);

              if (onlineModeRef.current && rec.online) {
                // If rec.online is a string, parse it. Otherwise, assume it's already an object.
                const onlineInsights = typeof rec.online === 'string' 
                  ? JSON.parse(rec.online.replace(/```json\n|```/g, '')) 
                  : rec.online;
                
                // --- THIS IS THE ONLY CHANGE IN THIS FILE ---
                // We now look for the 'examples' field and save it to the store.
                setInsightsPack({
                    themes: onlineInsights.themes || [],
                    insights: onlineInsights.insights || [],
                    didYouKnow: onlineInsights.did_you_know || "",
                    contradiction: onlineInsights.contradictions || "",
                    connections: onlineInsights.connections || [],
                    examples: onlineInsights.examples || [], // <-- ADD THIS LINE
                });
              } else {
                setInsightsPack({ themes: [], insights: [], didYouKnow: "", contradiction: "", connections: [], examples: [] });
              }
            } catch (e) {
              console.error("Error processing text selection:", e);
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
    .catch((error: any) => {
      console.error("Fatal error initializing Adobe Viewer:", error);
    });

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