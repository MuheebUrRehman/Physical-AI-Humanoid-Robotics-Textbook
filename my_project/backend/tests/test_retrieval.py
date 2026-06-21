import pytest
from unittest.mock import AsyncMock, MagicMock, patch


def _mock_cohere(embed_return=None):
    """Create a mock Cohere client with configurable embed."""
    mock = MagicMock()
    if embed_return is None:
        embed_return = MagicMock(embeddings=MagicMock(float_=[[0.1] * 1024]))
    mock.embed = AsyncMock(return_value=embed_return)
    return mock


def _mock_qdrant(points=None):
    """Create a mock Qdrant client with configurable query_points."""
    mock = MagicMock()
    if points is None:
        points = []
    mock.query_points = AsyncMock(return_value=MagicMock(points=points))
    return mock


@pytest.mark.asyncio
async def test_get_relevant_chunks_returns_text_and_source(mock_chunks):
    embed_return = MagicMock(embeddings=MagicMock(float_=[[0.1] * 1024]))
    qdrant_points = [
        MagicMock(
            payload={
                "content": c["text"],
                "source_file": c["source"],
                "module": c["module"],
                "chapter": c["chapter"],
            },
            score=0.92,
        )
        for c in mock_chunks
    ]

    with patch("retrieval._get_cohere_client", return_value=_mock_cohere(embed_return)), \
         patch("retrieval._get_qdrant_client", return_value=_mock_qdrant(qdrant_points)):
        from retrieval import get_relevant_chunks
        result = await get_relevant_chunks("What is ROS 2?")

    assert len(result) == 3
    for i, chunk in enumerate(result):
        assert isinstance(chunk, dict)
        assert "text" in chunk
        assert "source" in chunk
        assert "score" in chunk
        assert chunk["text"] == mock_chunks[i]["text"]
        assert chunk["source"] == mock_chunks[i]["source"]
        assert chunk["score"] == 0.92


@pytest.mark.asyncio
async def test_get_relevant_chunks_empty_results():
    with patch("retrieval._get_cohere_client", return_value=_mock_cohere()), \
         patch("retrieval._get_qdrant_client", return_value=_mock_qdrant([])):
        from retrieval import get_relevant_chunks
        result = await get_relevant_chunks("empty query")

    assert result == []


@pytest.mark.asyncio
async def test_get_relevant_chunks_retries_on_error():
    call_count = 0

    class FlakyEmbed:
        async def embed(self, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary API error")
            return MagicMock(embeddings=MagicMock(float_=[[0.1] * 1024]))

    flaky_client = MagicMock()
    flaky_client.embed = FlakyEmbed().embed

    with patch("retrieval._get_cohere_client", return_value=flaky_client), \
         patch("retrieval._get_qdrant_client", return_value=_mock_qdrant(
             [MagicMock(payload={"content": "success", "source_file": "test.mdx"}, score=0.95)]
         )):
        from retrieval import get_relevant_chunks
        result = await get_relevant_chunks("retry test")

    assert call_count == 3
    assert len(result) == 1
    assert result[0]["text"] == "success"


@pytest.mark.asyncio
async def test_get_relevant_chunks_fails_all_retries():
    failing_client = MagicMock()
    failing_client.embed = AsyncMock(side_effect=Exception("Persistent API failure"))

    with patch("retrieval._get_cohere_client", return_value=failing_client):
        from retrieval import get_relevant_chunks
        result = await get_relevant_chunks("failing query", max_retries=2)

    assert result == []


@pytest.mark.asyncio
async def test_get_relevant_chunks_filters_low_score():
    embed_return = MagicMock(embeddings=MagicMock(float_=[[0.1] * 1024]))
    qdrant_points = [
        MagicMock(payload={"content": "high relevance"}, score=0.95),
        MagicMock(payload={"content": "low relevance"}, score=0.10),
    ]

    with patch("retrieval._get_cohere_client", return_value=_mock_cohere(embed_return)), \
         patch("retrieval._get_qdrant_client", return_value=_mock_qdrant(qdrant_points)), \
         patch("retrieval.Config.RELEVANCE_THRESHOLD", 0.3):
        from retrieval import get_relevant_chunks
        result = await get_relevant_chunks("test query")

    assert len(result) == 1
    assert result[0]["text"] == "high relevance"


@pytest.mark.asyncio
async def test_get_relevant_chunks_no_payload_field():
    with patch("retrieval._get_cohere_client", return_value=_mock_cohere()), \
         patch("retrieval._get_qdrant_client", return_value=_mock_qdrant(
             [MagicMock(payload={"wrong_key": "data"}, score=0.8)]
         )):
        from retrieval import get_relevant_chunks
        result = await get_relevant_chunks("test")

    assert result == []


@pytest.mark.asyncio
async def test_embed_query_raises_on_failure():
    from retrieval import embed_query, _embed_cache

    _embed_cache.clear()

    failing_client = MagicMock()
    failing_client.embed = AsyncMock(side_effect=Exception("API error"))

    with patch("retrieval._get_cohere_client", return_value=failing_client):
        with pytest.raises(Exception):
            await embed_query("failing-unique-test-query", max_retries=1)
