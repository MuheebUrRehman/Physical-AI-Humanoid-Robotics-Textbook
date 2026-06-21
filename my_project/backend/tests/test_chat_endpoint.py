import pytest
import json
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.asyncio
async def test_chat_endpoint_missing_query_field():
    from app import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/chat", json={"user_id": "u1", "session_id": "s1"})
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_chat_endpoint_empty_query():
    from app import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/chat", json={"query": "", "user_id": "u1", "session_id": "s1"})
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_chat_endpoint_valid_request_returns_stream():
    from app import app

    async def _empty_stream_events():
        if False:
            yield

    with patch("app.get_relevant_chunks", new_callable=AsyncMock) as mock_retrieval, \
         patch("app.Runner.run_streamed") as mock_run:

        mock_retrieval.return_value = []
        mock_stream = MagicMock()
        mock_stream.stream_events = _empty_stream_events
        mock_run.return_value = mock_stream

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/chat",
                json={"query": "What is ROS?", "user_id": "u1", "session_id": "s1"},
            )
            assert response.status_code == 200
            assert "text/event-stream" in response.headers["content-type"]


@pytest.mark.asyncio
async def test_chat_endpoint_harmful_query_rejected():
    from app import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/chat",
            json={
                "query": "<script>alert('xss')</script>",
                "user_id": "u1",
                "session_id": "s1",
            },
        )
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_chat_endpoint_streams_citations():
    from app import app

    mock_chunks = [
        {"text": "ROS 2 content.", "source": "module1/chapter1.mdx", "score": 0.95}
    ]

    async def _mock_stream_events():
        yield MagicMock(
            type="run_item_stream_event",
            result=MagicMock(final_output="ROS 2 is a framework."),
        )

    with patch("app.get_relevant_chunks", new_callable=AsyncMock) as mock_retrieval, \
         patch("app.Runner.run_streamed") as mock_run:

        mock_retrieval.return_value = mock_chunks
        mock_stream = MagicMock()
        mock_stream.stream_events = _mock_stream_events
        mock_run.return_value = mock_stream

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            async with client.stream(
                "POST",
                "/chat",
                json={"query": "What is ROS?", "user_id": "u1", "session_id": "s1"},
            ) as response:
                lines = []
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        lines.append(line)

                for line in lines:
                    data = json.loads(line[6:])
                    if data["type"] == "final":
                        content = data["content"]
                        assert "citations" in content
                        assert "module1/chapter1.mdx" in str(content["citations"])
