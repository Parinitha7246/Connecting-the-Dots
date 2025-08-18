import { useRef, useState, useMemo } from "react";
import { useAppStore } from "../store/useAppStore";
import { ingestDocuments, listDocuments, deleteDocument } from "../api/documents";
import { UploadIcon, DocumentIcon, DeleteIcon } from "./Icons";

export default function Sidebar() {
  const { 
    docs, currentDoc, setCurrentDoc, onlineMode, setOnline, setDocs, 
    latestCurrentDocId, setLatestCurrentDocId, removeDocument 
  } = useAppStore();

  const fileRef = useRef<HTMLInputElement>(null);
  const [historical, setHistorical] = useState(true);
  const [busy, setBusy] = useState(false);

  async function onUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const files = e.target.files;
    if (!files || !files.length) return;

    const filesToUpload = Array.from(files);
    setBusy(true);
    try {
      await ingestDocuments(filesToUpload, historical);
      const items = await listDocuments();
      setDocs(items);
      
      if (!historical && filesToUpload.length > 0) {
        const newDoc = items.find(d => d.name === filesToUpload[0].name);
        if (newDoc) {
          setLatestCurrentDocId(newDoc.id);
          setCurrentDoc(newDoc);
        }
      } else if (!currentDoc && items.length > 0) {
        setCurrentDoc(items[0]);
      }
    } catch (error) {
      console.error("Upload failed:", error);
      alert("An error occurred during the upload. Please check the console for details.");
    } finally {
      setBusy(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  }

  const handleDelete = async (docId: string, docName: string) => {
    if (window.confirm(`Are you sure you want to delete "${docName}"?`)) {
      try {
        await deleteDocument(docId);
        removeDocument(docId);
      } catch (error) {
        console.error("Delete failed:", error);
        alert(`Failed to delete the document: ${docName}`);
      }
    }
  };

  const sortedDocs = useMemo(() => {
    return [...docs].sort((a, b) => {
      if (a.id === latestCurrentDocId) return -1;
      if (b.id === latestCurrentDocId) return 1;
      return a.name.localeCompare(b.name);
    });
  }, [docs, latestCurrentDocId]);

  return (
    <div className="card flex flex-col gap-4 h-full">
      
      {/* --- HEADER SECTION --- */}
      <div>
        <div className="flex items-center gap-3">
          <div className="bg-primary p-2 rounded-lg">
            <svg className="w-6 h-6 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
          </div>
          <div className="text-xl font-bold text-content">DocuWise</div>
        </div>
        <div className="border-t -mx-4 mt-4"></div>
      </div>
      
      {/* --- UPLOAD SECTION --- */}
      <div>
        <button
          className="w-full bg-surface border-2 border-gray-300 hover:border-primary hover:text-primary text-content-subtle font-semibold rounded-lg px-3 py-2 disabled:opacity-60 flex items-center justify-center gap-2 transition-colors"
          onClick={() => fileRef.current?.click()}
          disabled={busy}
        >
          <UploadIcon className="w-4 h-4" />
          {busy ? "Uploading..." : "Upload Documents"}
        </button>
        <input 
          ref={fileRef} type="file" multiple accept="application/pdf" className="hidden" 
          onChange={onUpload} 
        />
        <label className="text-sm flex items-center gap-2 text-content-subtle cursor-pointer mt-4">
          <input 
            type="checkbox" 
            checked={historical} 
            // --- THIS IS THE CORRECTED LINE ---
            // It now correctly uses e.target.checked
            onChange={(e) => setHistorical(e.target.checked)} 
            className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
          />
          Mark as “Past documents”
        </label>
      </div>

      {/* --- DOCUMENT LIST SECTION --- */}
      <div className="flex flex-col flex-1 min-h-0">
        <div className="text-sm font-semibold text-content mb-2">Documents</div>
        <div className="flex-1 scrolly -mx-2 pr-1">
          {sortedDocs.length === 0 && <div className="text-content-subtle text-sm px-2">No documents uploaded yet.</div>}
          
          {sortedDocs.map((d) => {
            const isLatestCurrent = d.id === latestCurrentDocId;
            const isSelected = d.id === currentDoc?.id;
            
            return (
              <div key={d.id} className={`group flex items-center justify-between rounded-lg pr-2 transition-colors ${isSelected ? "bg-primary-light" : isLatestCurrent ? "bg-accent-light" : "hover:bg-gray-100"}`}>
                <button
                  onClick={() => setCurrentDoc(d)}
                  className={`w-full text-left p-2 rounded-lg text-sm flex items-center gap-3 ${isSelected ? "text-primary font-semibold" : isLatestCurrent ? "text-accent-dark font-semibold" : "text-content"}`}
                  title={d.name}
                >
                  <DocumentIcon className="w-5 h-5 flex-shrink-0" />
                  <span className="truncate">{d.name}</span>
                </button>
                
                <button 
                  onClick={() => handleDelete(d.id, d.name)}
                  className="opacity-0 group-hover:opacity-100 text-red-500 hover:text-red-700 p-1 rounded-full hover:bg-red-100 transition-opacity"
                  title={`Delete ${d.name}`}
                >
                  <DeleteIcon />
                </button>
              </div>
            )
          })}
        </div>
      </div>

      {/* --- FOOTER SECTION --- */}
      <div>
        <div className="border-t -mx-4 mb-4"></div>
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-content">Online Mode</span>
          <label className="inline-flex items-center cursor-pointer">
            <input type="checkbox" className="sr-only peer" checked={onlineMode} onChange={(e)=>setOnline(e.target.checked)} />
            <div className="w-11 h-6 bg-gray-200 peer-checked:bg-primary rounded-full relative">
              <div className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full transition-transform ${onlineMode ? "translate-x-5" : ""}`} />
            </div>
          </label>
        </div>
      </div>
    </div>
  );
}