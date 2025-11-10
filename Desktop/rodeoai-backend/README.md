# RodeoAI Backend

FastAPI backend with TAURUS intelligent model routing for rodeo competition insights and contestant management.

## Features

- **TAURUS Model Routing**: Intelligent selection between GPT-4, GPT-4o, and GPT-4o-mini based on query complexity
- **Supabase Authentication**: Multi-provider auth (Google, Facebook, Email, Phone, Apple)
- **Contestant Profiles**: Social media integration and digital rodeo cards
- **Streaming Chat**: Real-time AI responses with Server-Sent Events
- **PostgreSQL Database**: With pgvector for future RAG capabilities
- **Railway Ready**: One-click deployment configuration

## Tech Stack

- **Framework**: FastAPI 0.104.1
- **Database**: PostgreSQL (via Supabase)
- **ORM**: SQLAlchemy 2.0.23
- **Auth**: Supabase Auth + JWT
- **AI**: OpenAI GPT-4 family
- **Deployment**: Railway

## Quick Start

### Local Development

1. **Clone and setup**
   ```bash
   git clone https://github.com/YOUR_USERNAME/rodeoai-backend.git
   cd rodeoai-backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

5. **Run server**
   ```bash
   uvicorn main:app --reload --port 8000
   ```

6. **Access API**
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs
   - Redoc: http://localhost:8000/redoc

### Environment Variables

```env
# OpenAI
OPENAI_API_KEY=sk-...

# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJ...
SUPABASE_JWT_SECRET=your-jwt-secret
DATABASE_URL=postgresql://postgres:password@db.xxx.supabase.co:5432/postgres

# Application
SECRET_KEY=your-secret-key-min-32-chars
```

## API Endpoints

### Health Check
```bash
GET /
```

### Authentication
```bash
POST /api/auth/register
POST /api/auth/token
GET /api/auth/me
```

### Chat (TAURUS)
```bash
POST /api/chat/
Content-Type: application/json

{
  "message": "What is team roping?",
  "model": "taurus"
}
```

### Contestant Profiles
```bash
POST /api/contestants/me         # Create profile
PATCH /api/contestants/me        # Update profile
GET /api/contestants/me          # Get own profile
GET /api/contestants/{username}  # Get public profile
```

## TAURUS Model Routing

Intelligent routing based on:
- **Query complexity** (0-10 scoring)
- **Tool requirements** (file, travel, analytics, marketplace, entry)
- **Advanced topics** (NFR, legal, medical, business)

### Model Selection
- **gpt-4o-mini**: Simple Q&A, basic queries (complexity < 4, no tools)
- **gpt-4o**: Tool use, moderate complexity (4-6), multi-step tasks
- **gpt-4**: High complexity (7+), advanced topics, critical decisions

### Testing Routing
```bash
python test_routing.py
```

Expected: 100% routing accuracy across 11 test scenarios.

## Database Schema

### Users
- Authentication and profile data
- Linked to Supabase Auth
- Pro tier management

### Contestant Profiles
- Social media handles (6 platforms)
- Rodeo information (hometown, events, bio)
- Verification status

### Future: Document Embeddings
- pgvector for RAG
- Store vet records, training logs, registration papers
- Semantic search capabilities

## Deployment

### Railway (Recommended)

1. **Push to GitHub**
   ```bash
   ./setup_github.sh
   ```

2. **Deploy on Railway**
   - Go to https://railway.app/new
   - Select GitHub repo
   - Configure environment variables
   - Deploy automatically

See [RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md) for detailed instructions.

### Manual Deployment

```bash
# Build
pip install -r requirements.txt

# Run
uvicorn main:app --host 0.0.0.0 --port $PORT
```

## Project Structure

```
rodeoai-backend/
├── main.py                    # FastAPI app and routes
├── taurus_routing.py          # Intelligent model selection
├── database.py                # Database configuration
├── models.py                  # SQLAlchemy models
├── schemas.py                 # Pydantic schemas
├── auth.py                    # JWT authentication
├── supabase_client.py         # Supabase integration
├── test_routing.py            # Routing test suite
├── requirements.txt           # Python dependencies
├── railway.json               # Railway configuration
├── Procfile                   # Process definition
├── .env.example               # Environment template
├── .gitignore                 # Git exclusions
├── README.md                  # This file
└── RAILWAY_DEPLOYMENT.md      # Deployment guide
```

## Development

### Adding New Routes

```python
# main.py

@app.get("/api/new-endpoint/")
async def new_endpoint():
    return {"message": "New endpoint"}
```

### Adding Database Models

```python
# models.py

class NewModel(Base):
    __tablename__ = "new_table"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
```

### Testing

```bash
# Run routing tests
python test_routing.py

# Manual API testing
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Test query", "model": "taurus"}'
```

## Monitoring

### Logs
- Railway: View in dashboard > Deployments > Deploy Logs
- Local: Console output

### Metrics
- Model selection decisions logged
- Complexity scores tracked
- Tool usage monitored

## Security

- JWT token-based authentication
- Bcrypt password hashing
- Supabase RLS policies
- CORS configured for production
- Environment variables for secrets

## Contributing

1. Create feature branch
2. Make changes
3. Test locally
4. Push and create PR
5. Railway auto-deploys on merge to main

## License

Private - DataSpur/RodeoAI

## Support

For issues or questions:
- Check Railway logs
- Review RAILWAY_DEPLOYMENT.md
- Check Supabase dashboard
- Monitor OpenAI usage

## Roadmap

- [ ] RAG implementation with pgvector
- [ ] Document processing pipeline
- [ ] Travel planner integration (Google Maps API)
- [ ] Marketplace AI-assisted listings
- [ ] Analytics dashboard backend
- [ ] WebSocket support for real-time features
- [ ] Rate limiting
- [ ] Caching layer (Redis)
