import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient, ASGITransport


@pytest.mark.asyncio
async def test_chatkit_session_creation():
    from app import app

    mock_thread = MagicMock()
    mock_thread.id = "thread-123"

    mock_server = MagicMock()
    mock_server.store.create_thread = AsyncMock(return_value=mock_thread)
    app.state.chatkit_server = mock_server

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/chatkit/session",
            json={"user_id": "student1"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "client_secret" in data
        assert data["thread_id"] == "thread-123"
        assert data["user_id"] == "student1"


@pytest.mark.asyncio
async def test_chatkit_session_without_server():
    from app import app

    app.state.chatkit_server = None

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/chatkit/session",
            json={"user_id": "student1"},
        )
        assert response.status_code == 500


@pytest.mark.asyncio
async def test_chatkit_refresh():
    from app import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/chatkit/refresh",
            headers={"X-User-ID": "student1"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "client_secret" in data
        assert "user_id" in data
        assert data["user_id"] == "student1"


@pytest.mark.asyncio
async def test_chatkit_user():
    from app import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/chatkit/user",
            headers={"X-User-ID": "student1"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "student1"
        assert data["name"] == "Physical AI Student"


@pytest.mark.asyncio
async def test_chatkit_user_default():
    from app import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/chatkit/user")
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "anonymous_student"
