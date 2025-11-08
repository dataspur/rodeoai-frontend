# RodeoAI Backend Architecture & AI Training Strategy

## Current Backend Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend Layer                           │
│  - Next.js App (pages/index.js)                                 │
│  - Standalone HTML (public/index.html)                          │
│  - Payment UI (public/payment-example.html)                     │
└──────────────────────┬──────────────────────────────────────────┘
                       │ HTTP/WebSocket
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway (FastAPI)                       │
│  main.py - All REST endpoints                                   │
│  - Chat endpoints                                               │
│  - User management                                              │
│  - Conversation CRUD                                            │
│  - Payment processing                                           │
│  - OAuth authentication                                         │
└──────────────┬──────────────────────────┬────────────────────────┘
               │                          │
               ▼                          ▼
┌──────────────────────────┐   ┌────────────────────────┐
│   Business Logic Layer   │   │   External Services    │
│  - payments.py           │   │  - Stripe API          │
│  - auth.py               │   │  - OpenAI API          │
│  - models.py             │   │  - OAuth providers     │
└──────────┬───────────────┘   └────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Database Layer                              │
│  database.py - SQLAlchemy ORM                                   │
│  - PostgreSQL/SQLite                                            │
│  - Users, Conversations, Messages, Payments, Subscriptions      │
└─────────────────────────────────────────────────────────────────┘
```

## Future Complete Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend Layer                           │
│  - Web App (Next.js/React)                                      │
│  - Mobile App (React Native - future)                           │
│  - Admin Dashboard                                              │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway (FastAPI)                       │
│  - REST API endpoints                                           │
│  - WebSocket for real-time features                            │
│  - Rate limiting & authentication                               │
└──────┬────────┬────────┬────────┬────────┬────────┬─────────────┘
       │        │        │        │        │        │
       ▼        ▼        ▼        ▼        ▼        ▼
┌──────────┐ ┌────────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌─────────────┐
│   AI     │ │ Payment│ │ MCP  │ │ Auth │ │ Notif│ │  Analytics  │
│  Engine  │ │Service │ │Servers│││Service│ │Service│ │  Service    │
│          │ │        │ │      │ │      │ │      │ │             │
│ - RAG    │ │-Stripe │ │-PRCA │ │-OAuth│ │-Email│ │ - Metrics   │
│ - Vector │ │-Refunds│ │-NexGen│││-JWT  │ │-SMS  │ │ - Logging   │
│   DB     │ │-Billing│ │      │ │      │ │-Push │ │ - Monitoring│
│ - Cache  │ │        │ │      │ │      │ │      │ │             │
└────┬─────┘ └────────┘ └──────┘ └──────┘ └──────┘ └─────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Data Storage Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ PostgreSQL   │  │ Vector DB    │  │ Redis Cache  │          │
│  │ (Primary)    │  │ (Pinecone/   │  │ (Sessions)   │          │
│  │              │  │  Weaviate)   │  │              │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ S3/Cloud     │  │ ElasticSearch│  │ InfluxDB     │          │
│  │ Storage      │  │ (Full-text)  │  │ (Time-series)│          │
│  │ (Media)      │  │              │  │              │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

## AI Training & Fine-Tuning Strategy

### Option 1: RAG (Retrieval Augmented Generation) - RECOMMENDED

**What is RAG?**
Instead of fine-tuning the model, you augment its knowledge by providing relevant context from a knowledge base in each query.

**Why RAG for RodeoAI?**
- ✅ Easier to update (add new rodeo knowledge without retraining)
- ✅ More transparent (you know where answers come from)
- ✅ Cost-effective (no fine-tuning fees)
- ✅ Better for frequently changing info (rodeo schedules, rules, techniques)
- ✅ Can cite sources

**Architecture:**

```
User Question: "What's the best rope length for heading?"
         ↓
┌────────────────────────────────────────────┐
│  1. Convert question to vector embedding   │
│     OpenAI Embeddings API                  │
└─────────────────┬──────────────────────────┘
                  ↓
