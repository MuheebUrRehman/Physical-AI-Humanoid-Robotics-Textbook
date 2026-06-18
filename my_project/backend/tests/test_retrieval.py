import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.asyncio
async def test_get_relevant_chunks_returns_text_and_source(mock_chunks):
    """Verify chunks include text, source, module, and chapter keys."""
    with patch("retrieval.co.embed", new_callable=AsyncMock) as mock_embed:
        mock_embed.return_value = MagicMock(
            embeddings=MagicMock(float_=[[0.1] * 1024])
        )
        with patch("retrieval.qdrant_client.query_points", new_callable=AsyncMock) as mock_query:
            mock_query.return_value = MagicMock(
                points=[
                    MagicMock(
                        payload={
                            "text": c["text"],
                            "source_file": c["source"],
                            "module": c["module"],
                            "chapter": c["chapter"],
                        }
                    )
                    for c in mock_chunks
                ]
            )
            from retrieval import get_relevant_chunks
            result = await get_relevant_chunks("What is ROS 2?")

    assert len(result) == 3
    for i, chunk in enumerate(result):
        assert isinstance(chunk, dict)
        assert "text" in chunk
        assert "source" in chunk
        assert chunk["text"] == mock_chunks[i]["text"]
        assert chunk["source"] == mock_chunks[i]["source"]


@pytest.mark.asyncio
async def test_get_relevant_chunks_empty_results():
    """Verify empty list returned when Qdrant returns no points."""
    with patch("retrieval.co.embed", new_callable=AsyncMock) as mock_embed:
        mock_embed.return_value = MagicMock(
            embeddings=MagicMock(float_=[[0.1] * 1024])
        )
        with patch("retrieval.qdrant_client.query_points", new_callable=AsyncMock) as mock_query:
            mock_query.return_value = MagicMock(points=[])
            from retrieval import get_relevant_chunks
            result = await get_relevant_chunks("empty query")

    assert result == []


@pytest.mark.asyncio
async def test_get_relevant_chunks_retries_on_error():
    """Verify retry logic: 2 failures then success on 3rd attempt."""
    from retrieval import get_relevant_chunks

    call_count = 0

    class FlakyEmbed:
        async def embed(self, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary API error")
            return MagicMock(embeddings=MagicMock(float_=[[0.1] * 1024]))

    flaky = FlakyEmbed()
    with patch("retrieval.co.embed", flaky.embed):
        with patch("retrieval.qdrant_client.query_points", new_callable=AsyncMock) as mock_query:
            mock_query.return_value = MagicMock(
                points=[MagicMock(payload={"text": "success", "source_file": "test.mdx"})]
            )
            result = await get_relevant_chunks("retry test")

    assert call_count == 3
    assert len(result) == 1
    assert result[0]["text"] == "success"


@pytest.mark.asyncio
async def test_get_relevant_chunks_fails_all_retries():
    """Verify empty list returned after all retries are exhausted."""
    from retrieval import get_relevant_chunks

    with patch("retrieval.co.embed", new_callable=AsyncMock) as mock_embed:
        mock_embed.side_effect = Exception("Persistent API failure")
        result = await get_relevant_chunks("failing query", max_retries=2)

    assert result == []
