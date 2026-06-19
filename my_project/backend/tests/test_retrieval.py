import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.asyncio
async def test_get_relevant_chunks_returns_text_and_source(mock_chunks):
    with patch("retrieval.co.embed", new_callable=AsyncMock) as mock_embed:
        mock_embed.return_value = MagicMock(
            embeddings=MagicMock(float_=[[0.1] * 1024])
        )
        with patch("retrieval.qdrant_client.query_points", new_callable=AsyncMock) as mock_query:
            mock_query.return_value = MagicMock(
                points=[
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
            )
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
                points=[MagicMock(payload={"content": "success", "source_file": "test.mdx"}, score=0.95)]
            )
            result = await get_relevant_chunks("retry test")

    assert call_count == 3
    assert len(result) == 1
    assert result[0]["text"] == "success"


@pytest.mark.asyncio
async def test_get_relevant_chunks_fails_all_retries():
    from retrieval import get_relevant_chunks

    with patch("retrieval.co.embed", new_callable=AsyncMock) as mock_embed:
        mock_embed.side_effect = Exception("Persistent API failure")
        result = await get_relevant_chunks("failing query", max_retries=2)

    assert result == []


@pytest.mark.asyncio
async def test_get_relevant_chunks_filters_low_score():
    with patch("retrieval.co.embed", new_callable=AsyncMock) as mock_embed:
        mock_embed.return_value = MagicMock(
            embeddings=MagicMock(float_=[[0.1] * 1024])
        )
        with patch("retrieval.qdrant_client.query_points", new_callable=AsyncMock) as mock_query:
            mock_query.return_value = MagicMock(
                points=[
                    MagicMock(payload={"content": "high relevance"}, score=0.95),
                    MagicMock(payload={"content": "low relevance"}, score=0.10),
                ]
            )

            with patch("retrieval.Config.RELEVANCE_THRESHOLD", 0.3):
                from retrieval import get_relevant_chunks
                result = await get_relevant_chunks("test query")

    assert len(result) == 1
    assert result[0]["text"] == "high relevance"


@pytest.mark.asyncio
async def test_get_relevant_chunks_no_payload_field():
    with patch("retrieval.co.embed", new_callable=AsyncMock) as mock_embed:
        mock_embed.return_value = MagicMock(
            embeddings=MagicMock(float_=[[0.1] * 1024])
        )
        with patch("retrieval.qdrant_client.query_points", new_callable=AsyncMock) as mock_query:
            mock_query.return_value = MagicMock(
                points=[MagicMock(payload={"wrong_key": "data"}, score=0.8)]
            )
            from retrieval import get_relevant_chunks
            result = await get_relevant_chunks("test")

    assert result == []


@pytest.mark.asyncio
async def test_embed_query_raises_on_failure():
    from retrieval import embed_query, _embed_cache

    _embed_cache.clear()

    with patch("retrieval.co.embed", new_callable=AsyncMock) as mock_embed:
        mock_embed.side_effect = Exception("API error")
        with pytest.raises(Exception):
            await embed_query("failing-unique-test-query", max_retries=1)
