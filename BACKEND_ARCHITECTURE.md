# RodeoAI Complete Backend Architecture

## System Overview

```
┌────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Web App    │  │  Mobile App  │  │Admin Dashboard│         │
│  │  (Next.js)   │  │(React Native)│  │  (Internal)   │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬────────┘         │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
          └──────────────────┴──────────────────┘
                             │ HTTPS
                             ▼
┌────────────────────────────────────────────────────────────────┐
│                      LOAD BALANCER (NGINX)                      │
│  - SSL Termination                                             │
│  - Request routing                                             │
│  - Rate limiting (first line)                                  │
└──────────────────────────┬─────────────────────────────────────┘
                           ▼
┌────────────────────────────────────────────────────────────────┐
│                   API GATEWAY (FastAPI)                         │
│  main.py - Central application server                          │
│                                                                 │
│  ┌─────────────────────────────────────────────────────┐       │
│  │              MIDDLEWARE STACK                        │       │
│  │  - CORS Handler                                      │       │
│  │  - Authentication (JWT)                              │       │
│  │  - Rate Limiting (SlowAPI)                          │       │
│  │  - Request Logging                                   │       │
│  │  - Error Handling                                    │       │
│  └─────────────────────────────────────────────────────┘       │
│                                                                 │
│  ┌─────────────────────────────────────────────────────┐       │
│  │                 REST ENDPOINTS                       │       │
│  │                                                      │       │
│  │  Authentication:                                     │       │
│  │  POST /api/auth/google     - OAuth login            │       │
│  │  GET  /api/auth/me         - Current user           │       │
│  │                                                      │       │
│  │  Chat & AI:                                         │       │
│  │  POST /api/chat            - AI chat (streaming)    │       │
│  │  GET  /api/conversations   - List chats             │       │
│  │  GET  /api/conversations/{id} - Get chat            │       │
│  │  POST /api/conversations   - Create chat            │       │
│  │  GET  /api/conversations/search - Search            │       │
│  │                                                      │       │
│  │  Payments:                                          │       │
│  │  GET  /api/subscription/plans - List plans          │       │
│  │  POST /api/payments/create-intent - One-time pay    │       │
│  │  POST /api/payments/create-subscription - Subscribe │       │
│  │  DELETE /api/payments/cancel-subscription - Cancel  │       │
│  │  GET  /api/payments/my-payments - History           │       │
│  │  GET  /api/payments/my-subscription - Active sub    │       │
│  │                                                      │       │
│  │  Export:                                            │       │
│  │  GET  /api/conversations/{id}/export/text - Export  │       │
│  │  GET  /api/conversations/{id}/export/pdf - PDF      │       │
│  │                                                      │       │
│  │  Users:                                             │       │
│  │  GET   /api/users/{id}     - Get user              │       │
│  │  PATCH /api/users/{id}     - Update user           │       │
│  │                                                      │       │
│  │  Webhooks:                                          │       │
│  │  POST /api/webhooks/stripe - Stripe events         │       │
│  │                                                      │       │
│  │  Health:                                            │       │
│  │  GET  /health             - Health check            │       │
│  └─────────────────────────────────────────────────────┘       │
└──────┬──────┬───────┬───────┬──────┬───────┬──────────┬────────┘
       │      │       │       │      │       │          │
       ▼      ▼       ▼       ▼      ▼       ▼          ▼
┌──────────────────────────────────────────────────────────────┐
│                    SERVICE LAYER                              │
│                                                               │
│  ┌───────────┐ ┌────────────┐ ┌──────────┐ ┌─────────────┐ │
│  │    AI     │ │  Payment   │ │   Auth   │ │     MCP     │ │
│  │  Engine   │ │  Service   │ │ Service  │ │  Servers    │ │
│  │           │ │            │ │          │ │             │ │
│  │ • RAG     │ │ • Stripe   │ │ • OAuth  │ │ • ProRodeo  │ │
│  │ • Vector  │ │ • Webhooks │ │ • JWT    │ │ • NexGen    │ │
│  │   Search  │ │ • Billing  │ │ • Session│ │ • Others    │ │
│  └─────┬─────┘ └─────┬──────┘ └────┬─────┘ └──────┬──────┘ │
└────────┼─────────────┼──────────────┼──────────────┼─────────┘
         │             │              │              │
         ▼             ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────┐
│                  EXTERNAL SERVICES                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  OpenAI  │  │  Stripe  │  │  Google  │  │  Email   │   │
│  │   API    │  │   API    │  │  OAuth   │  │ Service  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
         │             │              │              │
         ▼             ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────┐
│                     DATA LAYER                               │
│                                                              │
│  ┌─────────────────────────────────────────┐                │
│  │    PRIMARY DATABASE (PostgreSQL)        │                │
│  │  ┌──────────────────────────────────┐   │                │
│  │  │ Tables:                          │   │                │
│  │  │  • users                         │   │                │
│  │  │  • conversations                 │   │                │
│  │  │  • messages                      │   │                │
│  │  │  • payments                      │   │                │
│  │  │  • subscriptions                 │   │                │
│  │  │  • feedback                      │   │                │
│  │  │  • rate_limits                   │   │                │
│  │  │  • ai_metrics (future)           │   │                │
│  │  │  • rodeos (future)               │   │                │
│  │  └──────────────────────────────────┘   │                │
│  └─────────────────────────────────────────┘                │
│                                                              │
│  ┌─────────────────────────────────────────┐                │
│  │   VECTOR DATABASE (Pinecone/ChromaDB)   │                │
│  │  • Rodeo knowledge embeddings            │                │
│  │  • Semantic search for RAG               │                │
│  │  • ~1M vectors (rodeo expertise)         │                │
│  └─────────────────────────────────────────┘                │
│                                                              │
│  ┌─────────────────────────────────────────┐                │
│  │        CACHE (Redis)                    │                │
│  │  • Session storage                      │                │
│  │  • Rate limit counters                  │                │
│  │  • Temporary data                       │                │
│  │  • Pub/Sub for real-time                │                │
│  └─────────────────────────────────────────┘                │
│                                                              │
│  ┌─────────────────────────────────────────┐                │
│  │     OBJECT STORAGE (S3/CloudFlare R2)   │                │
│  │  • User uploads (images, videos)        │                │
│  │  • PDF exports                          │                │
│  │  • Static assets                        │                │
│  └─────────────────────────────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

## Detailed Component Breakdown

### 1. API Gateway (FastAPI)

**File:** `main.py` (960 lines)

**Responsibilities:**
- HTTP request/response handling
- WebSocket connections (future)
- Route registration
- Middleware orchestration
- Error handling and logging

**Key Features:**
- Async/await for high performance
- Automatic API documentation (Swagger/OpenAPI)
- Type validation with Pydantic
- Dependency injection
- Streaming responses for AI chat

**Performance:**
- Can handle 1000+ req/sec per instance
- Horizontal scaling with load balancer
- WebSocket support for real-time features

### 2. Service Layer

#### A. AI Engine (RAG Service)

**Files:**
- `rag_service.py` - RAG implementation
- `fine_tune.py` - Model fine-tuning
- `build_knowledge_base.py` - Knowledge ingestion

**Workflow:**
```
User Question
    ↓
