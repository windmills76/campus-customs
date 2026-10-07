import { useState, type FormEvent } from "react";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

// TODO(Problem 5): replace this stub with a real call to POST /api/chat on the
// agent backend. The agent's reply should also be able to return matching
// products so the page can surface them alongside the chat response.
async function sendMessage(_history: ChatMessage[], userText: string): Promise<string> {
  void _history;
  void userText;
  await new Promise((resolve) => setTimeout(resolve, 300));
  return "Our shopping assistant is getting ready — check back soon! In the meantime, browse Products to see what's in stock.";
}

export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: "assistant", content: "Hi! I'll be able to help you find Campus Customs gear soon." },
  ]);
  const [isSending, setIsSending] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const text = input.trim();
    if (!text || isSending) return;

    const nextMessages: ChatMessage[] = [...messages, { role: "user", content: text }];
    setMessages(nextMessages);
    setInput("");
    setIsSending(true);
    try {
      const reply = await sendMessage(nextMessages, text);
      setMessages((current) => [...current, { role: "assistant", content: reply }]);
    } finally {
      setIsSending(false);
    }
  }

  return (
    <div className="chat-widget">
      {isOpen && (
        <div className="chat-panel">
          <div className="chat-panel-header">
            <span>Campus Customs Chat</span>
            <button type="button" className="chat-close" onClick={() => setIsOpen(false)} aria-label="Close chat">
              ×
            </button>
          </div>
          <div className="chat-messages">
            {messages.map((message, index) => (
              <div key={index} className={`chat-message chat-message-${message.role}`}>
                {message.content}
              </div>
            ))}
            {isSending && <div className="chat-message chat-message-assistant">Typing…</div>}
          </div>
          <form className="chat-input-row" onSubmit={handleSubmit}>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about our merch…"
              aria-label="Chat message"
            />
            <button type="submit" disabled={isSending}>
              Send
            </button>
          </form>
        </div>
      )}
      <button type="button" className="chat-toggle" onClick={() => setIsOpen((open) => !open)}>
        {isOpen ? "Close" : "Chat"}
      </button>
    </div>
  );
}
