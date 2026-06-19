import pytest
from unittest.mock import MagicMock, patch
from ingest_book import create_qdrant_collection, batch_store_vectors_in_qdrant, verify_stored_vectors, validate_all_files_processed, VectorRecord


class TestCreateQdrantCollection:
    def test_collection_created(self):
        mock_client = MagicMock()
        mock_client.get_collections.return_value = MagicMock(collections=[])
        result = create_qdrant_collection(mock_client, "test_collection", vector_size=1024)
        assert result is True
        mock_client.recreate_collection.assert_called_once()

    def test_collection_already_exists(self):
        mock_collection = MagicMock()
        mock_collection.name = "test_collection"
        mock_client = MagicMock()
        mock_client.get_collections.return_value = MagicMock(collections=[mock_collection])
        result = create_qdrant_collection(mock_client, "test_collection")
        assert result is True
        mock_client.recreate_collection.assert_not_called()


class TestBatchStoreVectors:
    def test_empty_records(self):
        mock_client = MagicMock()
        result = batch_store_vectors_in_qdrant(mock_client, [], "test_collection")
        assert result is True

    def test_stores_records(self):
        mock_client = MagicMock()
        records = [
            VectorRecord(id="1", vector=[0.1, 0.2], content="test", source_file="a.mdx", module="m1", chapter="c1", chunk_index=0)
        ]
        result = batch_store_vectors_in_qdrant(mock_client, records, "test_collection")
        assert result is True
        mock_client.upsert.assert_called_once()


class TestVerifyStoredVectors:
    def test_verification_success(self):
        mock_point = MagicMock()
        mock_point.id = "point-1"
        mock_point.payload = {"content": "test", "source_file": "a.mdx", "module": "m1", "chapter": "c1", "chunk_index": 0, "created_at": "2025-01-01T00:00:00"}

        mock_client = MagicMock()
        mock_client.get_collection.return_value = MagicMock(points_count=1)
        mock_client.scroll.return_value = ([mock_point], None)

        assert verify_stored_vectors(mock_client, "test_collection") is True

    def test_verification_no_vectors(self):
        mock_client = MagicMock()
        mock_client.get_collection.return_value = MagicMock(points_count=0)

        assert verify_stored_vectors(mock_client, "test_collection") is False

    def test_verification_missing_fields(self):
        mock_point = MagicMock()
        mock_point.id = "point-1"
        mock_point.payload = {"content": "test"}

        mock_client = MagicMock()
        mock_client.get_collection.return_value = MagicMock(points_count=1)
        mock_client.scroll.return_value = ([mock_point], None)

        assert verify_stored_vectors(mock_client, "test_collection") is False


class TestValidateAllFilesProcessed:
    def test_all_processed(self):
        assert validate_all_files_processed(["a.mdx", "b.mdx"], ["a.mdx", "b.mdx"], 2) is True

    def test_missing_file(self):
        assert validate_all_files_processed(["a.mdx", "b.mdx"], ["a.mdx"], 1) is False

    def test_not_enough_vectors(self):
        assert validate_all_files_processed(["a.mdx", "b.mdx"], ["a.mdx", "b.mdx"], 0) is False
