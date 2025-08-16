import { useState } from "react";
import { chat } from "../api/insights";
import { useAppStore } from "../store/useAppStore";
import { SendIcon } from "./Icons";
import { EmptyState } from "./EmptyState";

type Msg = { role: "user"|"assistant"; text: string };

export default function AIChatTab() {
  const [msgs, setMsgs] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const { snippets } = useAppStore();

  async function send() { /* ... function is the same */ }

  return (
    <div className="h-full flex flex-col">
      <div className="scrolly flex-1 space-y-4 pr-2 -mr-2">
        {msgs.length === 0 && <EmptyState icon={<span>💬</span>} message="Ask a follow-up question about your selected text."/>}
        {msgs.map((m,i)=>(
          <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-xs md:max-w-md p-3 rounded-2xl text-sm ${m.role === 'user' ? 'bg-primary text-white rounded-br-lg' : 'bg-surface-inset text-content rounded-bl-lg'}`}>
              {m.text}
            </div>
          </div>
        ))}
      </div>
      <div className="mt-4 pt-4 border-t flex gap-2">
        <input
          className="bg-surface-inset border-gray-200 rounded-full px-4 py-2 flex-1 focus:ring-2 focus:ring-primary focus:outline-none"
          value={input}
          onChange={(e)=>setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && send()}
          placeholder="Ask a follow-up..."
        />
        <button className="bg-primary text-white rounded-full w-10 h-10 flex-shrink-0 flex items-center justify-center hover:bg-primary-hover" onClick={send}>
          <SendIcon />
        </button>
      </div>
    </div>
  );
}