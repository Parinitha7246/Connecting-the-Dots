import { useAppStore } from "../store/useAppStore";
import type { Snippet } from "../api/types";
import { SkeletonLoader } from "./SkeletonLoader";
import { EmptyState } from "./EmptyState";
import { DocumentIcon } from "./Icons";

const getRelationStyles = (relationType?: Snippet["relation_type"]) => {
  switch (relationType) {
    case "overlap":
      return "border-relation-overlap-dark bg-relation-overlap-light";
    case "contradiction":
      return "border-relation-contradiction-dark bg-relation-contradiction-light";
    case "example":
    case "supporting":
    case "related":
      return "border-relation-example-dark bg-relation-example-light";
    default:
      return "border-gray-300 bg-surface-inset";
  }
};

export default function SnippetsTab() {
  const {
    snippets,
    loadingSnippets,
    navigateToSnippet,
    selectedSnippetId,
    setSelectedSnippetId,
  } = useAppStore();

  if (loadingSnippets) return <SkeletonLoader />;
  if (snippets.length === 0) {
    return (
      <EmptyState
        icon={<span>✍️</span>}
        message="Select text to discover related snippets."
      />
    );
  }

  const handleSnippetClick = (snippet: Snippet, uniqueId: string) => {
  setSelectedSnippetId(uniqueId);

  console.log("--- JUMP PROCESS STEP 1: SNIPPET CLICKED ---");
  console.log("Sending this snippet object to the store:", snippet);

  // --- Normalize doc_id ---
  let rawId = snippet.document_id || snippet.doc_id || snippet.document;
  let doc_id = rawId?.endsWith(".pdf") ? rawId : `${rawId}.pdf`;

  navigateToSnippet({
    ...snippet,
    doc_id,
    doc_name: snippet.document_name || snippet.doc_name || snippet.document,
  });
};


  return (
    <div className="h-full flex flex-col">
      <div className="scrolly space-y-3 h-full -mr-2 pr-2">
        {snippets.map((s, index) => {
          const baseId = s.document_id || s.doc_id || s.document || "snippet";
          const uniqueId = baseId + index;
          const isSelected = selectedSnippetId === uniqueId;
          const relationStyles = getRelationStyles(s.relation_type);

          return (
            <button
              key={uniqueId}
              onClick={() => handleSnippetClick(s, uniqueId)}
              className={`w-full text-left border rounded-lg p-3 transition-all ${
                isSelected ? "ring-2 ring-primary ring-offset-2" : relationStyles
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <div
                  className="flex items-center gap-2 text-sm font-semibold text-content truncate"
                  title={s.document_name || s.doc_name || s.document}
                >
                  <DocumentIcon className="w-4 h-4 flex-shrink-0" />
                  <span>{s.document_name || s.doc_name || s.document}</span>
                </div>
                {s.relation_type && (
                  <span
                    className={`text-xs font-semibold capitalize px-2 py-0.5 rounded-full bg-white border ${relationStyles}`}
                  >
                    {s.relation_type}
                  </span>
                )}
              </div>
              {s.section_heading && (
                <div className="text-xs font-semibold text-content-subtle mb-1">
                  In section: "{s.section_heading}"
                </div>
              )}
              <div className="text-xs text-content-subtle mb-2">
                {s.page_number ? `Page ${s.page_number}` : "N/A"}
              </div>
              <p className="text-sm text-content leading-relaxed">
                "{s.snippet || s.snippet_text || s.text}"
              </p>
            </button>
          );
        })}
      </div>
    </div>
  );
}