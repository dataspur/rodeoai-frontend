# RodeoAI Backend

FastAPI backend with OpenAI integration for the RodeoAI chat interface.

## Quick Start

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set your OpenAI API key
export OPENAI_API_KEY='sk-...'  # On Windows: set OPENAI_API_KEY=sk-...

# Run the server
python main.py
```

Server will start on `http://localhost:8001`

## API Endpoints

### POST /api/chat
Streaming chat endpoint that accepts message history and returns AI responses.

**Request:**
```json
{
  "messages": [
    {"role": "user", "content": "How do I improve my heading?"}
  ],
  "model": "gpt-4o-mini"
}
```

**Response:**
Streams text/plain content as it's generated.

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "openai_configured": true
}
```

### GET /
Root endpoint returning service status.

## Environment Variables

- `OPENAI_API_KEY` (required) - Your OpenAI API key from platform.openai.com

## Testing

```bash
# Health check
curl http://localhost:8001/health

# Test chat (non-streaming)
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Hello"}], "model": "gpt-4o-mini"}'
```

## Dependencies

- fastapi==0.104.1 - Web framework
- uvicorn==0.24.0 - ASGI server
- pydantic==2.5.0 - Data validation
- openai==1.3.0 - OpenAI API client
- python-multipart==0.0.6 - Form data parsing

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
