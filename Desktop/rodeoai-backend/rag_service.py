"""RAG (Retrieval Augmented Generation) Service for RodeoAI.

This module provides semantic search over rodeo knowledge using ChromaDB
vector database and OpenAI embeddings.
"""

import os
import sys
from typing import List, Dict, Optional
from openai import OpenAI
import chromadb
from chromadb.config import Settings
import json

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize ChromaDB client
# Store in Desktop/rodeoai-backend/chroma_db directory
db_path = os.path.join(os.path.dirname(__file__), "chroma_db")
chroma_client = chromadb.PersistentClient(path=db_path)

# Get or create collection for rodeo knowledge
collection = chroma_client.get_or_create_collection(
    name="rodeo_knowledge",
    metadata={"description": "Rodeo expertise knowledge base"}
)


class RAGService:
    """Service for Retrieval Augmented Generation."""

    @staticmethod
    def create_embedding(text: str) -> List[float]:
        """
        Create vector embedding for text using OpenAI.

        Args:
            text: Text to embed

        Returns:
            List of floats representing the embedding vector
        """
        try:
            response = openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error creating embedding: {e}", file=sys.stderr)
            # Return zero vector as fallback
            return [0.0] * 1536

    @staticmethod
    def search_knowledge(
        query: str,
        top_k: int = 5,
        min_score: float = 0.5
    ) -> List[Dict]:
        """
        Search vector database for relevant rodeo knowledge.

        Args:
            query: User's question
            top_k: Number of results to return
            min_score: Minimum similarity score (0-1)

        Returns:
            List of relevant knowledge chunks with metadata
        """
        try:
            # Create embedding for query
            query_embedding = RAGService.create_embedding(query)

            # Search ChromaDB
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["documents", "metadatas", "distances"]
            )

            # Format results
            chunks = []
            if results and results['documents']:
                for i in range(len(results['documents'][0])):
                    # Convert distance to similarity score (lower distance = higher similarity)
                    # ChromaDB uses L2 distance, convert to similarity
                    distance = results['distances'][0][i] if results['distances'] else 1.0
                    similarity = 1.0 / (1.0 + distance)

                    if similarity >= min_score:
                        chunks.append({
                            "text": results['documents'][0][i],
                            "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                            "score": similarity
                        })

            return chunks

        except Exception as e:
            print(f"Error searching knowledge base: {e}", file=sys.stderr)
            return []

    @staticmethod
    def augmented_response(
        question: str,
        conversation_history: List[Dict],
        user_skill_level: str = "intermediate",
        stream: bool = True
    ):
        """
        Generate AI response using RAG.

        Args:
            question: User's current question
            conversation_history: Previous messages in conversation
            user_skill_level: User's skill level (beginner, intermediate, advanced, professional)
            stream: Whether to stream the response

        Yields:
            Response chunks if streaming, otherwise returns complete response
        """
        # Search for relevant knowledge
        relevant_chunks = RAGService.search_knowledge(question, top_k=3)

        # Build context from retrieved knowledge
        if relevant_chunks:
            context_parts = []
            for i, chunk in enumerate(relevant_chunks, 1):
                source = chunk['metadata'].get('source', 'Rodeo Knowledge Base')
                category = chunk['metadata'].get('category', '')
                context_parts.append(
                    f"[Source {i}: {source}]\n{chunk['text']}\n"
                )
            context = "\n".join(context_parts)
        else:
            context = "No specific knowledge found. Use general rodeo expertise."

        # Build augmented system prompt
        system_message = f"""You are RodeoAI, an expert assistant for team roping and rodeo.

User's skill level: {user_skill_level}

RELEVANT RODEO KNOWLEDGE:
{context}

GUIDELINES:
- Base your answers on the provided knowledge when relevant
- Cite sources when referencing specific information (e.g., "According to...")
- Adjust technical depth based on user's skill level:
  * Beginner: Simple explanations, basic techniques
  * Intermediate: More detail, assume some experience
  * Advanced: Technical depth, competitive strategies
  * Professional: Expert-level insights, nuanced advice
- If the knowledge doesn't fully answer the question, supplement with your general rodeo expertise
- Be practical, actionable, and encouraging
- Focus on safety when relevant
"""

        # Build messages for OpenAI
        messages = [{"role": "system", "content": system_message}]

        # Add conversation history (limit to last 10 messages to control token usage)
        if conversation_history:
            messages.extend(conversation_history[-10:])

        # Add current question
        messages.append({"role": "user", "content": question})

        # Generate response
        try:
            if not openai_client.api_key:
                yield "Error: OpenAI API key not configured. Please set OPENAI_API_KEY environment variable."
                return

            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                stream=stream,
                max_tokens=1500,
                temperature=0.7
            )

            if stream:
                # Yield chunks for streaming
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
            else:
                # Return complete response
                yield response.choices[0].message.content

        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            print(error_msg, file=sys.stderr)
            yield f"I apologize, but I encountered an error: {str(e)}"

    @staticmethod
    def add_knowledge(
        text: str,
        source: str,
        category: str = "general",
        skill_level: str = "all",
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Add new knowledge to the vector database.

        Args:
            text: Knowledge text to add
            source: Source of the knowledge (book, website, expert, etc.)
            category: Category (equipment, technique, training, competition, etc.)
            skill_level: Target skill level (beginner, intermediate, advanced, professional, all)
            metadata: Additional metadata

        Returns:
            Document ID
        """
        try:
            # Create embedding
            embedding = RAGService.create_embedding(text)

            # Generate unique ID
            import hashlib
            text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
            doc_id = f"{category}_{text_hash}"

            # Prepare metadata
            doc_metadata = {
                "source": source,
                "category": category,
                "skill_level": skill_level,
                **(metadata or {})
            }

            # Add to collection
            collection.add(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[text],
                metadatas=[doc_metadata]
            )

            print(f"✓ Added knowledge: {doc_id}", file=sys.stderr)
            return doc_id

        except Exception as e:
            print(f"Error adding knowledge: {e}", file=sys.stderr)
            raise

    @staticmethod
    def get_collection_stats() -> Dict:
        """Get statistics about the knowledge base."""
        try:
            count = collection.count()
            return {
                "total_chunks": count,
                "collection_name": collection.name,
                "database_path": db_path
            }
        except Exception as e:
            print(f"Error getting stats: {e}", file=sys.stderr)
            return {"error": str(e)}

    @staticmethod
    def clear_knowledge_base():
        """Clear all knowledge from the database. Use with caution!"""
        try:
            chroma_client.delete_collection(name="rodeo_knowledge")
            print("✓ Knowledge base cleared", file=sys.stderr)
        except Exception as e:
            print(f"Error clearing knowledge base: {e}", file=sys.stderr)
            raise


# Utility function for chunking text
def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Split text into overlapping chunks.

    Args:
        text: Text to chunk
        chunk_size: Size of each chunk in characters
        overlap: Number of characters to overlap between chunks

    Returns:
        List of text chunks
    """
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        # Try to break at sentence boundaries
        if end < len(text):
            # Look for last period in chunk
            last_period = chunk.rfind('.')
            if last_period > chunk_size * 0.7:  # At least 70% through
                end = start + last_period + 1
                chunk = text[start:end]

        chunks.append(chunk.strip())
        start = end - overlap

    return chunks


if __name__ == "__main__":
    # Test the RAG service
    print("Testing RAG Service...")

    # Check stats
    stats = RAGService.get_collection_stats()
    print(f"Knowledge base stats: {stats}")

    # Test search
    if stats.get("total_chunks", 0) > 0:
        print("\nTesting search...")
        results = RAGService.search_knowledge("What rope should I use for heading?")
        print(f"Found {len(results)} results")
        for i, result in enumerate(results, 1):
            print(f"\nResult {i}:")
            print(f"Score: {result['score']:.3f}")
            print(f"Text: {result['text'][:200]}...")
