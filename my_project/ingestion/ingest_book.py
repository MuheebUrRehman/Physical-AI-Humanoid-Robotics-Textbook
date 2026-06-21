#!/usr/bin/env python3
"""
Book Vector Ingestion System
Converts MDX files from the Physical AI & Humanoid Robotics textbook to vector embeddings
and stores them in Qdrant vector database for semantic search capabilities.

This module re-exports all public symbols from sub-modules for backward compatibility.
"""

from config import load_config, setup_logging, _DEFAULT_DOCS_DIR
from progress import ProgressTracker
from retry import handle_api_call_with_retry
from models import VectorRecord
from mdx_utils import read_mdx_file, convert_mdx_to_text
from chunking import chunk_text, process_large_mdx_file
from embedding import setup_cohere_client, safe_embed_chunks, embed_text_chunks
from qdrant_store import (
    setup_qdrant_client, safe_store_vectors_in_qdrant,
    create_qdrant_collection, batch_store_vectors_in_qdrant,
    verify_stored_vectors, validate_all_files_processed,
)
from pipeline import (
    extract_module_and_chapter_from_path, validate_file_path,
    get_all_mdx_files, scan_mdx_files, prepare_chunks_for_embedding,
    process_file_for_vectorization, track_performance,
)
from cli import create_cli_parser, validate_input_parameters, main

if __name__ == "__main__":
    main()

__all__ = [
    'load_config', 'setup_logging',
    'ProgressTracker',
    'handle_api_call_with_retry',
    'VectorRecord',
    'read_mdx_file', 'convert_mdx_to_text',
    'chunk_text', 'process_large_mdx_file',
    'setup_cohere_client', 'safe_embed_chunks', 'embed_text_chunks',
    'setup_qdrant_client', 'safe_store_vectors_in_qdrant',
    'create_qdrant_collection', 'batch_store_vectors_in_qdrant',
    'verify_stored_vectors', 'validate_all_files_processed',
    'extract_module_and_chapter_from_path', 'validate_file_path',
    'get_all_mdx_files', 'scan_mdx_files', 'prepare_chunks_for_embedding',
    'process_file_for_vectorization', 'track_performance',
    'create_cli_parser', 'validate_input_parameters', 'main',
]
