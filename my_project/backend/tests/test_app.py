import os
import sys
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi.testclient import TestClient

# Add the backend directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import app
from models.chat import ChatRequest


class TestApp:
    """Test cases for the main FastAPI application."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.client = TestClient(app)

    def test_health_check(self):
        """Test the health check endpoint."""
        response = self.client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data

    def test_chat_endpoint_valid_request(self):
        """Test the chat endpoint with a valid request."""
        with patch('app.get_relevant_chunks') as mock_get_chunks, \
             patch('app.get_agent_response') as mock_get_response:

            # Mock the retrieval and agent responses
            mock_get_chunks.return_value = ["Sample context chunk"]
            mock_get_response.return_value = "Sample response"

            request_data = {
                "query": "What is physical AI?",
                "user_id": "test_user",
                "session_id": "test_session"
            }

            response = self.client.post("/chat", json=request_data)
            assert response.status_code == 200

            data = response.json()
            assert "response" in data
            assert data["response"] == "Sample response"
            assert "source_chunks" in data

    def test_chat_endpoint_empty_query(self):
        """Test the chat endpoint with an empty query."""
        request_data = {
            "query": "",
            "user_id": "test_user",
            "session_id": "test_session"
        }

        response = self.client.post("/chat", json=request_data)
        assert response.status_code == 400

    def test_chat_endpoint_short_query(self):
        """Test the chat endpoint with a too-short query."""
        request_data = {
            "query": "hi",
            "user_id": "test_user",
            "session_id": "test_session"
        }

        response = self.client.post("/chat", json=request_data)
        assert response.status_code == 400

    def test_chat_endpoint_off_topic_query(self):
        """Test the chat endpoint with an off-topic query."""
        with patch('app.get_relevant_chunks') as mock_get_chunks, \
             patch('app.get_agent_response') as mock_get_response:

            # Mock to return an off-topic response
            mock_get_chunks.return_value = ["Sample context chunk"]
            mock_get_response.return_value = "I can only answer questions related to the technical book content. Please ask a question about physical AI, humanoid robotics, or related topics."

            request_data = {
                "query": "What's the weather like?",
                "user_id": "test_user",
                "session_id": "test_session"
            }

            response = self.client.post("/chat", json=request_data)
            assert response.status_code == 200

            data = response.json()
            assert "only answer questions related to the technical book content" in data["response"]
            assert data["confidence"] == 0.3  # Lower confidence for off-topic

    def test_chat_endpoint_internal_error(self):
        """Test the chat endpoint when an internal error occurs."""
        with patch('app.get_relevant_chunks') as mock_get_chunks:
            mock_get_chunks.side_effect = Exception("Internal error")

            request_data = {
                "query": "What is physical AI?",
                "user_id": "test_user",
                "session_id": "test_session"
            }

            response = self.client.post("/chat", json=request_data)
            assert response.status_code == 500