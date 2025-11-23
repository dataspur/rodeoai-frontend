import { useState, useRef, useEffect, useContext } from 'react';
import { ThemeContext } from './_app';
import SettingsDrawer from '../components/SettingsDrawer';

// Determine the base URL for the API.  You can set NEXT_PUBLIC_API_BASE
// in your Vercel/Netlify environment to override the default.
const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://127.0.0.1:8000';

// Define the available models with icons and colours.  These options
// populate the model switcher and drive colouring of assistant replies.
const MODELS = [
  { value: 'scamper', label: 'Scamper (Fast)', icon: '🐎', color: '#ffd700' },
  { value: 'gold buckle', label: 'Gold Buckle', icon: '🏅', color: '#e6b800' },
  { value: 'bodacious', label: 'Bodacious', icon: '🐂', color: '#d70040' }
];

// Base64 encoded logo (unused now, kept for reference)
const logoBase64 =
  'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAfQAAAH0CAYAAADL1t+KAAEAAElEQVR4nOzdd3gUVRfA4d/M7G42PZTQ' +
  'exMISIfQkSadICAdEVGRKkVBBAFBBISPJkVQRDqICIqggPQSmhTpvbdQ0rNtZr4/JqEoJYR07/s8PGgy' +
  'wEAnIiJSAQY6ERGRCjDQiYiIVICBTkREpAIMdCIiIhVgoBMREakAA52IiEgF/g9aCReFVLr9LwAAAABJ' +
  'RU5ErkJggg==';

// Use external logo file instead of base64 for crisp rendering and branding
const logoSrc = '/logo.png';

// Component to render the logo.  
function LogoImg(props) {
  return (
    <img
      src={logoSrc}
      alt="Rodeo AI"
      className="logo-img"
      style={{ width: '100%', height: '100%', verticalAlign: 'middle' }}
      {...props}
    />
  );
}

