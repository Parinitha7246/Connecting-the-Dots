import { useEffect, useState } from "react";
import Sidebar from "./components/Sidebar";
import AdobePDFViewer from "./components/AdobePDFViewer";
import RightPanel from "./components/RightPanel";
import { listDocuments } from "./api/documents";
import { useAppStore } from "./store/useAppStore";
import { BookIcon, BulbIcon } from "./components/Icons";

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
  const { setDocs, docs, setCurrentDoc, latestCurrentDocId } = useAppStore();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const initializeApp = async () => {
      try {
        const items = await listDocuments();
        setDocs(items);

        if (items.length > 0) {
          const latestDoc = items.find(d => d.id === latestCurrentDocId);
          setCurrentDoc(latestDoc || items[0]);
        }
      } catch (e) { 
        console.warn("Backend not connected or failed to list documents.", e); 
      } finally {
        setIsLoading(false);
      }
    };
    
    initializeApp();
  }, [setDocs, setCurrentDoc, latestCurrentDocId]);

  if (isLoading) {
    return (
      <div className="h-screen w-screen flex items-center justify-center bg-surface-ground text-content-subtle">
        Loading Application...
      </div>
    );
  }
  
  return (
    <div className="h-screen grid grid-cols-[280px_1fr_380px] gap-4 p-4 bg-surface-ground overflow-hidden">
      
      <div className="h-full overflow-hidden">
        <Sidebar />
      </div>
      
      <div className="h-full overflow-hidden">
        {docs.length > 0 ? (
          <div className="card h-full p-0">
            <AdobePDFViewer />
          </div>
        ) : (
          <WelcomeCard />
        )}
      </div>

      <div className="h-full overflow-hidden">
        {docs.length > 0 ? (
          <RightPanel />
        ) : (
          <UnlockInsightsCard />
        )}
      </div>
    </div>
  );
}