┌────────────────────────────────────────────┐
│  2. Search vector database for similar     │
│     rodeo knowledge chunks                 │
│     (Pinecone, Weaviate, or ChromaDB)      │
└─────────────────┬──────────────────────────┘
                  ↓
┌────────────────────────────────────────────┐
│  3. Retrieve top 5 most relevant chunks    │
│     - "Rope length guide for team roping"  │
│     - "Heading equipment specifications"   │
│     - "Professional header preferences"    │
└─────────────────┬──────────────────────────┘
                  ↓
┌────────────────────────────────────────────┐
│  4. Build augmented prompt                 │
│     System: You are RodeoAI...             │
│     Context: [Retrieved knowledge]         │
│     Question: [User's question]            │
└─────────────────┬──────────────────────────┘
                  ↓
┌────────────────────────────────────────────┐
│  5. Send to OpenAI GPT-4                   │
│     Returns answer based on context        │
└─────────────────┬──────────────────────────┘
                  ↓
         User receives expert answer!
```

**Implementation:**

```python
# Create: Desktop/rodeoai-backend/rag_service.py

from openai import OpenAI
import pinecone
from typing import List, Dict
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize Pinecone vector database
pinecone.init(
    api_key=os.getenv("PINECONE_API_KEY"),
    environment=os.getenv("PINECONE_ENV")
)
index = pinecone.Index("rodeo-knowledge")


class RAGService:
    """Retrieval Augmented Generation for rodeo expertise."""

    @staticmethod
    async def create_embedding(text: str) -> List[float]:
        """Convert text to vector embedding."""
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding

    @staticmethod
    async def search_knowledge(query: str, top_k: int = 5) -> List[Dict]:
        """Search vector database for relevant rodeo knowledge."""
        # Create embedding for the query
        query_embedding = await RAGService.create_embedding(query)

        # Search Pinecone
        results = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )

        return [
            {
                "text": match.metadata["text"],
                "source": match.metadata.get("source", ""),
                "score": match.score
            }
            for match in results.matches
        ]

    @staticmethod
    async def augmented_chat(
        question: str,
        conversation_history: List[Dict],
        user_skill_level: str = "intermediate"
    ) -> str:
        """
        Generate response using RAG.

        Args:
            question: User's question
            conversation_history: Previous messages
            user_skill_level: User's experience level

        Returns:
            AI-generated response augmented with rodeo knowledge
        """
        # 1. Search for relevant knowledge
        relevant_chunks = await RAGService.search_knowledge(question)

        # 2. Build context from retrieved knowledge
        context = "\n\n".join([
            f"[Source: {chunk['source']}]\n{chunk['text']}"
            for chunk in relevant_chunks
        ])

        # 3. Build augmented prompt
        system_message = f"""You are RodeoAI, an expert assistant for team roping and rodeo.

The user's skill level is: {user_skill_level}

Use the following rodeo knowledge to answer questions accurately:

{context}

Guidelines:
- Base answers on the provided context when possible
- Cite sources when referencing specific information
- Adjust technical depth based on user's skill level
- If context doesn't contain the answer, use your general rodeo knowledge
- Be practical and actionable in your advice
"""

        # 4. Add conversation history
        messages = [{"role": "system", "content": system_message}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": question})

        # 5. Generate response
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )

        return response.choices[0].message.content


# Update main.py to use RAG
from rag_service import RAGService

@app.post("/api/chat")
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """Chat endpoint with RAG support."""

    # Get user's skill level
    skill_level = "intermediate"
    if request.user_id:
        user = db.query(User).filter(User.id == request.user_id).first()
        if user and user.skill_level:
            skill_level = user.skill_level.value

    # Convert messages to conversation history
    conversation_history = [
        {"role": msg.role, "content": msg.content}
        for msg in request.messages[:-1]  # All except last message
    ]

    # Get last message (current question)
    question = request.messages[-1].content

    # Use RAG to generate response
    response = await RAGService.augmented_chat(
        question=question,
        conversation_history=conversation_history,
        user_skill_level=skill_level
    )

    return {"response": response}
```

**Building the Knowledge Base:**

```python
# Create: Desktop/rodeoai-backend/build_knowledge_base.py

