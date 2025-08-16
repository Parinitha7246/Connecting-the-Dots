import { useEffect } from "react";
import Sidebar from "./components/Sidebar";
import AdobePDFViewer from "./components/AdobePDFViewer";
import RightPanel from "./components/RightPanel";
import { listDocuments } from "./api/documents";
import { useAppStore } from "./store/useAppStore";
import { BookIcon, BulbIcon } from "./components/Icons";

// --- THIS IS THE CORRECTED WELCOME CARD ---
// It now has a transparent background and a dotted border, just like the Unlock Insights card.
const WelcomeCard = () => (
  <div className="h-full flex flex-col items-center justify-center text-center bg-transparent border-2 border-dashed border-gray-300 rounded-xl">
    <BookIcon />
    <h2 className="text-xl font-bold text-content mt-4">Welcome to DocuWise</h2>
    <p className="text-content-subtle mt-1 max-w-xs">Please upload a document and select it from the sidebar to begin.</p>
  </div>
);

const UnlockInsightsCard = () => (
  <div className="h-full flex flex-col items-center justify-center text-center bg-transparent border-2 border-dashed border-gray-300 rounded-xl">
    <BulbIcon />
    <h2 className="text-xl font-bold text-content mt-4">Unlock Insights</h2>
    <p className="text-content-subtle mt-1 max-w-xs">Select text in a document to discover related snippets, generate insights, and chat with your documents.</p>
  </div>
);

export default function App() {
  const { setDocs, docs, setCurrentDoc, currentDoc } = useAppStore();

  useEffect(() => {
    (async () => {
      try {
        const items = await listDocuments();
        setDocs(items);
        if (items.length && !currentDoc) {
          setCurrentDoc(items[0]);
        }
      } catch (e) { 
        console.warn("Backend not connected: Failed to list documents.", e); 
      }
    })();
  }, [setDocs, setCurrentDoc, currentDoc]);

  return (
    <div className="h-screen grid grid-cols-[280px_1fr_380px] gap-4 p-4 bg-surface-ground">
      <Sidebar />
      
      {/* This structure is now correct. It will render the WelcomeCard with its dotted border. */}
      {/* When documents are loaded, it will render the PDF viewer inside a solid card. */}
      <div className="relative overflow-hidden">
        {docs.length > 0 ? (
          <div className="card h-full p-0">
            <AdobePDFViewer />
          </div>
        ) : (
          <WelcomeCard />
        )}
      </div>

      {docs.length > 0 ? (
        <RightPanel />
      ) : (
        <UnlockInsightsCard />
      )}
    </div>
  );
}