import { useEffect, useRef, useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { getChatHistory, imageUrl, sendChat } from "../api";
import { useAuth } from "../auth";
import { useSearchResults } from "../searchResults";
import type { ChatTurn, Product } from "../types";

interface DisplayMessage {
  role: "user" | "assistant";
  content: string;
  products?: Product[];
}

const GREETING: DisplayMessage = {
  role: "assistant",
  content: "Hi! Ask me about Campus Customs gear — I can check real prices and stock for you.",
};

export default function ChatWidget() {
  const { user } = useAuth();
  const { setMatches } = useSearchResults();
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<DisplayMessage[]>([GREETING]);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = messagesRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages, isSending]);

  useEffect(() => {
    if (!user) {
      setMessages([GREETING]);
      return;
    }
    getChatHistory(user.id)
      .then((history) => {
        if (history.length === 0) {
          setMessages([GREETING]);
          return;
        }
        setMessages(
          history.map((entry) => ({
            role: entry.role,
            content: entry.content,
            products: entry.products.length > 0 ? entry.products : undefined,
          })),
        );
      })
      .catch(() => {
        // Keep the default greeting if history can't be loaded.
      });
  }, [user]);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const text = input.trim();
    if (!text || isSending) return;

    const history: ChatTurn[] = messages.map((m) => ({ role: m.role, content: m.content }));
    setMessages((current) => [...current, { role: "user", content: text }]);
    setInput("");
    setError(null);
    setIsSending(true);
    try {
      const result = await sendChat({ message: text, user_id: user?.id ?? null, history });
      setMessages((current) => [
        ...current,
        { role: "assistant", content: result.reply, products: result.products.length > 0 ? result.products : undefined },
      ]);
      if (result.products.length > 0) {
        // Drives the page-level ProductMatchesPanel (Problem 7) — the same
        // search results also shown inline above, now surfaced on the page.
        setMatches(text, result.products);
      }
    } catch {
      setError("Something went wrong reaching the shop assistant. Please try again.");
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
          <div className="chat-messages" ref={messagesRef}>
            {messages.map((message, index) => (
              <div key={index} className={`chat-message chat-message-${message.role}`}>
                {message.content}
                {message.products && message.products.length > 0 && (
                  <div className="chat-products">
                    {message.products.map((product) => (
                      <Link
                        key={product.product_id}
                        to={`/products/${product.product_id}`}
                        className="chat-product-card"
                        onClick={() => setIsOpen(false)}
                      >
                        <img src={imageUrl(product.image_url)} alt={product.name} />
                        <div>
                          <div className="chat-product-name">{product.name}</div>
                          <div className="chat-product-price">${product.price.toFixed(2)}</div>
                        </div>
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            ))}
            {isSending && <div className="chat-message chat-message-assistant">Typing…</div>}
            {error && <div className="chat-message chat-message-assistant chat-message-error">{error}</div>}
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
