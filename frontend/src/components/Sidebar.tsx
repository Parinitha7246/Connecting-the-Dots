import { useRef, useState } from "react";
import { useAppStore } from "../store/useAppStore";
import { ingestDocument, listDocuments } from "../api/documents";
import { UploadIcon, DocumentIcon } from "./Icons";

export default function Sidebar() {
  const { docs, currentDoc, setCurrentDoc, onlineMode, setOnline, setDocs } = useAppStore();
  const fileRef = useRef<HTMLInputElement>(null);
  const [busy, setBusy] = useState(false);

  async function onUpload(e: React.ChangeEvent<HTMLInputElement>) {
    // ... (onUpload function remains the same)
  }

  return (
    <div className="card flex flex-col gap-4">
      <div className="flex items-center gap-3">
        <div className="bg-primary p-2 rounded-lg">
          <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
        </div>
        <div className="text-xl font-bold text-gray-800">DocuWise</div>
      </div>

      <div className="border-t -mx-4"></div>

      <button
        className="w-full bg-white border-2 border-gray-300 hover:border-primary hover:text-primary text-gray-600 font-semibold rounded-lg px-3 py-2 disabled:opacity-60 flex items-center justify-center gap-2 transition-colors"
        onClick={() => fileRef.current?.click()}
        disabled={busy}
      >
        <UploadIcon className="w-4 h-4" />
        {busy ? "Uploading..." : "Upload Documents"}
      </button>
      <input ref={fileRef} type="file" multiple accept="application/pdf" className="hidden" onChange={onUpload} />

      <div className="text-sm font-semibold text-gray-700 mt-2">Documents</div>
      <div className="scrolly flex-1 -mx-2">
        {docs.length === 0 && <div className="text-muted text-sm px-2">No documents uploaded yet.</div>}
        {docs.map((d) => (
          <button
            key={d.id}
            onClick={() => setCurrentDoc(d)}
            className={`w-full text-left px-2 py-2 rounded-lg transition-colors text-sm flex items-center gap-3 ${currentDoc?.id === d.id ? "bg-primary-light text-primary font-semibold" : "hover:bg-gray-100 text-gray-700"}`}
            title={d.name}
          >
            <DocumentIcon className="w-5 h-5 flex-shrink-0" />
            <span className="truncate">{d.name}</span>
          </button>
        ))}
      </div>

      <div className="border-t -mx-4"></div>

      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-gray-700">Online Mode</span>
        <label className="inline-flex items-center cursor-pointer">
          <input type="checkbox" className="sr-only peer" checked={onlineMode} onChange={(e)=>setOnline(e.target.checked)} />
          <div className="w-11 h-6 bg-gray-200 peer-checked:bg-primary rounded-full relative">
            <div className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full transition-transform ${onlineMode ? "translate-x-5" : ""}`} />
          </div>
        </label>
      </div>
    </div>
  );
}