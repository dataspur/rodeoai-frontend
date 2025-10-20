from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except:
    client = None

class ChatRequest(BaseModel):
    message: str
    model: str = "scamper"

@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/api/chat/")
async def chat_endpoint(request: ChatRequest):
    if not client:
        raise HTTPException(status_code=500, detail="Client not ready")
    
    message = request.message
    model_choice = request.model or "scamper"
    
    models = {
        "scamper": "gpt-4o-mini",
        "gold_buckle": "gpt-4o",
        "bodacious": "gpt-4o"
    }
    model = models.get(model_choice, "gpt-4o-mini")
    
    prompts = {
        "scamper": "You are Scamper, a fast rodeo AI.",
        "gold_buckle": "You are Gold Buckle, a balanced rodeo expert.",
        "bodacious": "You are Bodacious, a premium rodeo AI."
    }
    system = prompts.get(model_choice, "You are a rodeo AI.")
    
    async def generate():
        with client.messages.stream(
            model=model,
            max_tokens=1024,
            system=system,
            messages=[{"role": "user", "content": message}]
        ) as stream:
            for text in stream.text_stream:
                yield f"data: {text}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
