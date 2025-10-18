import { useState, useRef, useEffect, useContext } from "react";
import { ThemeContext } from "./_app";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8000";
const MODELS = [
  { value: "scamper", label: "Scamper (Fast)", icon: "🐎", color: "#ffd700" },
  { value: "gold buckle", label: "Gold Buckle", icon: "🏅", color: "#e6b800" },
  { value: "bodacious", label: "Bodacious", icon: "🐂", color: "#d70040" }
];

function LogoImg(props) {
  return (
    <span className="logo-img" {...props}>
      <object type="image/svg+xml" data="/logo.svg" style={{ width: "100%", height: "100%", verticalAlign: "middle" }}>
        <img src="/logo.png" alt="RodeoAI" style={{ width: "100%", height: "100%" }} />
      </object>
    </span>
  );
}

export default function Home() {
  const [chats, setChats] = useState([]);
  const [current, setCurrent] = useState(null);
  const [input, setInput] = useState("");
  const [model, setModel] = useState(MODELS[0].value);
  const threadRef = useRef(null);
  const { theme, setTheme } = useContext(ThemeContext);

  useEffect(() => {
    if (threadRef.current) threadRef.current.scrollTop = threadRef.current.scrollHeight;
  }, [current]);

  function startNewChat() {
    const c = { id: Date.now(), title: "New Chat", messages: [], model };
    setChats((cs) => [c, ...cs]);
    setCurrent(c);
  }
  function selectChat(id) {
    setCurrent(chats.find((c) => c.id === id));
  }
  async function sendMessage() {
    if (!input.trim()) return;
    let chat = current;
    if (!chat) {
      startNewChat();
      chat = current;
    }
    chat.messages.push({ role: "user", text: input });
    setChats([...chats]);
    const messageText = input;
    setInput("");
    const resp = await fetch(`${API_BASE}/chat/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: messageText, model }),
    });
    const data = await resp.json();
    chat.messages.push({ role: "assistant", text: data.reply, model });
    fetch(`${API_BASE}/analytics/log`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        chatId: chat.id,
        model,
        prompt: messageText,
        response: data.reply,
        timestamp: Date.now(),
      }),
    });
    if (chat.title === "New Chat" && chat.messages.length === 2)
      chat.title = messageText.length > 22 ? messageText.slice(0, 22) + "…" : messageText;
    setChats([...chats]);
  }
  function toggleTheme() {
    setTheme(theme === "dark" ? "light" : "dark");
  }

  return (
    <div>
      <aside className="sidebar">
        <div className="sidebar-header">
          <a
            href="#"
            className="new-chat"
            onClick={(e) => {
              e.preventDefault();
              startNewChat();
            }}
          >
            + New Chat
          </a>
        </div>
        <ul className="chat-list">
          {chats.map((chat) => (
            <li
              key={chat.id}
              className={current && chat.id === current.id ? "active" : ""}
              onClick={() => selectChat(chat.id)}
            >
              {chat.title}
            </li>
          ))}
        </ul>
      </aside>
      <main className="main">
        <header className="header">
          <LogoImg />
          <div>
            <h2 className="app-name">RODEO&nbsp;AI</h2>
            <span className="tagline">Powered by DataSpur</span>
          </div>
          <select
            className="model-switcher"
            value={model}
            onChange={(e) => setModel(e.target.value)}
            style={{ marginLeft: "1.2em" }}
          >
            {MODELS.map((m) => (
              <option key={m.value} value={m.value}>
                {m.icon} {m.label}
              </option>
            ))}
          </select>
          <button className="theme-toggle-btn" title="Toggle theme" onClick={toggleTheme}>
            {theme === "dark" ? "☀️ Light" : "🌑 Dark"}
          </button>
        </header>
        <div className="thread" ref={threadRef}>
          {!current || !current.messages.length ? (
            <div
              style={{
                textAlign: "center",
                color: "var(--text-muted)",
                marginTop: "2em",
              }}
            >
              <LogoImg
                style={{ width: 70, height: 70, opacity: 0.5, marginBottom: ".5em" }}
              />
              <br />
              <b>Welcome to RodeoAI</b>
              <br />
              Start a conversation to see answers here.
            </div>
          ) : (
            current.messages.map((msg, i) => {
              const mInfo =
                MODELS.find((m) => m.value === (msg.model || model)) || MODELS[0];
              return (
                <div
                  key={i}
                  className={"bubble " + msg.role}
                  style={
                    msg.role === "assistant"
                      ? { borderLeft: `4px solid ${mInfo.color}` }
                      : {}
                  }
                >
                  {msg.role === "assistant" && (
                    <span style={{ marginRight: 6, fontSize: "1.3em" }}>
                      {mInfo.icon}
                    </span>
                  )}
                  <span>{msg.text}</span>
                </div>
              );
            })
          )}
        </div>
        <div className="chat-input">
          <input
            type="text"
            placeholder="Type your message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                sendMessage();
                e.preventDefault();
              }
            }}
          />
          <button className="send" onClick={sendMessage} title="Send">
            ➤
          </button>
        </div>
      </main>
    </div>
  );
}
