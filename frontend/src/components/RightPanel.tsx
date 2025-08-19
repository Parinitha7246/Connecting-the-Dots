import { useState } from "react";
import SnippetsTab from "./SnippetsTab";
import InsightsTab from "./InsightsTab";
import AIChatTab from "./AIChatTab";

export default function RightPanel() {
  const [tab, setTab] = useState<"snippets" | "insights" | "chat">("snippets");

  // The test button and its handler function have been completely removed.
  // This component is now fully dynamic.

  return (
    <div className="card h-full flex flex-col">
      <div className="flex items-center gap-2 mb-4 border-b -mx-4 px-4 pb-4">
        <button onClick={() => setTab("snippets")} className={`px-4 py-1.5 text-sm font-medium rounded-full transition-colors ${tab === 'snippets' ? 'bg-primary text-white' : 'hover:bg-gray-100 text-gray-600'}`}>Snippets</button>
        <button onClick={() => setTab("insights")} className={`px-4 py-1.5 text-sm font-medium rounded-full transition-colors ${tab === 'insights' ? 'bg-primary text-white' : 'hover:bg-gray-100 text-gray-600'}`}>Insights</button>
        <button onClick={() => setTab("chat")} className={`px-4 py-1.5 text-sm font-medium rounded-full transition-colors ${tab === 'chat' ? 'bg-primary text-white' : 'hover:bg-gray-100 text-gray-600'}`}>AI Chat</button>
      </div>

      <div className="flex-1 min-h-0">
        {tab === "snippets" && <SnippetsTab />}
        {tab === "insights" && <InsightsTab />}
        {tab === "chat" && <AIChatTab />}
      </div>
    </div>
  );
}