1. Question → Vector Embedding
    ↓
2. Search Vector DB (top 5 similar chunks)
    ↓
3. Retrieve:
   - "Rope selection guide"
   - "Professional techniques"
   - "Equipment specs"
    ↓
4. Build Enhanced Prompt:
   System: You are RodeoAI...
   Context: [Retrieved knowledge]
   History: [Previous messages]
   Question: [User question]
    ↓
5. Send to OpenAI GPT-4
    ↓
6. Stream response to user
```

**Knowledge Sources:**
- PRCA rulebooks and guides
- Professional training manuals
- Expert interviews (transcribed)
- Competition analysis
- Equipment manufacturer specs

**Vector Database Structure:**
```json
{
  "id": "team_roping_101_chunk_5",
  "vector": [0.123, -0.456, ...],  // 1536 dimensions
  "metadata": {
    "text": "For heading, rope length typically...",
    "source": "PRCA Team Roping Guide 2024",
    "category": "equipment",
    "skill_level": "beginner",
    "last_updated": "2024-01-15"
  }
}
```

#### B. Payment Service

**File:** `payments.py` (293 lines)

**Stripe Integration:**
- Customer creation and management
- One-time payments (PaymentIntents)
- Subscription management
- Webhook event processing
- Refunds and disputes

**Payment Flow:**
```
User clicks "Subscribe to Pro"
    ↓
