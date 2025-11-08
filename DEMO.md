# 🎪 RodeoAI Demo Guide

## ✅ Backend is Running!

The backend server is now running on **http://localhost:8001**

- Status: ✓ Healthy
- Database: ✓ Initialized (SQLite at `Desktop/rodeoai-backend/rodeoai.db`)
- OpenAI: ⚠️ Not configured (set `OPENAI_API_KEY` to enable AI chat)

## 🚀 Quick Start - Try the Frontend

### Option 1: Open the Standalone HTML (Easiest!)

1. Navigate to the frontend directory:
   ```bash
   cd /home/user/rodeoai-frontend
   ```

2. Open `public/index.html` in your browser:
   - **Linux:** `xdg-open public/index.html`
   - **macOS:** `open public/index.html`
   - **Windows:** `start public/index.html`
   - Or just drag the file into your browser

The frontend will automatically connect to the backend at `http://localhost:8001`!

## 🎯 Demo Features - Try These!

### 1. **Theme Toggle** ☀️🌙
- **Where:** Top-right corner moon button
- **Try it:** Click to switch between dark and light themes
- **Check:** Close and reopen the page - your theme preference is saved!

### 2. **Send a Message** 💬
- **Where:** Bottom input area
- **Try it:** Type "How do I improve my heading technique?"
- **See:** Typing indicator (three bouncing dots) while AI responds
- **Note:** You'll need to set `OPENAI_API_KEY` for real AI responses

### 3. **Copy Response** 📋
- **Where:** Hover over any AI message
- **Try it:** Click the "Copy" button
- **See:** Toast notification "Copied to clipboard!"

### 4. **Regenerate Response** 🔄
- **Where:** Hover over any AI message
- **Try it:** Click "Regenerate" button
- **See:** AI generates a new response to the same question

### 5. **Edit Message** ✏️
- **Where:** Hover over YOUR messages
- **Try it:** Click "Edit" button
- **See:** Message appears in input box - edit and press Enter to resend

### 6. **Feedback Buttons** 👍👎
- **Where:** Hover over any AI message
- **Try it:** Click thumbs up or thumbs down
- **See:** Toast notification "Thanks for the feedback!"
- **Backend:** Feedback is saved to the database

### 7. **Keyboard Shortcuts** ⌨️
- **Try:** Press `Ctrl+Enter` (or `Cmd+Enter` on Mac) to send message
- **Try:** Press `Shift+Enter` to add a new line in your message
- **Try:** Regular `Enter` also sends (when not holding Shift)

### 8. **Responsive UI** 🎨
- **Try:** Click the hamburger menu (☰) to collapse the sidebar
- **Try:** Resize your browser window - UI adapts!
- **Notice:** Smooth animations and transitions everywhere

## 🔧 Backend API Demo

The backend has 15+ new endpoints. Try these with curl:

```bash
# Health check
curl http://localhost:8001/health

# List all conversations (will be empty at first)
curl http://localhost:8001/api/conversations

# Create a new conversation
curl -X POST http://localhost:8001/api/conversations \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Conversation", "model": "gpt-4o-mini"}'

# Search conversations (after you have some)
curl "http://localhost:8001/api/conversations/search?q=heading"
```

## 💾 Database Features

All conversations are automatically saved to:
```
/home/user/rodeoai-frontend/Desktop/rodeoai-backend/rodeoai.db
```

### Check the Database:
```bash
cd ~/Desktop/rodeoai-backend
sqlite3 rodeoai.db "SELECT * FROM conversations;"
sqlite3 rodeoai.db "SELECT * FROM messages LIMIT 5;"
```

### Export Conversations:
```bash
# Export conversation #1 as text
curl http://localhost:8001/api/conversations/1/export/text -o chat.txt

# Export as PDF
curl http://localhost:8001/api/conversations/1/export/pdf -o chat.pdf
```

## 🎨 Theme Customization

The frontend uses CSS variables for easy theming. Check these out in `public/index.html`:

**Dark Theme Colors:**
- Background: `#212121`
- Accent: `#d4af37` (Rodeo gold)
- Text: `#ececec`

**Light Theme Colors:**
- Background: `#ffffff`
- Accent: `#d4af37` (same gold)
- Text: `#1a1a1a`

## 🔐 User Features (Backend Ready)

The backend supports user profiles and personalization:

```bash
# Update user profile (user_id = 1)
curl -X PATCH http://localhost:8001/api/users/1 \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Professional Roper",
    "skill_level": "professional",
    "preferences": {"favorite_event": "team_roping"}
  }'

# Get user profile
curl http://localhost:8001/api/users/1
```

**Skill Levels Available:**
- `beginner` - New to rodeo
- `intermediate` - Some experience
- `advanced` - Experienced competitor
- `professional` - Pro level

The AI personalizes responses based on your skill level!

## 📊 Rate Limiting

All endpoints have rate limits to prevent abuse:

- Chat endpoint: 30 requests/minute
- Conversations: 60 requests/minute
- Export PDF: 10 requests/minute
- OAuth login: 10 requests/minute

Try making rapid requests to see rate limiting in action:
```bash
for i in {1..35}; do curl http://localhost:8001/health; done
```

## 🎬 Full Demo Walkthrough

1. **Open the frontend** in your browser
2. **Toggle theme** - See smooth transition
3. **Type a test message** - Watch typing indicator
4. **Try all action buttons** on messages:
   - Copy
   - Regenerate
   - Edit (on your messages)
   - Thumbs up/down
5. **Use keyboard shortcuts** - Ctrl+Enter to send
6. **Check localStorage** in browser DevTools:
   - Open DevTools (F12)
   - Go to Application → Local Storage
   - See `rodeoai-theme` stored

## 🔑 Enable Full AI Chat

To enable actual AI responses, set your OpenAI API key:

```bash
cd ~/Desktop/rodeoai-backend
export OPENAI_API_KEY='sk-your-key-here'
python main.py
```

Then try a real rodeo question:
- "What's the best rope length for heading?"
- "How do I improve my swing?"
- "Tell me about breakaway roping techniques"

## 📱 Next Steps

Want to see more? Try:

1. **Create multiple conversations** - See them in the sidebar
2. **Search past conversations** - Use the search endpoint
3. **Export a conversation** - Download as PDF or text
4. **Test rate limiting** - Make rapid API calls
5. **Inspect the database** - Look at saved conversations
6. **Set up OAuth** - Configure Google login (requires GOOGLE_CLIENT_ID)

## 🛑 Stop the Demo

When you're done:

```bash
# Stop the backend server
# Find the process
ps aux | grep "python main.py"

# Or just press Ctrl+C in the terminal where it's running
```

---

**Enjoy exploring RodeoAI!** 🤠🐴
