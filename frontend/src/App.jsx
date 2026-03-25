import { useState, useRef, useEffect } from "react";
import "./App.css";

const SUGGESTED = [
  "Thiếu men G6PD là gì?",
  "Người thiếu men G6PD cần kiêng ăn gì?",
  "Thuốc nào cần tránh khi thiếu men G6PD?",
  "Trẻ sơ sinh thiếu men G6PD có nguy hiểm không?",
];

const WELCOME = {
  id: "welcome",
  role: "assistant",
  text: "Xin chào! Tôi là trợ lý sức khỏe chuyên về **thiếu men G6PD**.\n\nTôi có thể giúp bạn hiểu về triệu chứng, thực phẩm cần kiêng, thuốc cần tránh và cách quản lý bệnh. Hãy đặt câu hỏi hoặc chọn một gợi ý bên dưới.",
};

function formatText(text) {
  return text
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\n/g, "<br/>");
}

export default function App() {
  const [messages, setMessages] = useState([WELCOME]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  // Default open on desktop, closed on mobile
  const [sidebarOpen, setSidebarOpen] = useState(() => window.innerWidth >= 768);
  const bottomRef = useRef(null);
  const textareaRef = useRef(null);
  const hasUserMessages = messages.some((m) => m.role === "user");
  const isMobile = () => window.innerWidth < 768;

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  // Close sidebar on resize to mobile
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth < 768) setSidebarOpen(false);
    };
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  const closeSidebarOnMobile = () => {
    if (isMobile()) setSidebarOpen(false);
  };

  const sendMessage = async (text) => {
    const msg = (text || input).trim();
    if (!msg || loading) return;

    closeSidebarOnMobile();
    setMessages((prev) => [...prev, { id: Date.now(), role: "user", text: msg }]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: msg, session_id: sessionId }),
      });
      if (!res.ok) throw new Error();
      const data = await res.json();
      setSessionId(data.session_id);
      setMessages((prev) => [
        ...prev,
        { id: Date.now() + 1, role: "assistant", text: data.response },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { id: Date.now() + 1, role: "assistant", text: "Xin lỗi, đã xảy ra lỗi. Vui lòng thử lại.", error: true },
      ]);
    } finally {
      setLoading(false);
      textareaRef.current?.focus();
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleReset = () => {
    setMessages([WELCOME]);
    setSessionId(null);
    setInput("");
    closeSidebarOnMobile();
    textareaRef.current?.focus();
  };

  return (
    <div className="app">
      {/* Mobile overlay backdrop */}
      {sidebarOpen && (
        <div className="sidebar-overlay" onClick={() => setSidebarOpen(false)} />
      )}

      {/* Sidebar */}
      <aside className={`sidebar ${sidebarOpen ? "open" : "closed"}`}>
        <div className="sidebar-top">
          <div className="brand">
            <div className="brand-icon">G6</div>
            {sidebarOpen && <span className="brand-name">G6PD Assistant</span>}
          </div>
          <button
            className="toggle-btn"
            onClick={() => setSidebarOpen((v) => !v)}
            aria-label="Toggle sidebar"
          >
            {sidebarOpen ? "◀" : "▶"}
          </button>
        </div>

        {sidebarOpen && (
          <>
            <button className="new-chat-btn" onClick={handleReset}>
              + Cuộc hội thoại mới
            </button>

            <nav className="sidebar-nav">
              <p className="nav-label">Chủ đề phổ biến</p>
              <ul>
                {[
                  ["Thiếu men G6PD là gì?", "Tổng quan bệnh"],
                  ["Triệu chứng của thiếu men G6PD là gì?", "Triệu chứng"],
                  ["Người thiếu men G6PD cần kiêng ăn gì?", "Thực phẩm cần tránh"],
                  ["Thuốc nào cần tránh khi thiếu men G6PD?", "Thuốc cần tránh"],
                  ["Cách quản lý và sống chung với thiếu men G6PD?", "Quản lý bệnh"],
                ].map(([query, label]) => (
                  <li key={label} onClick={() => { sendMessage(query); closeSidebarOnMobile(); }}>
                    {label}
                  </li>
                ))}
              </ul>
            </nav>

            <div className="sidebar-footer">
              <p>Dữ liệu từ tài liệu y tế Bionet Việt Nam</p>
            </div>
          </>
        )}
      </aside>

      {/* Main */}
      <main className="main">
        <header className="topbar">
          <div className="topbar-left">
            {/* Hamburger — mobile only */}
            <button
              className="hamburger"
              onClick={() => setSidebarOpen((v) => !v)}
              aria-label="Open menu"
            >
              ☰
            </button>
            <div className="topbar-icon">G6</div>
            <div>
              <h1>Trợ lý sức khỏe G6PD</h1>
              <span className="status">
                <span className="status-dot" />
                Đang hoạt động
              </span>
            </div>
          </div>
          <button className="topbar-reset" onClick={handleReset}>
            Cuộc hội thoại mới
          </button>
        </header>

        <div className="feed">
          <div className="feed-inner">
            {messages.map((msg) => (
              <div key={msg.id} className={`msg ${msg.role}`}>
                {msg.role === "assistant" && (
                  <div className="msg-avatar">G6</div>
                )}
                <div className={`msg-content ${msg.error ? "error" : ""}`}>
                  {msg.role === "assistant" ? (
                    <div dangerouslySetInnerHTML={{ __html: formatText(msg.text) }} />
                  ) : (
                    msg.text
                  )}
                </div>
                {msg.role === "user" && <div className="msg-avatar user">Tu</div>}
              </div>
            ))}

            {loading && (
              <div className="msg assistant">
                <div className="msg-avatar">G6</div>
                <div className="msg-content typing">
                  <span /><span /><span />
                </div>
              </div>
            )}

            <div ref={bottomRef} />
          </div>

          {/* Suggested questions — only before first user message */}
          {!hasUserMessages && (
            <div className="suggestions">
              {SUGGESTED.map((q) => (
                <button key={q} className="suggestion-chip" onClick={() => sendMessage(q)}>
                  {q}
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
              onKeyDown={handleKeyDown}
              placeholder="Hỏi về thiếu men G6PD..."
              rows={1}
              disabled={loading}
            />
            <button
              className="send-btn"
              onClick={() => sendMessage()}
              disabled={!input.trim() || loading}
              aria-label="Gửi"
            >
              ↑
            </button>
          </div>
          <p className="composer-hint">
            Thông tin chỉ mang tính tham khảo, không thay thế tư vấn y tế chuyên nghiệp.
          </p>
        </div>
      </main>
    </div>
  );
}
