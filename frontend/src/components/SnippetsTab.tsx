import { useAppStore } from "../store/useAppStore";
import type { Snippet } from "../api/types";
import { SkeletonLoader } from "./SkeletonLoader";
import { EmptyState } from "./EmptyState";
import { DocumentIcon } from "./Icons";

export default function SnippetsTab() {
  const { snippets, loadingSnippets, navigateToSnippet, selectedSnippetId, setSelectedSnippetId } = useAppStore();

  if (loadingSnippets) { return <SkeletonLoader />; }
  if (snippets.length === 0) {
    return <EmptyState icon={<span>✍️</span>} message="Select text to discover related snippets." />;
  }

  const handleSnippetClick = (snippet: Snippet) => {
    setSelectedSnippetId(snippet.doc_id + snippet.text); // Create a simple unique ID
    navigateToSnippet(snippet);
  };

  return (
    <div className="h-full flex flex-col">
      <div className="scrolly space-y-3 h-full -mr-2 pr-2">
        {snippets.map((s) => {
          const uniqueId = s.doc_id + s.text;
          const isSelected = selectedSnippetId === uniqueId;
          return (
            <button 
              key={uniqueId}
              onClick={() => handleSnippetClick(s)}
              className={`w-full text-left border rounded-lg p-3 transition-all ${isSelected ? 'border-accent ring-2 ring-accent-light bg-accent-light' : 'bg-surface-inset border-gray-200 hover:border-gray-300'}`}
            >
              <div className={`flex items-center gap-2 text-sm font-semibold truncate mb-1 ${isSelected ? 'text-accent-dark' : 'text-content'}`} title={s.doc_name}>
                <DocumentIcon className="w-4 h-4 flex-shrink-0" />
                {s.doc_name}
              </div>
              <div className="text-xs text-content-subtle mb-2">
                {s.page_number ? `Page ${s.page_number}` : "N/A"}
              </div>
              <p className="text-sm text-content leading-relaxed">"{s.text}"</p>
            </button>
          )
        })}
      </div>
    </div>
  );
}