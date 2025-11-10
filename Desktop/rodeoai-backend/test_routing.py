#!/usr/bin/env python3
"""
Test script for TAURUS intelligent model routing
Demonstrates how different query types are routed to appropriate models
"""

from taurus_routing import TaurusRouter

# Test queries representing different complexity levels and tool requirements
test_queries = [
    # Simple queries (should use gpt-4o-mini)
    {
        "query": "What is team roping?",
        "expected": "gpt-4o-mini",
        "category": "Simple Q&A"
    },
    {
        "query": "How do I tie a honda knot?",
        "expected": "gpt-4o-mini",
        "category": "Simple Q&A"
    },

    # Tool-requiring queries (should use gpt-4o)
    {
        "query": "Can you help me plan a route from Dallas to Denver with horse-friendly stops?",
        "expected": "gpt-4o",
        "category": "Travel Planning (Tool)"
    },
    {
        "query": "Upload my horse Bo's vet records and tell me when his next vaccination is due",
        "expected": "gpt-4o",
        "category": "File Analysis (Tool)"
    },
    {
        "query": "Analyze my performance stats from last month's rodeos",
        "expected": "gpt-4o",
        "category": "Analytics (Tool)"
    },

    # Complex queries (should use gpt-4o or gpt-4)
    {
        "query": "Create a comprehensive 6-month training program for my heading horse, considering biomechanics and injury prevention",
        "expected": "gpt-4",
        "category": "Complex Planning"
    },
    {
        "query": "What's the best strategy for qualifying for the NFR with only 3 months left in the season?",
        "expected": "gpt-4",
        "category": "Advanced Strategy"
    },
    {
        "query": "Compare the benefits of a 4-horse slant load versus a straight load trailer for cross-country travel",
        "expected": "gpt-4o",
        "category": "Comparison Analysis"
    },

    # Multi-step queries (should use gpt-4o)
    {
        "query": "Walk me through the process of conditioning a young rope horse, step by step",
        "expected": "gpt-4o",
        "category": "Multi-step Guide"
    },

    # Business/legal queries (should use gpt-4)
    {
        "query": "What should I include in a sponsorship contract for my rodeo career?",
        "expected": "gpt-4",
        "category": "Legal/Business"
    },

    # Multiple tool categories (should use gpt-4o)
    {
        "query": "Help me sell my horse - upload photos and create a listing, then calculate shipping costs to various states",
        "expected": "gpt-4o",
        "category": "Multi-tool"
    }
]

def test_routing():
    """Test the routing system with various queries"""
    print("=" * 80)
    print("TAURUS INTELLIGENT MODEL ROUTING - TEST RESULTS")
    print("=" * 80)
    print()

    correct = 0
    total = len(test_queries)

    for i, test in enumerate(test_queries, 1):
        print(f"\n{i}. {test['category']}")
        print(f"   Query: \"{test['query']}\"")
        print(f"   Expected: {test['expected']}")

        # Analyze query
        analysis = TaurusRouter.analyze_query(test['query'])
        selected_model = analysis['recommended_model']

        print(f"   Selected: {selected_model}")
        print(f"   Complexity: {analysis['complexity_score']}/10")
        print(f"   Tools: {', '.join(analysis['tool_categories']) if analysis['tool_categories'] else 'None'}")
        print(f"   Reasoning: {analysis['reasoning']}")

        # Check if matches expected (allow some flexibility)
        match = selected_model == test['expected']
        if not match:
            # Allow gpt-4o where gpt-4 was expected or vice versa (both advanced)
            if (test['expected'] in ['gpt-4', 'gpt-4o'] and
                selected_model in ['gpt-4', 'gpt-4o']):
                match = True
                print("   ✓ ACCEPTABLE (advanced model selected)")

        if match:
            print("   ✓ CORRECT")
            correct += 1
        else:
            print("   ✗ MISMATCH")

        print("-" * 80)

    print(f"\n\nTest Results: {correct}/{total} correct ({correct/total*100:.1f}%)")
    print("=" * 80)

if __name__ == "__main__":
    test_routing()