export default function Home() {
  const [chats, setChats] = useState([]);
  const [current, setCurrent] = useState(null);
  const [input, setInput] = useState('');
  const [model, setModel] = useState(MODELS[0].value);
  const threadRef = useRef(null);
  const { theme, setTheme } = useContext(ThemeContext);
  const [settingsOpen, setSettingsOpen] = useState(false);
  // Placeholder user state; extend when OAuth is added.
  const [user, setUser] = useState(null);

  // Ensure the chat scrolls to the latest message whenever current chat updates.
  useEffect(() => {
    if (threadRef.current) {
      threadRef.current.scrollTop = threadRef.current.scrollHeight;
    }
  }, [current]);

  // Start a new chat by creating a conversation object and prepending to the list.
  function startNewChat() {
    const c = { id: Date.now(), title: 'New Chat', messages: [], model };
    setChats(cs => [c, ...cs]);
    setCurrent(c);
  }

  // Select an existing chat from the sidebar.
  function selectChat(id) {
    setCurrent(chats.find(c => c.id === id));
  }

  // Send the specified text (or the current input if none provided) to the backend
  // and append the reply to the conversation.  This helper is used both for
  // manual input and for sending pre-defined suggestion prompts.  It accepts an
  // optional `customText` parameter to override the input state.
  async function sendMessage(customText) {
    const textToSend = customText !== undefined ? customText : input;
    if (!textToSend.trim()) return;
    let chat = current;
    if (!chat) {
      startNewChat();
      chat = current;
    }
    chat.messages.push({ role: 'user', text: textToSend });
    setChats([...chats]);
    if (customText === undefined) {
      setInput('');
    }
    try {
      const resp = await fetch(`${API_BASE}/chat/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: textToSend, model })
      });
      const data = await resp.json();
      chat.messages.push({ role: 'assistant', text: data.reply, model });
      // Fire and forget analytics logging.
      fetch(`${API_BASE}/analytics/log`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          chatId: chat.id,
          model,
          prompt: textToSend,
          response: data.reply,
          timestamp: Date.now()
        })
      });
      // If this was the first assistant reply, rename the chat using the first user message.
      if (chat.title === 'New Chat' && chat.messages.length === 2) {
        chat.title = textToSend.length > 22 ? `${textToSend.slice(0, 22)}…` : textToSend;
      }
      setChats([...chats]);
    } catch (err) {
      console.error(err);
    }
  }

  // Toggle between dark and light themes.
  function toggleTheme() {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  }

  return (
    <div>
      {/* Sidebar with new chat button and existing conversations */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <a href="#" className="new-chat" onClick={e => { e.preventDefault(); startNewChat(); }}>+ New Chat</a>
        </div>
        <ul className="chat-list">
          {chats.map(chat => (
            <li key={chat.id}
                className={current && chat.id === current.id ? 'active' : ''}
                onClick={() => selectChat(chat.id)}>
              {chat.title}
            </li>
          ))}
        </ul>
        <a href="/scrape" className="nav-link">
          🔍 Social Scraper
        </a>
      </aside>

      {/* Main chat area */}
      <main className="main">
        <header className="header">
          <LogoImg />
          <div>
            <h2 className="app-name">RODEO&nbsp;AI</h2>
            <span className="tagline">Expert rodeo insights, powered by AI.</span>
          </div>
          <select className="model-switcher" value={model} onChange={e => setModel(e.target.value)} style={{ marginLeft: '1.2em' }}>
            {MODELS.map(m => (
              <option key={m.value} value={m.value}>
                {m.icon} {m.label}
              </option>
            ))}
          </select>
          <button className="theme-toggle-btn" title="Toggle theme" onClick={toggleTheme}>
            {theme === 'dark' ? '☀️' : '🌑'}
          </button>
          <button className="settings-btn" onClick={() => setSettingsOpen(true)} style={{ marginLeft: '0.8em', background: 'none', border: 'none', color: 'var(--primary)', fontSize: '1.2em', cursor: 'pointer' }}>
            ⚙️
          </button>
        </header>
        <div className="thread" ref={threadRef}>
          {(!current || !current.messages.length) ? (
            <div style={{ textAlign: 'center', color: 'var(--text-light)', marginTop: '2em' }}>
              {/* Welcome section with logo and suggestion prompts */}
              <div className="welcome">
                <div className="welcome-logo">
                  <img src={logoSrc} alt="Rodeo AI" style={{ width: 96, height: 96 }} />
                </div>
                <h2 style={{ fontSize: '2.25rem', fontWeight: '700', marginBottom: '0.75rem', color: 'var(--primary)' }}>
                  Welcome to RodeoAI
                </h2>
                <p className="welcome-subtitle" style={{ color: 'var(--text-muted)', fontSize: '1rem', marginBottom: '3rem' }}>
                  Expert rodeo insights, powered by AI.
                </p>
                <div className="suggestions-grid">
                  {['Improve my heading technique', 'Best rope for heeling', 'Train my horse smarter', 'Strategy for NFR'].map((s, idx) => (
                    <div
                      key={idx}
                      className="suggestion-card"
                      onClick={() => sendMessage(s)}
                    >
                      {s}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : current.messages.map((msg, i) => {
            const mInfo = MODELS.find(m => m.value === (msg.model || model)) || MODELS[0];
            return (
              <div key={i} className={'bubble ' + msg.role} style={msg.role === 'assistant' ? { borderLeft: `4px solid ${mInfo.color}` } : {}}>
                {msg.role === 'assistant' && <span style={{ marginRight: 6, fontSize: '1.3em' }}>{mInfo.icon}</span>}
                <span>{msg.text}</span>
              </div>
            );
          })}
        </div>
        <div className="chat-input">
          <input type="text"
                 placeholder="Type your message..."
                 value={input}
                 onChange={e => setInput(e.target.value)}
                 onKeyDown={e => {
                   if (e.key === 'Enter' && !e.shiftKey) {
                     sendMessage();
                     e.preventDefault();
                   }
                 }}
          />
          <button className="send" onClick={sendMessage} title="Send">&#x27A4;</button>
        </div>
      </main>
      {/* Slide-in settings drawer */}
      <SettingsDrawer
        open={settingsOpen}
        onClose={() => setSettingsOpen(false)}
        user={user}
        setUser={setUser}
        model={model}
        setModel={setModel}
        chats={chats}
        setChats={setChats}
      />
    </div>
  );
}