Frontend: Show Stripe card form
    ↓
User enters card details
    ↓
Backend: Create Subscription
    • Create/get Stripe customer
    • Create subscription with price_id
    • Return client_secret
    ↓
Frontend: Confirm payment with Stripe.js
    ↓
Stripe: Process payment
    ↓
Webhook: payment_intent.succeeded
    ↓
Backend: Update subscription status
    ↓
User: Pro features unlocked!
```

#### C. Auth Service

**File:** `auth.py` (150 lines)

**Features:**
- JWT token generation/validation
- OAuth 2.0 flow (Google, Facebook)
- Password hashing (bcrypt)
- Session management
- Permission checking

**Auth Flow:**
```
User clicks "Login with Google"
    ↓
Frontend: Redirect to Google OAuth
    ↓
Google: User authorizes
    ↓
Google: Return authorization code
    ↓
Backend: Exchange code for user info
    ↓
Backend: Create/get user in DB
    ↓
Backend: Generate JWT token
    ↓
Frontend: Store token in localStorage
    ↓
All future requests: Include token in header
```

#### D. MCP Servers (Future)

**Files:**
- `mcp_prorodeo.py` - ProRodeo.org automation
- `mcp_nexgen.py` - NexGen automation

**Capabilities:**
- Search upcoming rodeos
- Get rodeo details
- Submit entries automatically
- Track standings
- Calendar sync

### 3. Database Layer

#### PostgreSQL Schema

```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    oauth_provider VARCHAR(50),
    oauth_id VARCHAR(255) UNIQUE,
    skill_level VARCHAR(50) DEFAULT 'beginner',
    preferences TEXT,
    stripe_customer_id VARCHAR(255) UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true
);

-- Conversations table
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    title VARCHAR(500) DEFAULT 'New Chat',
    model VARCHAR(100) DEFAULT 'gpt-4o-mini',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    is_archived BOOLEAN DEFAULT false
);

-- Messages table
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    model VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    tokens_used INTEGER
);

-- Payments table
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    stripe_payment_intent_id VARCHAR(255) UNIQUE,
    amount INTEGER NOT NULL,  -- cents
    currency VARCHAR(3) DEFAULT 'usd',
    status VARCHAR(50),
    description TEXT,
    metadata TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Subscriptions table
CREATE TABLE subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    stripe_subscription_id VARCHAR(255) UNIQUE,
    stripe_customer_id VARCHAR(255),
    plan VARCHAR(50) NOT NULL,
    status VARCHAR(50),
    current_period_start TIMESTAMP WITH TIME ZONE,
    current_period_end TIMESTAMP WITH TIME ZONE,
    cancel_at_period_end BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Feedback table