import asyncio
from openai import OpenAI
import pinecone
import json

client = OpenAI()

# Initialize Pinecone
pinecone.init(api_key="your-key", environment="us-west1-gcp")

# Create index if it doesn't exist
if "rodeo-knowledge" not in pinecone.list_indexes():
    pinecone.create_index(
        "rodeo-knowledge",
        dimension=1536,  # text-embedding-3-small dimension
        metric="cosine"
    )

index = pinecone.Index("rodeo-knowledge")


async def chunk_text(text: str, chunk_size: int = 500) -> List[str]:
    """Split text into chunks for embedding."""
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)

    return chunks


async def embed_and_store(chunks: List[str], source: str):
    """Embed text chunks and store in vector database."""
    vectors = []

    for i, chunk in enumerate(chunks):
        # Create embedding
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=chunk
        )
        embedding = response.data[0].embedding

        # Prepare for storage
        vectors.append({
            "id": f"{source}_{i}",
            "values": embedding,
            "metadata": {
                "text": chunk,
                "source": source,
                "chunk_index": i
            }
        })

    # Upload to Pinecone
    index.upsert(vectors)
    print(f"✓ Stored {len(vectors)} chunks from {source}")


async def ingest_rodeo_knowledge():
    """Ingest rodeo knowledge from various sources."""

    # 1. Team Roping Techniques
    team_roping_guide = """
    TEAM ROPING FUNDAMENTALS

    Rope Length for Headers:
    - Beginners: 30-31 feet provides more forgiveness
    - Intermediate: 30 feet is standard
    - Advanced: 28-30 feet for faster horses and timing
    - Professional: Many use 28-30 feet soft lay rope

    Rope Weight and Lay:
    - Soft lay (3/8"): Better feel, popular among headers
    - Medium lay (7/16"): More body, holds loop shape better
    - Stiff lay: Holds shape in wind, less popular

    Loop Size:
    - Header loop: 6-8 feet diameter for beginners
    - Experienced headers: 5-6 feet for precision
    - Adjust based on cattle size and speed

    Swing Techniques:
    - Keep tip up and moving forward
    - Swing with shoulder, not just arm
    - Time delivery with horse's stride
    - Release at peak of swing for distance
    ...
    """

    chunks = await chunk_text(team_roping_guide)
    await embed_and_store(chunks, "Team Roping Guide - ProRodeo")

    # 2. Horse Training
    horse_training = """
    RODEO HORSE TRAINING GUIDE

    Heading Horse Requirements:
    - Calm temperament essential
    - Good stop and rate cattle
    - Ability to track left (position cattle)
    - Soft mouth for control
    - 15.1-16 hands ideal height

    Training Progression:
    Week 1-4: Ground work and basics
    - Desensitization
    - Leading and respect
    - Lunging both directions

    Week 5-8: Introduction to cattle
    - Tracking slow cattle
    - Rating (matching speed)
    - Stop and position
    ...
    """

    chunks = await chunk_text(horse_training)
    await embed_and_store(chunks, "Horse Training - AQHA")

    # 3. Competition Strategy
    competition_guide = """
    RODEO COMPETITION STRATEGY

    Pre-Run Preparation:
    - Arrive 2 hours early
    - Check cattle and arena conditions
    - Warm up horse progressively
    - Mental visualization (3-5 minutes)
    - Review partner signals

    During Competition:
    - Stay focused on process, not outcome
    - Adjust strategy based on cattle
    - Communicate with partner
    - Breathe and stay relaxed

    Common Mistakes:
    - Over-riding nervous horses
    - Not adjusting to cattle speed
    - Poor partner communication
    - Rushing the throw
    ...
    """

    chunks = await chunk_text(competition_guide)
    await embed_and_store(chunks, "Competition Guide - PRCA")

    # 4. Equipment Recommendations
    equipment_guide = """
    TEAM ROPING EQUIPMENT GUIDE

    Essential Gear for Headers:

    Saddles:
    - 15-16 inch seat typical
    - High cantle for security
    - Forward rigging (7/8 or full)
    - Strong horn for dallying
    - Price range: $2,000-$8,000

    Recommended brands:
    - Billy Cook (reliable, $2,500-4,500)
    - Cactus Saddlery (pro choice, $4,000-8,000)
    - Martin Saddlery (high-end, $5,000+)

    Ropes:
    Headers:
    - FastBack Ropes: Consistent, popular
    - Classic Ropes: Wide variety of lays
    - Lone Star Ropes: Premium quality
    - Price: $30-$60 per rope

    Heelers:
    - Generally prefer stiffer lay
    - 35-37 feet length
    - Same brands as headers
    ...
    """

    chunks = await chunk_text(equipment_guide)
    await embed_and_store(chunks, "Equipment Guide - Western Horseman")

    print("✓ Knowledge base built successfully!")


