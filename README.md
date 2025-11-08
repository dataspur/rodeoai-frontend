# RodeoAI - Functional Frontend & Backend

This project provides a complete AI-powered chat interface for rodeo expertise, with both a Next.js frontend and a standalone HTML version, powered by a FastAPI backend using OpenAI's API.

## Project Structure

```
rodeoai-frontend/
├── pages/               # Next.js frontend (React-based)
│   ├── index.js        # Main chat interface
│   └── _app.js         # App wrapper with theme context
├── components/          # React components
├── public/
│   ├── index.html      # Standalone HTML version (no build required)
│   └── logo.png        # RodeoAI logo
└── styles/             # CSS styles

Desktop/rodeoai-backend/
├── main.py             # FastAPI backend with OpenAI integration
└── requirements.txt    # Python dependencies
```

## Quick Start

### Option 1: Standalone HTML Frontend (Simplest)

This is the easiest way to run RodeoAI without any build steps.

1. **Set up the backend:**
```bash
cd ~/Desktop/rodeoai-backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set your OpenAI API key
export OPENAI_API_KEY='your-api-key-here'  # On Windows: set OPENAI_API_KEY=your-api-key-here

# Run the backend
python main.py
```

The backend will start on `http://localhost:8001`

2. **Open the frontend:**
```bash
# In a new terminal, navigate to the frontend directory
cd ~/rodeoai-frontend

# Open the standalone HTML file in your browser
# On Linux:
xdg-open public/index.html
# On macOS:
open public/index.html
# On Windows:
start public/index.html
```

That's it! The HTML frontend will automatically connect to the backend at `http://localhost:8001`.

### Option 2: Next.js Frontend (Full Development Environment)

For a more feature-rich development experience with React.

1. **Set up the backend** (same as above)

2. **Set up the Next.js frontend:**
```bash
cd ~/rodeoai-frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```

The Next.js app will start on `http://localhost:3000`

## Backend API Details

### Endpoints

**POST /api/chat**
- Accepts an array of messages with role and content
- Streams back AI responses in real-time
- Request format:
```json
{
  "messages": [
    {"role": "user", "content": "How do I improve my heading?"}
  ],
  "model": "gpt-4o-mini"
}
```

**GET /health**
- Health check endpoint
- Returns OpenAI client status

