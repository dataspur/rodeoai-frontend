"""
TAURUS Intelligent Model Routing
Analyzes user queries to determine optimal OpenAI model selection
"""

import re
from typing import Literal

ModelType = Literal["gpt-4o-mini", "gpt-4o", "gpt-4"]


class TaurusRouter:
    """Intelligent routing system for TAURUS model selection"""

    # Keywords that indicate advanced tool requirements
    TOOL_KEYWORDS = {
        'file': ['upload', 'document', 'file', 'vet record', 'registration', 'training log', 'pdf'],
        'travel': ['route', 'travel', 'trip', 'map', 'directions', 'fuel', 'cost', 'miles', 'distance'],
        'analytics': ['analyze', 'stats', 'statistics', 'performance', 'track', 'chart', 'graph', 'data'],
        'marketplace': ['buy', 'sell', 'listing', 'horse sale', 'trailer sale', 'equipment'],
        'entry': ['enter', 'registration', 'sign up for', 'rodeo entry', 'compete'],
    }

    # Keywords indicating complex reasoning requirements
    COMPLEXITY_KEYWORDS = {
        'strategy': ['strategy', 'plan', 'approach', 'tactics', 'optimize'],
        'comparison': ['compare', 'versus', 'vs', 'difference', 'better', 'best'],
        'multi_step': ['step by step', 'how do i', 'guide me', 'walk me through', 'process'],
        'analysis': ['why', 'explain', 'analyze', 'evaluate', 'assess'],
        'calculation': ['calculate', 'compute', 'estimate', 'how much', 'cost'],
    }

    # Advanced topics requiring GPT-4
    ADVANCED_TOPICS = [
        'nfr', 'national finals', 'championship',
        'training program', 'conditioning program',
        'injury', 'recovery', 'rehabilitation',
        'breeding', 'genetics', 'bloodline',
        'business', 'sponsorship', 'marketing',
        'legal', 'contract', 'insurance'
    ]

    @staticmethod
    def analyze_query(message: str) -> dict:
        """
        Analyze user query for complexity and tool requirements

        Returns:
            dict with analysis results including:
                - requires_tools: bool
                - tool_categories: list
                - complexity_score: int (0-10)
                - recommended_model: ModelType
        """
        message_lower = message.lower()

        # Detect tool requirements
        requires_tools = False
        tool_categories = []

        for category, keywords in TaurusRouter.TOOL_KEYWORDS.items():
            if any(keyword in message_lower for keyword in keywords):
                requires_tools = True
                tool_categories.append(category)

        # Calculate complexity score
        complexity_score = TaurusRouter._calculate_complexity(message_lower)

        # Determine recommended model
        recommended_model = TaurusRouter._select_model(
            complexity_score,
            requires_tools,
            tool_categories,
            message_lower
        )

        return {
            'requires_tools': requires_tools,
            'tool_categories': tool_categories,
            'complexity_score': complexity_score,
            'recommended_model': recommended_model,
            'reasoning': TaurusRouter._explain_selection(
                complexity_score,
                requires_tools,
                tool_categories,
                recommended_model
            )
        }

    @staticmethod
    def _calculate_complexity(message: str) -> int:
        """Calculate complexity score from 0-10"""
        score = 0

        # Length factor (longer queries often more complex)
        word_count = len(message.split())
        if word_count > 50:
            score += 3
        elif word_count > 30:
            score += 2
        elif word_count > 15:
            score += 1

        # Multiple questions or complex sentence structure
        question_count = message.count('?')
        score += min(question_count, 2)

        # Multiple clauses indicate complexity
        comma_count = message.count(',')
        if comma_count >= 3:
            score += 1

        # Complexity keywords (weight by category)
        complexity_weights = {
            'strategy': 2,
            'comparison': 2,
            'multi_step': 2,
            'analysis': 2,
            'calculation': 1,
        }

        for category, keywords in TaurusRouter.COMPLEXITY_KEYWORDS.items():
            if any(keyword in message for keyword in keywords):
                score += complexity_weights.get(category, 1)

        # Advanced topic detection (stronger weight)
        for topic in TaurusRouter.ADVANCED_TOPICS:
            if topic in message:
                score += 3
                break

        # Technical terminology (strong indicator of complexity)
        technical_terms = ['biomechanics', 'veterinary', 'pathology', 'anatomy',
                          'physiology', 'therapeutic', 'diagnostic', 'comprehensive',
                          'conditioning', 'rehabilitation', 'contract', 'legal']
        if any(term in message for term in technical_terms):
            score += 3

        return min(score, 10)

    @staticmethod
    def _select_model(
        complexity_score: int,
        requires_tools: bool,
        tool_categories: list,
        message: str
    ) -> ModelType:
        """Select the optimal model based on analysis"""

        # GPT-4 for very high complexity or advanced topics
        if complexity_score >= 7:
            return "gpt-4"

        # GPT-4 for critical/advanced topics (even with lower complexity)
        for topic in TaurusRouter.ADVANCED_TOPICS:
            if topic in message and complexity_score >= 3:
                return "gpt-4"

        # GPT-4o for ANY tool use (tools benefit from better reasoning)
        if requires_tools:
            return "gpt-4o"

        # GPT-4o for moderate complexity
        if complexity_score >= 4:
            return "gpt-4o"

        # GPT-4o for multiple tool categories (redundant now but kept for clarity)
        if len(tool_categories) >= 2:
            return "gpt-4o"

        # GPT-4o-mini only for simple, non-tool queries
        return "gpt-4o-mini"

    @staticmethod
    def _explain_selection(
        complexity_score: int,
        requires_tools: bool,
        tool_categories: list,
        model: ModelType
    ) -> str:
        """Explain why a particular model was selected"""
        reasons = []

        if complexity_score >= 8:
            reasons.append("high complexity query")
        elif complexity_score >= 6:
            reasons.append("moderate complexity")
        elif complexity_score <= 3:
            reasons.append("simple query")

        if requires_tools:
            reasons.append(f"requires tools: {', '.join(tool_categories)}")

        if not reasons:
            reasons.append("standard query")

        return f"Selected {model}: {', '.join(reasons)}"


# Convenience function for easy import
def select_model_for_query(message: str) -> tuple[ModelType, dict]:
    """
    Select the best model for a given query

    Args:
        message: The user's query

    Returns:
        Tuple of (model_name, analysis_details)
    """
    analysis = TaurusRouter.analyze_query(message)
    return analysis['recommended_model'], analysis
