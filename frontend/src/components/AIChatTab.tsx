import { useState } from "react";
import { docChat } from "../api/insights"; // <-- Import our new function
import { SendIcon } from "./Icons";
import { EmptyState } from "./EmptyState";

// Define a type for our message objects for better type safety
type Message = { 
  role: "user" | "assistant"; 
  text: string;
};

export default function AIChatTab() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false); // <-- Add a loading state

  // --- THIS IS THE IMPLEMENTED 'send' FUNCTION ---
  async function send() {
    const userMessage = input.trim();
    if (!userMessage || isLoading) return;

    // Add the user's message to the chat history immediately
    setMessages(prev => [...prev, { role: "user", text: userMessage }]);
    setInput("");
    setIsLoading(true);

    try {
      // Call the backend API
      const response = await docChat(userMessage);
      
      // Create the assistant's response message object
      const assistantMessage: Message = {
        role: "assistant",
        text: response.response || "Sorry, I encountered an error."
      };

      // Add the assistant's message to the chat history
      setMessages(prev => [...prev, assistantMessage]);

    } catch (error) {
      console.error("AI Chat failed:", error);
      // If the API call fails, add an error message to the chat
      const errorMessage: Message = {
        role: "assistant",
        text: "Sorry, I couldn't connect to the AI assistant right now."
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      // Always stop the loading state
      setIsLoading(false);
    }
  }

  return (
    <div className="h-full flex flex-col">
      <div className="scrolly flex-1 space-y-4 pr-2 -mr-2">
        {messages.length === 0 && (
          <EmptyState icon={<span>💬</span>} message="Ask a question about any of your uploaded documents."/>
        )}
        
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-xs md:max-w-md p-3 rounded-2xl text-sm ${m.role === 'user' ? 'bg-primary text-white rounded-br-lg' : 'bg-surface-inset text-content rounded-bl-lg'}`}>
              {m.text}
            </div>
          </div>
        ))}
        
        {/* Show a "Thinking..." bubble while waiting for the backend */}
        {isLoading && (
          <div className="flex justify-start">
            <div className="max-w-xs md:max-w-md p-3 rounded-2xl text-sm bg-surface-inset text-content-subtle rounded-bl-lg animate-pulse">
              Thinking...
            </div>
          </div>
        )}
      </div>

      <div className="mt-4 pt-4 border-t flex gap-2">
        <input
          className="bg-surface-inset border-gray-200 rounded-full px-4 py-2 flex-1 focus:ring-2 focus:ring-primary focus:outline-none disabled:opacity-50"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && send()}
          placeholder={isLoading ? "Waiting for response..." : "Ask about your documents..."}
          disabled={isLoading} // Disable input while loading
        />
        <button 
          className="bg-primary text-white rounded-full w-10 h-10 flex-shrink-0 flex items-center justify-center hover:bg-primary-hover disabled:opacity-50" 
          onClick={send}
          disabled={isLoading} // Disable button while loading
        >
          <SendIcon />
        </button>
      </div>
    </div>
  );
}