**GET /**
- Root endpoint
- Returns service status

### Supported Models

The backend maps these model names:
- `gpt-4o-mini` → OpenAI's gpt-4o-mini
- `gpt-4o` → OpenAI's gpt-4o
- `o1` → Falls back to gpt-4o (o1 not yet available via API)

### Environment Variables

- `OPENAI_API_KEY` (required) - Your OpenAI API key

## Features

### Frontend Features (Quick Wins ✅)
- **Real-time streaming responses** with typing indicators
- **Dark/light theme toggle** with localStorage persistence
- **Copy to clipboard** button for AI responses
- **Regenerate response** functionality
- **Message editing** - edit and resend your questions
- **Feedback buttons** (thumbs up/down) on AI responses
- **Keyboard shortcuts** - Ctrl+Enter to send messages
- Message history maintained in conversation
- Clean, modern UI with rodeo branding
- Model selection (Scamper/gpt-4o-mini, Gold Buckle/gpt-4o, Bodacious/o1)
- Responsive design with smooth animations
- Auto-scroll to latest messages
- Error handling with user-friendly toast notifications

### Backend Features (High Priority ✅)
#### Chat & Streaming
- Streaming responses using OpenAI's Chat Completions API
- Conversation context maintained across messages
- CORS enabled for cross-origin requests
- Proper error handling with detailed logging

#### Database & Persistence
- **PostgreSQL/SQLite support** with SQLAlchemy ORM
- **Conversation history** saved to database
- **Resume conversations** across sessions
- **Search conversations** by title or content
- **Export chat history** to PDF or plain text
- Automatic conversation titling from first message

#### User Management
- **User profiles** with customizable preferences
- **Skill level settings** (beginner, intermediate, advanced, professional)
- **Personalized AI responses** based on user skill level
- User preferences stored as JSON for flexibility

#### Rate Limiting & Security
- **Rate limiting** on all endpoints (using slowapi)
- JWT-based authentication
- OAuth support structure (Google OAuth ready)
- Secure password hashing with bcrypt

#### Feedback & Analytics
- **User feedback collection** (thumbs up/down)
- Feedback stored with message references
- Token usage tracking for cost analysis

## API Endpoints

### Chat
- `POST /api/chat` - Send message and get streaming response
  - Body: `{messages: [{role, content}], model, conversation_id?, user_id?}`
  - Returns: Streaming text response
  - Headers: `X-Conversation-ID` with the conversation ID

### Conversations
- `GET /api/conversations` - List all conversations
  - Query params: `user_id`, `limit`, `offset`
- `GET /api/conversations/{id}` - Get specific conversation with messages
- `POST /api/conversations` - Create new conversation
- `PATCH /api/conversations/{id}` - Update conversation (title, archive)
- `DELETE /api/conversations/{id}` - Delete conversation
- `GET /api/conversations/search?q=query` - Search conversations

### Export
- `GET /api/conversations/{id}/export/text` - Export as plain text
- `GET /api/conversations/{id}/export/pdf` - Export as PDF

### Users
- `GET /api/users/{id}` - Get user profile
- `PATCH /api/users/{id}` - Update user profile
  - Body: `{full_name?, skill_level?, preferences?}`

### Feedback
- `POST /api/feedback` - Submit feedback on a response
  - Body: `{message_id, feedback: 'positive'|'negative', comment?}`

### Authentication
- `POST /api/auth/google` - Authenticate with Google OAuth
- `GET /api/auth/me` - Get current user info (requires JWT token)

### Health
- `GET /health` - Health check endpoint
- `GET /` - Root endpoint

All endpoints have rate limiting. See main.py:108-644 for details.

## Testing the Connection

1. Start the backend as described above
2. Open the frontend (either standalone HTML or Next.js)
3. Look for the connection status indicator
4. Try sending a message like "How do I improve my heading technique?"
5. You should see a streaming response with typing indicator
6. Try the new features:
   - Toggle theme with the sun/moon button
   - Copy responses with the copy button
   - Regenerate responses
   - Edit your messages
   - Give feedback with thumbs up/down

### Troubleshooting

**Backend won't start:**
- Make sure you have Python 3.8+ installed
- Check that OPENAI_API_KEY is set: `echo $OPENAI_API_KEY`
- Verify dependencies are installed: `pip list | grep fastapi`

**Frontend can't connect:**
- Verify backend is running on port 8001
- Check browser console for errors (F12 → Console)
- Ensure no firewall is blocking localhost:8001

**No AI responses:**
- Check backend terminal for error messages
- Verify OpenAI API key is valid
- Check your OpenAI account has credits available
- Test backend directly: `curl http://localhost:8001/health`

**CORS errors:**
- The backend has CORS enabled for all origins
- If issues persist, check browser console for specific CORS errors

## Production Deployment

### Backend
The backend can be deployed to any platform that supports Python:
- Update CORS origins in `main.py` to match your frontend domain
- Set OPENAI_API_KEY environment variable
- Use a production ASGI server (uvicorn is included)
- Consider using gunicorn for better production performance

### Frontend (Standalone HTML)
The standalone HTML file can be:
- Served from any static hosting (Netlify, Vercel, GitHub Pages)
- Update the API_BASE URL in the HTML if backend is on a different domain
- No build step required

### Frontend (Next.js)
For the Next.js version:
```bash
npm run build
npm start
```
Or deploy to Vercel/Netlify/other platforms that support Next.js

## Development

### Backend Development
The backend uses:
- FastAPI for the web framework
- OpenAI Python SDK for AI integration
- Pydantic for request validation
- Uvicorn as the ASGI server

### Frontend Development
The standalone HTML uses vanilla JavaScript with:
- Fetch API for HTTP requests
- Streaming response handling with ReadableStream
- Modern CSS with CSS variables for theming

The Next.js frontend uses:
- React 18
- Next.js 14
- Context API for theme management

## Cost Considerations

This application uses OpenAI's API, which charges per token:
- gpt-4o-mini: ~$0.15 per million input tokens, ~$0.60 per million output tokens
- gpt-4o: ~$5 per million input tokens, ~$15 per million output tokens

Each chat message consumes tokens based on the conversation history length. Monitor your usage at platform.openai.com.

## License

This is a custom application for RodeoAI. All rights reserved.
