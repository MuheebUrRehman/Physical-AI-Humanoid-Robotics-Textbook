import os
import sys
from unittest.mock import Mock, patch, AsyncMock

import pytest

# Add the backend directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agent import get_agent_response, classify_content_relevance


class TestAgent:
    """Test cases for the agent module."""

    def test_classify_content_relevance_book_topic(self):
        """Test that book-related queries are classified as relevant."""
        relevant_queries = [
            "What is physical AI?",
            "Explain humanoid robotics",
            "How does robot learning work?",
            "What are neural networks in robotics?"
        ]

        for query in relevant_queries:
            result = classify_content_relevance(query)
            assert result is True, f"Query '{query}' should be classified as relevant"

    def test_classify_content_relevance_off_topic(self):
        """Test that off-topic queries are classified as not relevant."""
        off_topic_queries = [
            "What's the weather like today?",
            "Tell me a joke",
            "How do I make chocolate chip cookies?",
            "Who won the football game last night?"
        ]

        for query in off_topic_queries:
            result = classify_content_relevance(query)
            assert result is False, f"Query '{query}' should be classified as not relevant"

    @pytest.mark.asyncio
    async def test_get_agent_response_off_topic(self):
        """Test that off-topic queries return appropriate refusal message."""
        result = await get_agent_response("What's the weather like today?", [])
        assert "only answer questions related to the technical book content" in result.lower()

    @pytest.mark.asyncio
    async def test_get_agent_response_no_context(self):
        """Test response when no relevant context is available."""
        result = await get_agent_response("What is AI?", [])
        assert "don't have relevant information" in result.lower()

    @pytest.mark.asyncio
    async def test_get_agent_response_with_context(self):
        """Test response when context is available."""
        with patch('agent.client') as mock_client:
            # Mock the chat completion response
            mock_choice = Mock()
            mock_choice.message.content = "This is a sample response based on the context."
            mock_completion = Mock()
            mock_completion.choices = [mock_choice]
            mock_client.chat.completions.create.return_value = mock_completion

            result = await get_agent_response("What is AI?", ["AI stands for Artificial Intelligence."])

            # Should not contain off-topic message
            assert "only answer questions related to the technical book content" not in result.lower()
            assert "This is a sample response based on the context." == result