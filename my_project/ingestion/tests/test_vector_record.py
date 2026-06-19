import pytest
from datetime import datetime, timezone
from ingest_book import VectorRecord


class TestVectorRecord:
    def test_creation(self):
        record = VectorRecord(
            id="test-id",
            vector=[0.1, 0.2, 0.3],
            content="test content",
            source_file="docs/module1/chapter1.mdx",
            module="module1",
            chapter="chapter1",
            chunk_index=0,
        )
        assert record.id == "test-id"
        assert record.vector == [0.1, 0.2, 0.3]
        assert record.content == "test content"
        assert record.source_file == "docs/module1/chapter1.mdx"
        assert record.module == "module1"
        assert record.chapter == "chapter1"
        assert record.chunk_index == 0

    def test_to_payload(self):
        record = VectorRecord(
            id="test-id",
            vector=[0.1, 0.2, 0.3],
            content="test content",
            source_file="docs/module1/chapter1.mdx",
            module="module1",
            chapter="chapter1",
            chunk_index=0,
        )
        payload = record.to_payload()
        assert payload["content"] == "test content"
        assert payload["source_file"] == "docs/module1/chapter1.mdx"
        assert payload["module"] == "module1"
        assert payload["chapter"] == "chapter1"
        assert payload["chunk_index"] == 0
        assert "created_at" in payload

    def test_to_qdrant_point(self):
        record = VectorRecord(
            id="test-id",
            vector=[0.1, 0.2, 0.3],
            content="test",
            source_file="doc.mdx",
            module="m1",
            chapter="c1",
            chunk_index=0,
        )
        point = record.to_qdrant_point()
        assert point["id"] == "test-id"
        assert point["vector"] == [0.1, 0.2, 0.3]
        assert point["payload"]["content"] == "test"

    def test_from_text_chunk(self):
        record = VectorRecord.from_text_chunk(
            text_chunk="hello world",
            source_file="docs/module1/chapter1.mdx",
            module="module1",
            chapter="chapter1",
            chunk_index=0,
        )
        assert record.content == "hello world"
        assert record.source_file == "docs/module1/chapter1.mdx"
        assert record.module == "module1"
        assert record.chapter == "chapter1"
        assert record.chunk_index == 0
        assert record.id is not None
        assert record.vector == []

    def test_from_text_chunk_with_embedding(self):
        record = VectorRecord.from_text_chunk(
            text_chunk="hello",
            source_file="doc.mdx",
            module="m1",
            chapter="c1",
            chunk_index=0,
            embedding=[0.5, 0.6, 0.7],
        )
        assert record.vector == [0.5, 0.6, 0.7]
