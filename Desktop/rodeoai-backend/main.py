from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import os
import sys
import json

app = FastAPI()

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
client = None
try:
    from openai import OpenAI
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        client = OpenAI(api_key=api_key)
        print("✓ OpenAI client initialized", file=sys.stderr)
    else:
        print("⚠ OPENAI_API_KEY not set", file=sys.stderr)
except Exception as e:
    print(f"Error initializing OpenAI: {e}", file=sys.stderr)

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    model: str = "gpt-4o-mini"

@app.get("/")
def root():
    return {"status": "ok", "service": "RodeoAI Backend"}

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "openai_configured": client is not None
    }

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    Chat endpoint that accepts messages array and streams back responses.
    Compatible with the HTML frontend.
    """
    if not client:
        raise HTTPException(
            status_code=500,
            detail="OpenAI client not initialized. Please set OPENAI_API_KEY environment variable."
        )

    # Map friendly model names to OpenAI model IDs
    model_mapping = {
        "gpt-4o-mini": "gpt-4o-mini",
        "gpt-4o": "gpt-4o",
        "o1": "gpt-4o",  # o1 is not available via API yet, fallback to gpt-4o
    }

    model_id = model_mapping.get(request.model, "gpt-4o-mini")

    # Convert Pydantic models to dicts for OpenAI API
    messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]

    # Add system message for rodeo context
    system_message = {
        "role": "system",
        "content": "You are RodeoAI, an expert assistant for team roping, rodeo techniques, equipment, and training. Provide helpful, accurate advice to rodeo athletes."
    }
    messages.insert(0, system_message)

    async def generate():
        """Stream responses from OpenAI"""
        try:
            stream = client.chat.completions.create(
                model=model_id,
                messages=messages,
                stream=True,
                max_tokens=2000,
                temperature=0.7,
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(error_msg, file=sys.stderr)
            yield error_msg

    return StreamingResponse(
        generate(),
        media_type="text/plain"
    )

if __name__ == "__main__":
    import uvicorn
    print("Starting RodeoAI Backend on http://0.0.0.0:8001")
    print("Make sure OPENAI_API_KEY is set in your environment")
    uvicorn.run(app, host="0.0.0.0", port=8001)