# Run the ingestion
if __name__ == "__main__":
    asyncio.run(ingest_rodeo_knowledge())
```

**Sources for Knowledge Base:**

1. **Official Rulebooks**
   - PRCA (Professional Rodeo Cowboys Association)
   - WPRA (Women's Professional Rodeo Association)
   - USTRC (United States Team Roping Championships)

2. **Training Manuals**
   - "Team Roping with Jake and Clay" - Jake Barnes
   - "Heeling" - Matt Sherwood
   - "The Art of Team Roping" - Leo Camarillo

3. **Video Transcripts**
   - ProRodeo.TV instructional videos
   - Rope Smart Academy content
   - Professional clinics and seminars

4. **Expert Interviews**
   - World champion headers/heelers
   - Professional trainers
   - Equipment manufacturers

5. **Competition Data**
   - Historical winning times
   - Technique analysis
   - Equipment preferences of top ropers

### Option 2: Fine-Tuning GPT Models

**When to fine-tune:**
- You have 1000+ high-quality training examples
- Specific style/tone you want to match
- Need to reduce token usage in prompts
- Want model to follow specific patterns

**Process:**

```python
# Create: Desktop/rodeoai-backend/fine_tune.py

from openai import OpenAI
import json

client = OpenAI()

# 1. Prepare training data
training_data = [
    {
        "messages": [
            {"role": "system", "content": "You are RodeoAI, an expert in team roping."},
            {"role": "user", "content": "What rope length should I use for heading?"},
            {"role": "assistant", "content": "For heading, rope length depends on your experience level. Beginners should start with 30-31 feet, which offers more forgiveness. Intermediate ropers typically use 30 feet. Advanced and professional headers often prefer 28-30 feet for faster horses and precise timing. The key is finding what feels comfortable and gives you confidence in your delivery."}
        ]
    },
    {
        "messages": [
            {"role": "system", "content": "You are RodeoAI, an expert in team roping."},
            {"role": "user", "content": "How do I improve my swing?"},
            {"role": "assistant", "content": "To improve your swing:\n\n1. Keep the tip up and moving forward\n2. Swing from your shoulder, not just your arm\n3. Time your delivery with your horse's stride\n4. Release at the peak of your swing for maximum distance\n5. Practice daily - even 10 minutes of dummy roping helps\n\nConsistency comes from muscle memory, so regular practice is essential."}
        ]
    },
    # ... need 100-1000+ examples
]

# 2. Save to JSONL file
with open("training_data.jsonl", "w") as f:
    for item in training_data:
        f.write(json.dumps(item) + "\n")

# 3. Upload training file
with open("training_data.jsonl", "rb") as f:
    training_file = client.files.create(
        file=f,
        purpose="fine-tune"
    )

# 4. Create fine-tuning job
fine_tune_job = client.fine_tuning.jobs.create(
    training_file=training_file.id,
    model="gpt-4o-mini-2024-07-18",  # or gpt-4o
    hyperparameters={
        "n_epochs": 3
    }
)

print(f"Fine-tune job created: {fine_tune_job.id}")
print("Monitor status with: client.fine_tuning.jobs.retrieve(job_id)")

# 5. Use fine-tuned model
# After job completes, you'll get a model ID like:
# ft:gpt-4o-mini:your-org:rodeoai:abc123

