import { useEffect, useRef, useState } from "react";
import { api } from "../api.js";
import { useI18n } from "../i18n/index.jsx";

function formatText(text) {
  return text
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\n/g, "<br/>");
}

export default function ChatPanel({ baby }) {
  const { t, lang } = useI18n();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const bottomRef = useRef(null);
  const textareaRef = useRef(null);

  // Reset welcome message on language change
  useEffect(() => {
    setMessages([
      { id: "welcome", role: "assistant", text: t("chat.welcome") },
    ]);
  }, [lang, t]);

  // Reset session when switching babies
  useEffect(() => {
    setSessionId(null);
    setMessages([
      { id: "welcome", role: "assistant", text: t("chat.welcome") },
    ]);
  }, [baby?.id, t]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const hasUserMessages = messages.some((m) => m.role === "user");

  const send = async (text) => {
    const msg = (text || input).trim();
    if (!msg || loading) return;
    setMessages((m) => [...m, { id: Date.now(), role: "user", text: msg }]);
    setInput("");
    setLoading(true);
    try {
      const data = await api.chat(msg, sessionId, baby?.id, lang);
      setSessionId(data.session_id);
      setMessages((m) => [
        ...m,
        { id: Date.now() + 1, role: "assistant", text: data.response },
      ]);
    } catch {
      setMessages((m) => [
        ...m,
        {
          id: Date.now() + 1,
          role: "assistant",
          text: t("chat.error"),
          error: true,
        },
      ]);
    } finally {
      setLoading(false);
      textareaRef.current?.focus();
    }
  };

  const onKey = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  const suggestions = [
    "chat.suggested.growth",
    "chat.suggested.milestones",
    "chat.suggested.vaccines",
    "chat.suggested.feeding",
  ];

  return (
    <div className="chat-panel">
      <div className="feed">
        <div className="feed-inner">
          {!baby && (
            <div className="msg-banner">{t("chat.no_baby_warning")}</div>
          )}
          {messages.map((m) => (
            <div key={m.id} className={`msg ${m.role}`}>
              {m.role === "assistant" && (
                <div className="msg-avatar">B</div>
              )}
              <div className={`msg-content ${m.error ? "error" : ""}`}>
                {m.role === "assistant" ? (
                  <div
                    dangerouslySetInnerHTML={{ __html: formatText(m.text) }}
                  />
                ) : (
                  m.text
                )}
              </div>
              {m.role === "user" && <div className="msg-avatar user">Me</div>}
            </div>
          ))}
          {loading && (
            <div className="msg assistant">
              <div className="msg-avatar">B</div>
              <div className="msg-content typing">
                <span /> <span /> <span />
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {!hasUserMessages && (
          <div className="suggestions">
            {suggestions.map((k) => (
              <button
                key={k}
                className="suggestion-chip"
                onClick={() => send(t(k))}
              >
                {t(k)}
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="composer">
        <div className="composer-inner">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={onKey}
            placeholder={t("chat.placeholder")}
            rows={1}
            disabled={loading}
          />
          <button
            className="send-btn"
            onClick={() => send()}
            disabled={!input.trim() || loading}
            aria-label="send"
          >
            ↑
          </button>
        </div>
        <p className="composer-hint">{t("chat.disclaimer")}</p>
      </div>
    </div>
  );
}
