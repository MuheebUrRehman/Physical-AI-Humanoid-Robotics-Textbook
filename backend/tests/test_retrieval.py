import os
import sys
from unittest.mock import Mock, patch, AsyncMock

import pytest

# Add the backend directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from retrieval import get_relevant_chunks, embed_query


class TestRetrieval:
    """Test cases for the retrieval module."""

    @pytest.mark.asyncio
    async def test_get_relevant_chunks_success(self):
        """Test successful retrieval of relevant chunks."""
        # Mock the Cohere and Qdrant clients
        with patch('retrieval.co') as mock_cohere, \
             patch('retrieval.qdrant_client') as mock_qdrant:

            # Setup mock responses
            mock_embedding_response = Mock()
            mock_embedding_response.embeddings = [[0.1, 0.2, 0.3]]
            mock_cohere.embed.return_value = mock_embedding_response

            mock_search_result = [
                Mock(),
                Mock()
            ]
            mock_search_result[0].payload = {"text": "Sample chunk 1"}
            mock_search_result[1].payload = {"text": "Sample chunk 2"}
            mock_qdrant.search.return_value = mock_search_result

            # Test the function
            result = await get_relevant_chunks("test query")

            # Assertions
            assert len(result) == 2
            assert "Sample chunk 1" in result
            assert "Sample chunk 2" in result

    @pytest.mark.asyncio
    async def test_get_relevant_chunks_with_retry(self):
        """Test that the function retries on failure."""
        with patch('retrieval.co') as mock_cohere, \
             patch('retrieval.qdrant_client') as mock_qdrant:

            # Setup to fail on first attempt, succeed on second
            mock_cohere.embed.side_effect = [Exception("API Error"), Mock(embeddings=[[0.1, 0.2, 0.3]])]

            mock_search_result = [Mock()]
            mock_search_result[0].payload = {"text": "Sample chunk after retry"}
            mock_qdrant.search.return_value = mock_search_result

            result = await get_relevant_chunks("test query", max_retries=2)

            assert len(result) == 1
            assert "Sample chunk after retry" in result

    @pytest.mark.asyncio
    async def test_embed_query_success(self):
        """Test successful embedding of a query."""
        with patch('retrieval.co') as mock_cohere:
            mock_embedding_response = Mock()
            mock_embedding_response.embeddings = [[0.1, 0.2, 0.3]]
            mock_cohere.embed.return_value = mock_embedding_response

            result = await embed_query("test query")

            assert result == [0.1, 0.2, 0.3]

    @pytest.mark.asyncio
    async def test_embed_query_with_retry(self):
        """Test that embedding function retries on failure."""
        with patch('retrieval.co') as mock_cohere:
            mock_cohere.embed.side_effect = [Exception("API Error"), Mock(embeddings=[[0.4, 0.5, 0.6]])]

            result = await embed_query("test query", max_retries=2)

            assert result == [0.4, 0.5, 0.6]