# Use it in chat:
response = client.chat.completions.create(
    model="ft:gpt-4o-mini:your-org:rodeoai:abc123",
    messages=[
        {"role": "user", "content": "Best rope for heeling?"}
    ]
)
```

**Cost Comparison:**

| Approach | Setup Cost | Per-Request Cost | Maintenance |
|----------|-----------|------------------|-------------|
| RAG | $10-50/mo (Pinecone) | ~$0.01/request | Easy updates |
| Fine-tuning | $10-100 (training) | ~$0.005/request | Retrain for updates |
| Hybrid | $20-100/mo | ~$0.008/request | Best of both |

### Option 3: Hybrid Approach (BEST)

Combine RAG + Fine-tuned model:

```python
class HybridAIService:
    """Best of both worlds: Fine-tuned model + RAG."""

    def __init__(self):
        self.base_model = "ft:gpt-4o-mini:rodeoai:abc123"  # Fine-tuned
        self.rag_service = RAGService()

    async def generate_response(self, question: str, history: List):
        # 1. Get relevant knowledge from RAG
        context = await self.rag_service.search_knowledge(question)

        # 2. Use fine-tuned model (already knows rodeo terminology/style)
        #    with RAG context (for up-to-date specific info)
        messages = [
            {"role": "system", "content": f"Context: {context}"},
            *history,
            {"role": "user", "content": question}
        ]

        response = client.chat.completions.create(
            model=self.base_model,  # Fine-tuned for rodeo expertise
            messages=messages
        )

        return response.choices[0].message.content
```

## Dependencies to Add

```txt
# Add to requirements.txt

# For RAG
pinecone-client==3.0.0
chromadb==0.4.18  # Alternative to Pinecone (free, local)
langchain==0.1.0  # Optional: RAG framework

# For embeddings
tiktoken==0.5.2  # Token counting

# For knowledge processing
beautifulsoup4==4.12.2  # Web scraping
pypdf==3.17.0  # PDF processing
youtube-transcript-api==0.6.1  # Video transcripts
```

## Recommended Architecture

**Phase 1: Start with RAG (Weeks 1-2)**
- Set up Pinecone/ChromaDB
- Ingest rodeo knowledge
- Implement RAG in chat endpoint
- Test with real users

**Phase 2: Collect Data (Weeks 3-8)**
- Log all user questions
- Save high-quality responses
- Get expert review of answers
- Build fine-tuning dataset

**Phase 3: Fine-tune (Week 9-10)**
- Create training dataset (1000+ examples)
- Fine-tune gpt-4o-mini
- A/B test against RAG-only
- Measure improvement

**Phase 4: Hybrid (Week 11+)**
- Combine fine-tuned model + RAG
- Best accuracy and performance
- Continuous improvement loop

## File Structure

```
Desktop/rodeoai-backend/
├── main.py                 # API endpoints
├── payments.py             # Stripe integration
├── auth.py                 # Authentication
├── models.py               # Database models
├── database.py             # DB config
├── rag_service.py          # RAG implementation ⭐ NEW
├── fine_tune.py            # Fine-tuning scripts ⭐ NEW
├── build_knowledge_base.py # Knowledge ingestion ⭐ NEW
├── knowledge/              # Knowledge sources ⭐ NEW
│   ├── team_roping_guide.txt
│   ├── horse_training.txt
│   ├── competition_strategy.txt
│   └── equipment_guide.txt
└── requirements.txt        # Dependencies
```

## Performance Metrics to Track

```python
# Add to models.py
class AIMetric(Base):
    """Track AI performance for continuous improvement."""
    __tablename__ = "ai_metrics"

    id = Column(Integer, primary_key=True)
    question = Column(Text)
    response = Column(Text)
    rag_chunks_used = Column(Integer)
    model_used = Column(String(100))
    latency_ms = Column(Integer)
    user_feedback = Column(String(20))  # thumbs_up, thumbs_down
    expert_reviewed = Column(Boolean, default=False)
    expert_rating = Column(Integer)  # 1-5 stars
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

---

**Recommended: Start with RAG, then add fine-tuning once you have data!** 🚀
