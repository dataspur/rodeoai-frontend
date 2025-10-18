import { useContext, useState } from "react";
import { ThemeContext } from "../pages/_app";

export default function SettingsDrawer({ open, onClose, user, setUser, model, setModel, chats, setChats }) {
  const { theme, setTheme } = useContext(ThemeContext);
  const [allowTrain, setAllowTrain] = useState(user?.allowTrain ?? true);

  function clearChats() {
    if (window.confirm("Delete all conversations? This cannot be undone.")) setChats([]);
  }

  function exportChats() {
    const blob = new Blob([JSON.stringify(chats, null, 2)], {type:"application/json"});
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "rodeoai_chats.json";
    a.click();
  }

  function logout() {
    setUser(null);
    onClose();
  }

  function toggleAllowTrain(val) {
    setAllowTrain(val);
    setUser(u => ({ ...u, allowTrain: val }));
    // send to backend if needed
  }

  if (!open) return null;

  return (
    <div className="settings-drawer">
      <div className="drawer-header">
        <span>⚙️ Settings</span>
        <button onClick={onClose} className="close-btn">✖</button>
      </div>
      <div className="drawer-section">
        <b>Profile</b>
        <div className="profile-row">
          <img src={user?.avatar || "/default-avatar.png"} alt="avatar" className="avatar" />
          <div>
            <div>{user?.username || "User"}</div>
            <div style={{fontSize:"0.8em", color:"var(--text-muted)"}}>{user?.email || "—"}</div>
            <div style={{fontSize:"0.75em", color:"var(--primary)"}}>Plan: Free Tier</div>
          </div>
        </div>
      </div>
      <div className="drawer-section">
        <b>Appearance</b>
        <div>
          <label>Theme:</label>
          <select value={theme} onChange={e => setTheme(e.target.value)}>
            <option value="system">System</option>
            <option value="dark">Dark</option>
            <option value="light">Light</option>
          </select>
        </div>
        <div>
          <label>Font size:</label>
          <select defaultValue="default" onChange={e => {
            document.body.style.fontSize = e.target.value === "large" ? "1.18em" : "";
          }}>
            <option value="default">Default</option>
            <option value="large">Large</option>
          </select>
        </div>
      </div>
      <div className="drawer-section">
        <b>Preferences</b>
        <div>
          <label>Default Model:</label>
          <select value={model} onChange={e => setModel(e.target.value)}>
            <option value="scamper">🐎 Scamper</option>
            <option value="gold buckle">🏅 Gold Buckle</option>
            <option value="bodacious">🐂 Bodacious</option>
          </select>
        </div>
        <div>
          <input type="checkbox" checked={allowTrain}
                 onChange={e => toggleAllowTrain(e.target.checked)} id="allow-train"/>
          <label htmlFor="allow-train" style={{marginLeft:8}}>
            Allow my chats to help improve RodeoAI
          </label>
          <div style={{fontSize:"0.75em",color:"var(--text-muted)"}}>
            Uncheck to opt out of data for model improvement (see <a href="/privacy" target="_blank">privacy policy</a>).
          </div>
        </div>
      </div>
      <div className="drawer-section">
        <b>Data & Privacy</b>
        <button onClick={exportChats} className="drawer-btn">Download Conversations</button>
        <button onClick={clearChats} className="drawer-btn">Clear All Conversations</button>
      </div>
      <div className="drawer-section">
        <b>Account</b>
        <button onClick={logout} className="drawer-btn">Sign Out</button>
      </div>
      <div className="drawer-section" style={{fontSize:"0.92em",color:"var(--text-muted)"}}>
        <b>Shortcuts:</b> <br/>
        <kbd>⏎</kbd> Send, <kbd>Shift+⏎</kbd> New Line, <kbd>/</kbd> Quick Switch Model
      </div>
      <style jsx>{`
        .settings-drawer {
          position:fixed; top:0; right:0; width:340px; height:100%;
          background:var(--panel);
          box-shadow: -6px 0 18px 0 rgba(0,0,0,0.17);
          z-index:1002;
          padding:0 0 24px 0;
          overflow-y:auto;
          transition: right 0.3s cubic-bezier(.7,.2,.17,1);
        }
        .drawer-header {
          padding:1.2em 1.3em .6em 1.3em;
          display:flex;
          justify-content:space-between;
          align-items:center;
        }
        .close-btn {
          background:none;
          border:none;
          color:var(--primary);
          font-size:1.2em;
          cursor:pointer;
        }
        .drawer-section {
          padding:1.1em 1.4em 0 1.4em;
        }
        .profile-row {
          display:flex;
          align-items:center;
          gap:14px;
          margin-top:.5em;
        }
        .avatar {
          width:52px;
          height:52px;
          border-radius:50%;
          border:2px solid var(--primary);
        }
        .drawer-btn {
          display:block;
          margin-top:.7em;
          width:100%;
          background:var(--primary);
          color:var(--bg);
          border:none;
          border-radius:8px;
          font-weight:bold;
          padding:.68em 0;
          margin-bottom:5px;
          cursor:pointer;
        }
      `}</style>
    </div>
  );
}
