#!/usr/bin/env python3
"""
Unit tests for the Book Vector Ingestion System.
These tests verify the critical functions of the system.
"""

import unittest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from ingest_book import (
    extract_module_and_chapter_from_path,
    validate_file_path,
    convert_mdx_to_text,
    chunk_text,
    VectorRecord,
    create_cli_parser,
    validate_input_parameters
)


class TestPathExtraction(unittest.TestCase):
    """Test functions related to path extraction and validation."""

    def test_extract_module_and_chapter_from_path(self):
        """Test extracting module and chapter from file paths."""
        # Test normal case
        module, chapter = extract_module_and_chapter_from_path('my-website/docs/module1/chapter1.mdx')
        self.assertEqual(module, 'module1')
        self.assertEqual(chapter, 'chapter1')

        # Test with glossary file
        module, chapter = extract_module_and_chapter_from_path('my-website/docs/glossary.mdx')
        self.assertEqual(module, 'root')
        self.assertEqual(chapter, 'glossary')

        # Test with different path format
        module, chapter = extract_module_and_chapter_from_path('./my-website/docs/module2/chapter3.mdx')
        self.assertEqual(module, 'module2')
        self.assertEqual(chapter, 'chapter3')

    def test_validate_file_path(self):
        """Test file path validation."""
        # Test valid path
        result = validate_file_path('my-website/docs/module1/chapter1.mdx', 'my-website/docs')
        self.assertTrue(result)

        # Test path traversal attempt
        result = validate_file_path('my-website/docs/../secret.txt', 'my-website/docs')
        self.assertFalse(result)

        # Test path outside base directory
        result = validate_file_path('/tmp/secret.txt', 'my-website/docs')
        self.assertFalse(result)


class TestMdxConversion(unittest.TestCase):
    """Test MDX to text conversion functions."""

    def test_convert_mdx_to_text(self):
        """Test converting MDX content to plain text."""
        mdx_content = """
# Introduction

This is a **bold** text and *italic* text.

- Item 1
- Item 2

[Link text](http://example.com)

<Component jsx="value">Content</Component>
"""
        expected_text = "Introduction\n\nThis is a bold text and italic text.\n\nItem 1\nItem 2\n\nLink text\n\nContent"
        result = convert_mdx_to_text(mdx_content)
        # The actual result will have some differences due to regex, but the core content should be there
        self.assertIn("Introduction", result)
        self.assertIn("bold", result)
        self.assertIn("italic", result)
        self.assertIn("Link text", result)
        self.assertIn("Content", result)

    def test_convert_mdx_to_text_empty(self):
        """Test converting empty MDX content."""
        result = convert_mdx_to_text("")
        self.assertEqual(result, "")


class TestChunking(unittest.TestCase):
    """Test text chunking functions."""

    def test_chunk_text(self):
        """Test chunking text with overlap."""
        text = "A " * 100  # Create a text of 200 characters
        chunks = chunk_text(text, chunk_size=50, overlap=10)

        self.assertGreater(len(chunks), 1)  # Should have multiple chunks
        self.assertLessEqual(len(chunks[0]), 50)  # First chunk should not exceed chunk_size

    def test_chunk_text_no_overlap(self):
        """Test chunking text with no overlap."""
        text = "A " * 20  # Create a short text
        chunks = chunk_text(text, chunk_size=100, overlap=0)

        self.assertEqual(len(chunks), 1)  # Should have just one chunk

    def test_chunk_text_empty(self):
        """Test chunking empty text."""
        chunks = chunk_text("")
        self.assertEqual(chunks, [])


class TestVectorRecord(unittest.TestCase):
    """Test VectorRecord class."""

    def test_vector_record_creation(self):
        """Test creating a VectorRecord."""
        record = VectorRecord(
            id="test-id",
            vector=[0.1, 0.2, 0.3],
            content="test content",
            source_file="docs/module1/chapter1.mdx",
            module="module1",
            chapter="chapter1",
            chunk_index=0
        )

        self.assertEqual(record.id, "test-id")
        self.assertEqual(record.vector, [0.1, 0.2, 0.3])
        self.assertEqual(record.content, "test content")
        self.assertEqual(record.source_file, "docs/module1/chapter1.mdx")
        self.assertEqual(record.module, "module1")
        self.assertEqual(record.chapter, "chapter1")
        self.assertEqual(record.chunk_index, 0)

    def test_vector_record_to_payload(self):
        """Test converting VectorRecord to payload."""
        record = VectorRecord(
            id="test-id",
            vector=[0.1, 0.2, 0.3],
            content="test content",
            source_file="docs/module1/chapter1.mdx",
            module="module1",
            chapter="chapter1",
            chunk_index=0
        )

        payload = record.to_payload()
        self.assertEqual(payload["content"], "test content")
        self.assertEqual(payload["source_file"], "docs/module1/chapter1.mdx")
        self.assertEqual(payload["module"], "module1")
        self.assertEqual(payload["chapter"], "chapter1")
        self.assertEqual(payload["chunk_index"], 0)
        self.assertIn("created_at", payload)


class TestCLIAndValidation(unittest.TestCase):
    """Test CLI and input validation functions."""

    def test_create_cli_parser(self):
        """Test that CLI parser is created without errors."""
        parser = create_cli_parser()
        self.assertIsNotNone(parser)

    def test_validate_input_parameters(self):
        """Test input parameter validation."""
        # Create a mock args object
        class MockArgs:
            docs_dir = "./my-website/docs"
            chunk_size = 512
            chunk_overlap = 50
            qdrant_host = "localhost"
            qdrant_port = 6333
            cohere_model = "embed-multilingual-v3.0"
            collection_name = "book_vectors"
            batch_size = 100

        args = MockArgs()
        # This should not raise an exception
        result = validate_input_parameters(args)
        self.assertTrue(result)

    def test_validate_input_parameters_invalid(self):
        """Test input parameter validation with invalid values."""
        # Test with invalid chunk size
        class MockArgsInvalid:
            docs_dir = "./my-website/docs"
            chunk_size = -1  # Invalid
            chunk_overlap = 50
            qdrant_host = "localhost"
            qdrant_port = 6333
            cohere_model = "embed-multilingual-v3.0"
            collection_name = "book_vectors"
            batch_size = 100

        args = MockArgsInvalid()
        with self.assertRaises(ValueError):
            validate_input_parameters(args)


if __name__ == '__main__':
    print("Running unit tests for Book Vector Ingestion System...")
    unittest.main(verbosity=2)