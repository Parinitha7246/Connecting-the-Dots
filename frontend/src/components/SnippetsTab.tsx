import { useAppStore } from "../store/useAppStore";
import type { Snippet } from "../api/types";
import { SkeletonLoader } from "./SkeletonLoader";
import { EmptyState } from "./EmptyState";
import { DocumentIcon } from "./Icons";

// --- HELPER FUNCTION ---
// Maps relation_type to Tailwind classes
const getRelationStyles = (relationType?: Snippet["relation_type"]) => {
  switch (relationType) {
    case "overlap":
      return "border-relation-overlap-dark bg-relation-overlap-light"; // Blue
    case "contradiction":
      return "border-relation-contradiction-dark bg-relation-contradiction-light"; // Red
    case "example":
    case "supporting":
    case "related":
      return "border-relation-example-dark bg-relation-example-light"; // Green
    default:
      return "border-gray-300 bg-surface-inset"; // Neutral fallback
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

  const handleSnippetClick = (snippet: Snippet) => {
    setSelectedSnippetId(snippet.doc_id + snippet.text);
    navigateToSnippet(snippet);
  };

  return (
    <div className="h-full flex flex-col">
      <div className="scrolly space-y-3 h-full -mr-2 pr-2">
        {snippets.map((s) => {
          const uniqueId = s.doc_id + s.text;
          const isSelected = selectedSnippetId === uniqueId;
          const relationStyles = getRelationStyles(s.relation_type);

          return (
            <button
              key={uniqueId}
              onClick={() => handleSnippetClick(s)}
              className={`w-full text-left border rounded-lg p-3 transition-all ${
                isSelected
                  ? "ring-2 ring-primary ring-offset-2"
                  : relationStyles
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <div
                  className="flex items-center gap-2 text-sm font-semibold text-content truncate"
                  title={s.doc_name}
                >
                  <DocumentIcon className="w-4 h-4 flex-shrink-0" />
                  <span>{s.doc_name}</span>
                </div>

                {s.relation_type && (
                  <span
                    className={`text-xs font-semibold capitalize px-2 py-0.5 rounded-full bg-white border ${relationStyles}`}
                  >
                    {s.relation_type}
                  </span>
                )}
              </div>

              <div className="text-xs text-content-subtle mb-2">
                {s.page_number ? `Page ${s.page_number}` : "N/A"}
              </div>

              <p className="text-sm text-content leading-relaxed">
                "{s.snippet || s.text}"
              </p>
            </button>
          );
        })}
      </div>
    </div>
  );
}
