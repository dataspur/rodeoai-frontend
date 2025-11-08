# RodeoAI Backend

FastAPI backend with OpenAI integration, PostgreSQL/SQLite database, user authentication, and chat history persistence.

## Quick Start

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY='sk-...'  # Required
export DATABASE_URL='sqlite:///./rodeoai.db'  # Optional, defaults to SQLite
export JWT_SECRET_KEY='your-secret-key'  # Optional, for production use

# Run the server
python main.py
```

Server will start on `http://localhost:8001` and database will be initialized automatically.

## API Endpoints

### Chat & Streaming
**POST /api/chat** - Main chat endpoint with streaming responses
- Body: `{messages: [{role, content}], model, conversation_id?, user_id?}`
- Returns: Streaming text with `X-Conversation-ID` header
- Rate limit: 30/minute
- Saves conversation and messages to database
- Personalizes responses based on user skill level

### Conversations
**GET /api/conversations** - List conversations
- Query: `user_id`, `limit`, `offset`
- Rate limit: 60/minute

**GET /api/conversations/{id}** - Get conversation with full message history
- Rate limit: 60/minute

**POST /api/conversations** - Create new conversation
- Body: `{title?, model?}`
- Rate limit: 30/minute

**PATCH /api/conversations/{id}** - Update conversation
- Body: `{title?, is_archived?}`
- Rate limit: 60/minute

**DELETE /api/conversations/{id}** - Delete conversation
- Rate limit: 30/minute

**GET /api/conversations/search** - Search conversations
- Query: `q` (search term), `user_id?`, `limit?`
- Rate limit: 30/minute

### Export
**GET /api/conversations/{id}/export/text** - Export as plain text
- Returns: Text file download
- Rate limit: 20/minute

**GET /api/conversations/{id}/export/pdf** - Export as PDF
- Returns: PDF file download
- Rate limit: 10/minute

### Users
**GET /api/users/{id}** - Get user profile
- Rate limit: 60/minute

**PATCH /api/users/{id}** - Update user profile
- Body: `{full_name?, skill_level?, preferences?}`
- Skill levels: `beginner`, `intermediate`, `advanced`, `professional`
- Rate limit: 30/minute

### Feedback
**POST /api/feedback** - Submit feedback
- Body: `{message_id?, feedback: 'positive'|'negative', message, timestamp, comment?}`
- Rate limit: 60/minute

### Authentication
**POST /api/auth/google** - Google OAuth login
- Body: `{token: string}`
- Returns: `{access_token, token_type, user}`
- Rate limit: 10/minute

**GET /api/auth/me** - Get current user (requires JWT)
- Headers: `Authorization: Bearer <token>`
- Rate limit: 60/minute

### Health
**GET /health** - Health check
- Returns: `{status, openai_configured}`
- Rate limit: 100/minute

**GET /** - Root endpoint
- Rate limit: 100/minute

## Environment Variables

Required:
- `OPENAI_API_KEY` - Your OpenAI API key from platform.openai.com

Optional:
- `DATABASE_URL` - Database connection string (defaults to SQLite)
  - SQLite: `sqlite:///./rodeoai.db`
  - PostgreSQL: `postgresql://user:password@localhost/rodeoai`
- `JWT_SECRET_KEY` - Secret key for JWT tokens (change in production!)
- `GOOGLE_CLIENT_ID` - Google OAuth client ID
- `GOOGLE_CLIENT_SECRET` - Google OAuth client secret
- `GOOGLE_REDIRECT_URI` - OAuth redirect URI (default: `http://localhost:3000/auth/callback`)

## Testing

```bash
# Health check
curl http://localhost:8001/health

# Test chat with streaming
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Hello"}], "model": "gpt-4o-mini"}'

# List conversations
curl http://localhost:8001/api/conversations

# Search conversations
curl "http://localhost:8001/api/conversations/search?q=heading"

# Export conversation
curl http://localhost:8001/api/conversations/1/export/text -o chat.txt
```

## Dependencies

Core:
- fastapi==0.104.1 - Web framework
- uvicorn==0.24.0 - ASGI server
- pydantic==2.5.0 - Data validation
- openai==1.3.0 - OpenAI API client

Database:
- sqlalchemy==2.0.23 - ORM
- psycopg2-binary==2.9.9 - PostgreSQL adapter
- alembic==1.12.1 - Database migrations

Security & Auth:
- slowapi==0.1.9 - Rate limiting
- python-jose[cryptography]==3.3.0 - JWT tokens
- passlib[bcrypt]==1.7.4 - Password hashing
- authlib==1.3.0 - OAuth support

Utilities:
- python-multipart==0.0.6 - Form data parsing
- reportlab==4.0.7 - PDF generation
- itsdangerous==2.1.2 - Secure signing

## Configuration

**Port:** 8001 (configured in main.py line 113)

**CORS:** Enabled for all origins (configured for development)

**Model Mapping:**
- `gpt-4o-mini` → gpt-4o-mini
- `gpt-4o` → gpt-4o
- `o1` → gpt-4o (fallback)

## Development

The backend includes:
- Streaming response support
- System message for rodeo expertise context
- Error handling for missing API keys
- Request validation with Pydantic models
- CORS middleware for frontend access

## Production Notes

For production deployment:
1. Update CORS origins to match your frontend domain
2. Use environment variables for configuration
3. Consider using gunicorn with uvicorn workers
4. Set up proper logging and monitoring
5. Implement rate limiting if needed
