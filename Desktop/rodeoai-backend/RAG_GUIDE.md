# RodeoAI RAG System Guide

## Overview

RodeoAI uses a **RAG (Retrieval Augmented Generation)** system to provide accurate, knowledge-grounded responses about team roping and rodeo. Instead of relying solely on the AI model's training data, RAG retrieves relevant information from a curated knowledge base and uses it to inform responses.

## How RAG Works

1. **User asks a question** - "What rope should I use for heading?"
2. **Semantic search** - The system converts the question to a vector embedding and searches the knowledge base for similar content
3. **Retrieve relevant chunks** - Top 3-5 most relevant knowledge pieces are retrieved
4. **Augment the prompt** - Retrieved knowledge is added to the AI's context
5. **Generate response** - AI generates an answer informed by the specific rodeo knowledge
6. **Cite sources** - AI can reference where information came from

## Architecture

```
User Question
     ↓
Vector Embedding (OpenAI text-embedding-3-small)
     ↓
ChromaDB Semantic Search
     ↓
Retrieve Top K Chunks (with metadata)
     ↓
Build Augmented Prompt
     ↓
OpenAI gpt-4o-mini with Context
     ↓
Stream Response to User
```

## Knowledge Base Structure

**Location**: `Desktop/rodeoai-backend/chroma_db/`

**Vector Database**: ChromaDB (local, persistent)

**Current Knowledge Files**:
- `knowledge/team_roping_basics.txt` - Fundamentals of header and heeler techniques
- `knowledge/equipment_guide.txt` - Comprehensive gear recommendations
- `knowledge/horse_training.txt` - Training methods for roping horses

**Metadata for Each Chunk**:
- `source`: Where the knowledge came from
- `category`: Type of knowledge (technique, equipment, training, competition, general)
- `skill_level`: Target audience (beginner, intermediate, advanced, professional, all)
- `chunk_index`: Position in the original document
- `total_chunks`: Total number of chunks from this source

## Adding New Knowledge

### Method 1: Using the Build Script (Recommended)

1. **Create a text file** in the `knowledge/` directory:
```bash
cd Desktop/rodeoai-backend/knowledge
nano my_new_knowledge.txt
```

2. **Add configuration** to `build_knowledge_base.py`:
```python
KNOWLEDGE_SOURCES = [
    # ... existing sources ...
    {
        "file": "knowledge/my_new_knowledge.txt",
        "category": "competition",  # or technique, equipment, training, general
        "skill_level": "intermediate",  # or beginner, advanced, professional, all
        "source": "Competition Strategies Guide"
    }
]
```

3. **Run the build script**:
```bash
python build_knowledge_base.py --add
```

This will add your new knowledge while keeping existing knowledge intact.

### Method 2: Interactive Custom Knowledge

```bash
python build_knowledge_base.py
```

Then select option 4 (Add custom knowledge) and follow the prompts.

### Method 3: Programmatic API

```python
from rag_service import RAGService

# Add a single piece of knowledge
RAGService.add_knowledge(
    text="When heading, position your horse parallel to the steer...",
    source="Expert Tips",
    category="technique",
    skill_level="advanced",
    metadata={"author": "John Smith", "year": 2024}
)
```

### Method 4: Bulk Import from File

```python
from rag_service import RAGService, chunk_text

# Read file
with open("my_knowledge.txt", "r") as f:
    content = f.read()

# Chunk it
chunks = chunk_text(content, chunk_size=500, overlap=50)

# Add each chunk
for i, chunk in enumerate(chunks):
    RAGService.add_knowledge(
        text=chunk,
        source="My Knowledge Source",
        category="general",
        skill_level="all",
        metadata={"chunk": i, "total": len(chunks)}
    )
```

## Knowledge File Format

Knowledge files should be plain text (.txt) with clear sections and informative content.

**Best Practices**:
- Use clear section headings
- Include specific, actionable information
- Cite sources when possible
- Break complex topics into digestible paragraphs
- Use examples to illustrate concepts
- Maintain a consistent voice and terminology

