#!/usr/bin/env python3
"""
Build RodeoAI Knowledge Base

This script ingests rodeo knowledge from text files into the ChromaDB vector database.
Run this once to initialize the knowledge base, or re-run to update it.

Usage:
    python build_knowledge_base.py
"""

import os
import sys
from pathlib import Path
from rag_service import RAGService, chunk_text

# Knowledge sources configuration
KNOWLEDGE_SOURCES = [
    {
        "file": "knowledge/team_roping_basics.txt",
        "category": "technique",
        "skill_level": "all",
        "source": "Team Roping Basics Guide"
    },
    {
        "file": "knowledge/equipment_guide.txt",
        "category": "equipment",
        "skill_level": "all",
        "source": "Equipment Guide"
    },
    {
        "file": "knowledge/horse_training.txt",
        "category": "training",
        "skill_level": "intermediate",
        "source": "Horse Training Guide"
    }
]


def load_and_chunk_file(file_path: str, chunk_size: int = 500, overlap: int = 50):
    """
    Load a text file and split it into chunks.

    Args:
        file_path: Path to the text file
        chunk_size: Size of each chunk in characters
        overlap: Number of characters to overlap between chunks

    Returns:
        List of text chunks
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split into chunks
        chunks = chunk_text(content, chunk_size=chunk_size, overlap=overlap)
        print(f"✓ Loaded {file_path}: {len(chunks)} chunks created")
        return chunks

    except FileNotFoundError:
        print(f"✗ File not found: {file_path}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"✗ Error loading {file_path}: {e}", file=sys.stderr)
        return []


def build_knowledge_base(clear_existing: bool = False):
    """
    Build the knowledge base from all configured sources.

    Args:
        clear_existing: If True, clear existing knowledge before adding new
    """
    print("=" * 70)
    print("🤠 RodeoAI Knowledge Base Builder")
    print("=" * 70)
    print()

    # Clear existing knowledge if requested
    if clear_existing:
        print("⚠️  Clearing existing knowledge base...")
        try:
            RAGService.clear_knowledge_base()
            print("✓ Knowledge base cleared")
        except Exception as e:
            print(f"✗ Error clearing knowledge base: {e}", file=sys.stderr)
            return False
        print()

    # Check current stats
    stats = RAGService.get_collection_stats()
    print(f"Current knowledge base stats:")
    print(f"  - Total chunks: {stats.get('total_chunks', 0)}")
    print(f"  - Collection: {stats.get('collection_name', 'N/A')}")
    print(f"  - Database path: {stats.get('database_path', 'N/A')}")
    print()

    # Process each knowledge source
    total_chunks_added = 0
    total_sources = len(KNOWLEDGE_SOURCES)

    print(f"Processing {total_sources} knowledge sources...")
    print()

    for i, source in enumerate(KNOWLEDGE_SOURCES, 1):
        print(f"[{i}/{total_sources}] Processing: {source['source']}")
        print(f"  Category: {source['category']}")
        print(f"  Skill level: {source['skill_level']}")

        # Load and chunk the file
        file_path = os.path.join(os.path.dirname(__file__), source['file'])
        chunks = load_and_chunk_file(file_path)

        if not chunks:
            print(f"  ⚠️  Skipping {source['file']} - no content loaded")
            print()
            continue

        # Add each chunk to the knowledge base
        chunks_added = 0
        for chunk_idx, chunk in enumerate(chunks):
            try:
                # Add metadata including chunk position
                metadata = {
                    "chunk_index": chunk_idx,
                    "total_chunks": len(chunks),
                    "file": source['file']
                }

                doc_id = RAGService.add_knowledge(
                    text=chunk,
                    source=source['source'],
                    category=source['category'],
                    skill_level=source['skill_level'],
                    metadata=metadata
                )
                chunks_added += 1

                # Progress indicator for large files
                if chunks_added % 10 == 0:
                    print(f"  Progress: {chunks_added}/{len(chunks)} chunks added...")

            except Exception as e:
                print(f"  ✗ Error adding chunk {chunk_idx}: {e}", file=sys.stderr)
                continue

        print(f"  ✓ Added {chunks_added} chunks from {source['source']}")
        total_chunks_added += chunks_added
        print()

    # Final statistics
    print("=" * 70)
    print("📊 Knowledge Base Build Complete!")
    print("=" * 70)

    final_stats = RAGService.get_collection_stats()
    print(f"Total chunks added this session: {total_chunks_added}")
    print(f"Total chunks in database: {final_stats.get('total_chunks', 0)}")
    print()

    # Test search to verify
    print("🔍 Testing knowledge base with sample query...")
    test_query = "What rope should I use for heading?"
    results = RAGService.search_knowledge(test_query, top_k=3)

    if results:
        print(f"✓ Search test successful! Found {len(results)} results")
        print(f"\nTop result (score: {results[0]['score']:.3f}):")
        print(f"  {results[0]['text'][:200]}...")
    else:
        print("⚠️  Search test returned no results")

    print()
    print("✓ Knowledge base is ready for use!")
    print()

    return True


def interactive_mode():
    """Run in interactive mode with options."""
    print()
    print("RodeoAI Knowledge Base Builder")
    print()
    print("Options:")
    print("  1. Add knowledge (keep existing)")
    print("  2. Rebuild knowledge base (clear and add)")
    print("  3. View statistics only")
    print("  4. Test search")
    print("  5. Exit")
    print()

    choice = input("Enter your choice (1-5): ").strip()

    if choice == "1":
        build_knowledge_base(clear_existing=False)
    elif choice == "2":
        confirm = input("⚠️  This will delete all existing knowledge. Continue? (yes/no): ").strip().lower()
        if confirm == "yes":
            build_knowledge_base(clear_existing=True)
        else:
            print("Cancelled.")
    elif choice == "3":
        stats = RAGService.get_collection_stats()
        print("\n📊 Knowledge Base Statistics:")
        print(f"  Total chunks: {stats.get('total_chunks', 0)}")
        print(f"  Collection: {stats.get('collection_name', 'N/A')}")
        print(f"  Path: {stats.get('database_path', 'N/A')}")
        print()
    elif choice == "4":
        query = input("\nEnter search query: ").strip()
        if query:
            print(f"\n🔍 Searching for: {query}")
            results = RAGService.search_knowledge(query, top_k=5)

            if results:
                print(f"\n✓ Found {len(results)} results:\n")
                for i, result in enumerate(results, 1):
                    print(f"{i}. Score: {result['score']:.3f}")
                    print(f"   Source: {result['metadata'].get('source', 'Unknown')}")
                    print(f"   Category: {result['metadata'].get('category', 'Unknown')}")
                    print(f"   Text: {result['text'][:150]}...")
                    print()
            else:
                print("No results found.")
    elif choice == "5":
        print("Goodbye!")
        sys.exit(0)
    else:
        print("Invalid choice.")


def add_custom_knowledge():
    """Add custom knowledge interactively."""
    print("\n📝 Add Custom Knowledge\n")

    text = input("Enter knowledge text (or path to .txt file): ").strip()

    # Check if it's a file path
    if os.path.isfile(text):
        try:
            with open(text, 'r', encoding='utf-8') as f:
                text = f.read()
            print(f"✓ Loaded {len(text)} characters from file")
        except Exception as e:
            print(f"✗ Error reading file: {e}")
            return

    source = input("Source name: ").strip() or "Custom Knowledge"
    category = input("Category (technique/equipment/training/competition/general): ").strip() or "general"
    skill_level = input("Skill level (beginner/intermediate/advanced/professional/all): ").strip() or "all"

    print("\nProcessing...")

    # Chunk if needed
    if len(text) > 500:
        chunks = chunk_text(text, chunk_size=500, overlap=50)
        print(f"Text split into {len(chunks)} chunks")
    else:
        chunks = [text]

    # Add chunks
    added = 0
    for chunk in chunks:
        try:
            RAGService.add_knowledge(
                text=chunk,
                source=source,
                category=category,
                skill_level=skill_level
            )
            added += 1
        except Exception as e:
            print(f"✗ Error adding chunk: {e}")

    print(f"\n✓ Added {added} chunks to knowledge base!")


if __name__ == "__main__":
    # Check if running with command-line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--rebuild":
            print("Rebuilding knowledge base from scratch...")
            build_knowledge_base(clear_existing=True)
        elif sys.argv[1] == "--add":
            print("Adding knowledge to existing database...")
            build_knowledge_base(clear_existing=False)
        elif sys.argv[1] == "--stats":
            stats = RAGService.get_collection_stats()
            print("\n📊 Knowledge Base Statistics:")
            print(f"  Total chunks: {stats.get('total_chunks', 0)}")
            print(f"  Collection: {stats.get('collection_name', 'N/A')}")
            print(f"  Path: {stats.get('database_path', 'N/A')}")
            print()
        elif sys.argv[1] == "--custom":
            add_custom_knowledge()
        elif sys.argv[1] == "--help":
            print("\nRodeoAI Knowledge Base Builder")
            print("\nUsage:")
            print("  python build_knowledge_base.py              # Interactive mode")
            print("  python build_knowledge_base.py --rebuild    # Clear and rebuild")
            print("  python build_knowledge_base.py --add        # Add to existing")
            print("  python build_knowledge_base.py --stats      # View statistics")
            print("  python build_knowledge_base.py --custom     # Add custom knowledge")
            print("  python build_knowledge_base.py --help       # Show this help")
            print()
        else:
            print(f"Unknown argument: {sys.argv[1]}")
            print("Use --help for usage information")
    else:
        # Interactive mode
        interactive_mode()