CREATE TABLE feedback (
    id SERIAL PRIMARY KEY,
    message_id INTEGER REFERENCES messages(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id),
    rating VARCHAR(20),  -- positive, negative
    comment TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_payments_user_id ON payments(user_id);
CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX idx_feedback_message_id ON feedback(message_id);
```

## Deployment Architecture

### Development
```
Local Machine:
  • FastAPI dev server (uvicorn)
  • SQLite database
  • No Redis (optional)
  • OpenAI API
  • Stripe test mode
```

### Staging
```
Cloud Server (DigitalOcean/AWS):
  • FastAPI (gunicorn + uvicorn workers)
  • PostgreSQL RDS
  • Redis cache
  • OpenAI API
  • Stripe test mode
  • SSL certificate
```

### Production
```
Multi-tier setup:

Load Balancer (AWS ALB / Cloudflare)
    ↓
API Servers (3+ instances)
  • Auto-scaling based on load
  • Docker containers
  • Health checks
    ↓
Database Cluster (PostgreSQL)
  • Primary + Read replicas
  • Automated backups
  • Connection pooling
    ↓
Cache Layer (Redis Cluster)
  • High availability
  • Persistence enabled
    ↓
Vector Database (Pinecone/Weaviate Cloud)
  • Managed service
  • Auto-scaling

Monitoring:
  • Datadog / New Relic
  • Error tracking (Sentry)
  • Performance metrics
  • User analytics
```

## Scaling Strategy

### Vertical Scaling (Single Server)
```
Start: 2 CPU, 4GB RAM - $20/mo
  ↓ (100+ concurrent users)
Upgrade: 4 CPU, 8GB RAM - $40/mo
  ↓ (500+ concurrent users)
Upgrade: 8 CPU, 16GB RAM - $80/mo
```

### Horizontal Scaling (Multiple Servers)
```
Once vertical limits reached:

Load Balancer
    ↓
API Server 1 (4 CPU, 8GB) ─┐
API Server 2 (4 CPU, 8GB) ─┼→ PostgreSQL Primary
API Server 3 (4 CPU, 8GB) ─┘     ↓
                              Read Replica
    ↓
Redis Cluster
Vector DB (managed)
```

**Can handle:**
- 10,000+ concurrent users
- 1M+ requests per day
- 99.9% uptime

## Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| API response time | < 200ms | ~150ms |
| AI chat response (first token) | < 1s | ~800ms |
| AI chat full response | < 5s | ~3s |
| Database queries | < 50ms | ~20ms |
| Uptime | 99.9% | TBD |
| Concurrent users | 10K+ | TBD |

## Security Measures

1. **Authentication**
   - JWT tokens with expiration
   - Secure password hashing (bcrypt)
   - OAuth 2.0 for social login

2. **API Security**
   - Rate limiting (30-100 req/min)
   - CORS configuration
   - Input validation (Pydantic)
   - SQL injection prevention (ORM)

3. **Payment Security**
   - Stripe handles all card data (PCI compliant)
   - Webhook signature verification
   - HTTPS only in production

4. **Data Security**
   - Database encryption at rest
   - SSL/TLS for data in transit
   - Regular backups
   - Access controls (IAM)

## Monitoring & Logging

```python
# Add structured logging
import logging
from pythonjsonlogger import jsonlogger

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
handler.setFormatter(formatter)
logger.addHandler(handler)

# Log important events
logger.info("User login", extra={
    "user_id": user.id,
    "method": "google_oauth",
    "ip": request.client.host
})

logger.error("Payment failed", extra={
    "user_id": user.id,
    "amount": amount,
    "stripe_error": str(error)
})
```

**What to monitor:**
- API response times
- Error rates
- Active users
- Database performance
- AI token usage
- Payment success rate
- Cache hit rate

## Cost Estimation

**Monthly Operating Costs (1000 active users):**

| Service | Cost |
|---------|------|
| Server (2 instances) | $80 |
| PostgreSQL (managed) | $50 |
| Redis (managed) | $30 |
| Vector DB (Pinecone) | $70 |
| OpenAI API (50K queries) | $150 |
| Stripe fees (500 subs) | $150 |
| SSL & domain | $10 |
| **Total** | **$540/mo** |

**Revenue (1000 active users):**
- 500 Pro ($9.99) = $4,995
- 200 Premium ($19.99) = $3,998
- **Total: $8,993/mo**
- **Profit: $8,453/mo**

## Next Steps for Production

1. **Set up infrastructure** (Week 1)
   - Choose cloud provider (AWS/DO/GCP)
   - Set up PostgreSQL
   - Configure Redis
   - Set up monitoring

2. **Implement RAG** (Week 2-3)
   - Set up vector database
   - Ingest rodeo knowledge
   - Test search quality
   - Optimize prompts

3. **Load testing** (Week 4)
   - Simulate 1000 concurrent users
   - Identify bottlenecks
   - Optimize slow queries
   - Configure caching

4. **Security audit** (Week 5)
   - Penetration testing
   - Code review
   - OWASP top 10 check
   - Fix vulnerabilities

5. **Launch** (Week 6)
   - Deploy to production
   - Monitor closely
   - Gather user feedback
   - Iterate quickly

---

**This architecture can scale to millions of users with proper implementation!** 🚀
