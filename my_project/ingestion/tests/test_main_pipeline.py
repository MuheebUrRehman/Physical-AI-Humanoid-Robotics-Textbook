import pytest
import os
import tempfile
from unittest.mock import MagicMock, patch
from ingest_book import process_file_for_vectorization, track_performance, load_config


class TestProcessFileForVectorization:
    def test_processes_file_successfully(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mdx", encoding="utf-8", delete=False) as f:
            f.write("# Test Chapter\n\nThis is test content for embedding.")
            path = f.name
        try:
            mock_client = MagicMock()

            text = "# Test Chapter\n\nThis is test content for embedding."
            from ingest_book import chunk_text
            chunks = chunk_text("Test Chapter\n\nThis is test content for embedding.", chunk_size=256, overlap=25)
            num_chunks = len(chunks)
            embeddings = [[0.1] * 1024 for _ in range(num_chunks)]

            mock_client.embed.return_value = MagicMock(embeddings=embeddings)

            config = {
                "chunk_size": 256,
                "chunk_overlap": 25,
                "cohere_model": "embed-multilingual-v3.0",
                "max_file_size_mb": 50,
            }

            records = process_file_for_vectorization(path, mock_client, config)
            assert len(records) > 0
            assert records[0].source_file == path
            assert len(records[0].vector) == 1024
        finally:
            os.unlink(path)

    def test_handles_nonexistent_file(self):
        mock_client = MagicMock()
        config = {"chunk_size": 256, "chunk_overlap": 25, "cohere_model": "test", "max_file_size_mb": 50}
        records = process_file_for_vectorization("/nonexistent/file.mdx", mock_client, config)
        assert records == []


class TestTrackPerformance:
    def test_tracks_performance(self):
        import time
        start = time.time() - 10
        data = track_performance(start, total_files=10, processed_files=5)
        assert data["total_files"] == 10
        assert data["processed_files"] == 5
        assert "elapsed_time" in data
        assert "progress_percent" in data
        assert data["progress_percent"] == 50.0


class TestLoadConfig:
    def test_defaults(self):
        config = load_config()
        assert config["chunk_size"] == 512
        assert config["chunk_overlap"] == 50
        assert "cohere_api_key" in config
        assert "qdrant_host" in config