**Example Structure**:
```
TOPIC NAME - COMPREHENSIVE GUIDE

Introduction paragraph explaining the topic...

SUBTOPIC 1

Detailed information about subtopic 1...

Key points:
- Point 1
- Point 2
- Point 3

SUBTOPIC 2

More detailed information...

Common Mistakes:
- Mistake 1
- Mistake 2

Tips for Success:
- Tip 1
- Tip 2
```

## Chunking Strategy

Documents are automatically chunked into ~500 character pieces with 50 character overlap.

**Why Chunking?**
- Smaller chunks improve search precision
- Overlap ensures context isn't lost at boundaries
- Fits within embedding model limits
- Faster retrieval and processing

**Chunk Size Guidelines**:
- Default: 500 characters
- Longer chunks (800-1000): Better for complex topics requiring more context
- Shorter chunks (300-400): Better for quick facts and definitions

You can adjust chunking in `rag_service.py`:
```python
chunks = chunk_text(text, chunk_size=500, overlap=50)
```

## Testing the Knowledge Base

### View Statistics

```bash
python build_knowledge_base.py --stats
```

Output:
```
Total chunks: 247
Collection: rodeo_knowledge
Path: /path/to/chroma_db
```

### Test Search

```python
from rag_service import RAGService

results = RAGService.search_knowledge(
    "How do I train a heading horse?",
    top_k=5,
    min_score=0.5
)

for i, result in enumerate(results, 1):
    print(f"\n{i}. Score: {result['score']:.3f}")
    print(f"   Source: {result['metadata'].get('source')}")
    print(f"   Text: {result['text'][:150]}...")
```

### Test Full RAG Response

```python
from rag_service import RAGService

question = "What equipment do I need to start team roping?"
conversation_history = []

for chunk in RAGService.augmented_response(
    question=question,
    conversation_history=conversation_history,
    user_skill_level="beginner",
    stream=True
):
    print(chunk, end="", flush=True)
```

## Managing the Knowledge Base

### Rebuild from Scratch

```bash
python build_knowledge_base.py --rebuild
```

This clears all existing knowledge and rebuilds from configured sources.

### View Collection Info

```python
from rag_service import RAGService

stats = RAGService.get_collection_stats()
print(f"Total chunks: {stats['total_chunks']}")
print(f"Database path: {stats['database_path']}")
```

### Clear Knowledge Base

```python
from rag_service import RAGService

# WARNING: This deletes all knowledge!
RAGService.clear_knowledge_base()
```

## Embedding Model

**Current Model**: OpenAI `text-embedding-3-small`

**Specs**:
- Dimensions: 1536
- Cost: $0.00002 / 1K tokens
- Max input: 8,191 tokens
- Performance: Fast, accurate for semantic search

**Switching Models**:
Edit `rag_service.py` line 46:
```python
response = openai_client.embeddings.create(
    model="text-embedding-3-large",  # or text-embedding-ada-002
    input=text
)
```

Note: Changing models requires rebuilding the entire knowledge base.

## Search Parameters

Configure in `main.py` or when calling RAGService:

```python
RAGService.search_knowledge(
    query="your question",
    top_k=5,        # Number of chunks to retrieve
    min_score=0.5   # Minimum similarity threshold (0-1)
)
```

**Recommendations**:
- `top_k=3`: Fast, concise responses
- `top_k=5`: Balanced (default)
- `top_k=10`: Comprehensive, may include less relevant info
- `min_score=0.3`: More lenient, more results
- `min_score=0.7`: Strict, only highly relevant

## Performance Optimization

### Indexing

ChromaDB automatically indexes vectors for fast search. No manual indexing needed.

### Caching

ChromaDB uses memory-mapped files for efficient access. The database persists to disk but keeps frequently accessed data in memory.

### Batch Operations

When adding many documents:
```python
texts = [...]  # List of knowledge texts
for text in texts:
    RAGService.add_knowledge(text, ...)
```

### Database Location

Default: `Desktop/rodeoai-backend/chroma_db/`

To change, edit `rag_service.py` line 20:
```python
db_path = os.path.join(os.path.dirname(__file__), "your_custom_path")
```

## Troubleshooting

### "No results found" for valid questions

**Possible Causes**:
1. Knowledge base is empty
2. Question uses very different terminology
3. `min_score` threshold too high

