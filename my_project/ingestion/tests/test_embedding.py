import pytest
from unittest.mock import MagicMock, patch
from ingest_book import prepare_chunks_for_embedding, embed_text_chunks, VectorRecord


class TestPrepareChunksForEmbedding:
    def test_prepares_records(self):
        records = prepare_chunks_for_embedding(
            chunks=["chunk1", "chunk2"],
            source_file="docs/module1/chapter1.mdx",
            module="module1",
            chapter="chapter1",
        )
        assert len(records) == 2
        assert records[0].content == "chunk1"
        assert records[0].chunk_index == 0
        assert records[1].chunk_index == 1
        assert records[0].source_file == "docs/module1/chapter1.mdx"

    def test_empty_chunks(self):
        records = prepare_chunks_for_embedding([], "doc.mdx", "m1", "c1")
        assert records == []


class TestEmbedTextChunks:
    def test_embeds_records(self):
        mock_client = MagicMock()
        mock_client.embed.return_value = MagicMock(embeddings=[[0.1, 0.2], [0.3, 0.4]])

        records = [
            VectorRecord(id="1", vector=[], content="hello", source_file="doc.mdx", module="m1", chapter="c1", chunk_index=0),
            VectorRecord(id="2", vector=[], content="world", source_file="doc.mdx", module="m1", chapter="c1", chunk_index=1),
        ]

        result = embed_text_chunks(mock_client, records, model="embed-multilingual-v3.0")
        assert len(result) == 2
        assert result[0].vector == [0.1, 0.2]
        assert result[1].vector == [0.3, 0.4]

    def test_empty_records(self):
        mock_client = MagicMock()
        result = embed_text_chunks(mock_client, [], model="embed-multilingual-v3.0")
        assert result == []

    def test_embedding_failure(self):
        mock_client = MagicMock()
        mock_client.embed.side_effect = Exception("API Error")

        records = [
            VectorRecord(id="1", vector=[], content="hello", source_file="doc.mdx", module="m1", chapter="c1", chunk_index=0),
        ]

        with pytest.raises(Exception, match="API Error"):
            embed_text_chunks(mock_client, records)
