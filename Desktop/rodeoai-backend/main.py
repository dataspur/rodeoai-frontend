from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import sys

# Import scraping routes
from routes.scraping import router as scraping_router

app = FastAPI(
    title="RodeoAI API",
    description="AI Chat and Social Media Scraping API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = None
try:
    from openai import OpenAI
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        client = OpenAI(api_key=api_key)
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)

class ChatRequest(BaseModel):
    message: str
    model: str = "scamper"

# Include scraping routes
app.include_router(scraping_router)


@app.get("/")
def root():
    return {"status": "ok", "version": "1.0.0"}

@app.post("/api/chat/")
async def chat(request: ChatRequest):
    if not client:
        raise HTTPException(status_code=500, detail="Client not ready")
    
    models = {
        "scamper": "gpt-4o-mini",
        "gold_buckle": "gpt-4o",
        "bodacious": "gpt-4o"
    }
    model = models.get(request.model, "gpt-4o-mini")
    
    prompts = {
        "scamper": "You are Scamper, a fast rodeo AI.",
        "gold_buckle": "You are Gold Buckle, a balanced rodeo expert.",
        "bodacious": "You are Bodacious, a premium rodeo AI."
    }
    system = prompts.get(request.model, "You are a rodeo AI.")
    
    async def generate():
        with client.messages.stream(
            model=model,
            max_tokens=1024,
            system=system,
            messages=[{"role": "user", "content": request.message}]
        ) as stream:
            for text in stream.text_stream:
                yield f"data: {text}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