**Solutions**:
- Check stats: `python build_knowledge_base.py --stats`
- Rebuild: `python build_knowledge_base.py --rebuild`
- Lower min_score to 0.3
- Add more knowledge on that topic

### Slow response times

**Causes**:
- Too many chunks being retrieved
- Large knowledge base
- Network latency to OpenAI

**Solutions**:
- Reduce `top_k` to 3
- Increase `min_score` to filter more aggressively
- Consider caching common queries

### "OpenAI API key not configured"

Set environment variable:
```bash
export OPENAI_API_KEY='sk-...'
```

Or in Python:
```python
import os
os.environ['OPENAI_API_KEY'] = 'sk-...'
```

### ChromaDB database corruption

```bash
# Backup if possible
cp -r chroma_db chroma_db_backup

# Clear and rebuild
python build_knowledge_base.py --rebuild
```

## Best Practices

### 1. Quality Over Quantity
- Better to have 50 high-quality knowledge chunks than 500 mediocre ones
- Verify accuracy of all added knowledge
- Remove outdated or incorrect information

### 2. Consistent Terminology
- Use standard rodeo terminology
- Define acronyms and technical terms
- Be consistent with naming (e.g., "head catch" vs "head loop")

### 3. Source Attribution
- Always include source metadata
- Note date/year for time-sensitive info
- Credit expert contributors

### 4. Regular Updates
- Review and update knowledge quarterly
- Add new techniques and equipment as they emerge
- Remove deprecated information

### 5. Testing
- Test search with various question phrasings
- Verify responses cite correct sources
- Check responses at all skill levels

### 6. Organization
- Use clear category labels
- Separate beginner vs advanced content
- Group related topics together

## Advanced Usage

### Custom Retrieval Logic

Modify `rag_service.py` to customize retrieval:

```python
@staticmethod
def search_knowledge(query: str, filters: Dict = None):
    embedding = RAGService.create_embedding(query)

    # Add metadata filters
    where = {}
    if filters:
        if 'category' in filters:
            where['category'] = filters['category']
        if 'skill_level' in filters:
            where['skill_level'] = filters['skill_level']

    results = collection.query(
        query_embeddings=[embedding],
        where=where,  # Apply filters
        n_results=5
    )

    return process_results(results)
```

### Hybrid Search

Combine vector search with keyword matching:

```python
# First do vector search
vector_results = RAGService.search_knowledge(query)

# Then keyword filter
filtered_results = [
    r for r in vector_results
    if any(keyword in r['text'].lower() for keyword in['rope', 'header'])
]
```

### Multi-Language Support

Add language metadata:
```python
RAGService.add_knowledge(
    text="...",
    source="...",
    metadata={"language": "es"}
)
```

Filter by language in searches.

## Cost Considerations

**Embedding Costs** (OpenAI text-embedding-3-small):
- Building knowledge base (247 chunks × ~500 chars): ~$0.02
- Per query embedding: ~$0.00001
- Monthly cost (1000 queries/day): ~$0.30

**Extremely cost-effective compared to fine-tuning!**

**Storage**: ChromaDB is local and free.

## Migration and Backup

### Backup Knowledge Base

```bash
# Backup entire database
tar -czf chroma_db_backup_$(date +%Y%m%d).tar.gz chroma_db/

# Backup knowledge files
tar -czf knowledge_backup_$(date +%Y%m%d).tar.gz knowledge/
```

### Restore from Backup

```bash
# Stop server first
tar -xzf chroma_db_backup_20250101.tar.gz
```

### Export to JSON

```python
# Custom export script
import json
from rag_service import collection

data = collection.get(include=["documents", "metadatas"])

with open("knowledge_export.json", "w") as f:
    json.dump(data, f, indent=2)
```

## Next Steps

1. **Add domain-specific knowledge** - Rodeo events, venues, rules
2. **Include video transcripts** - Expert instruction videos
3. **Add competition data** - Past results, statistics
4. **User-generated content** - With moderation
5. **Multi-modal RAG** - Include images/diagrams

## Resources

- [ChromaDB Documentation](https://docs.trychroma.com/)
- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- [RAG Best Practices](https://www.pinecone.io/learn/retrieval-augmented-generation/)

---

**Need help?** Check the troubleshooting section or open an issue on GitHub.
