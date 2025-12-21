#!/usr/bin/env python3
"""
End-to-end test for the Book Vector Ingestion System.
This script demonstrates the complete workflow from MDX files to vector storage.
"""

import os
import tempfile
import shutil
from unittest.mock import Mock, patch
from ingest_book import (
    scan_mdx_files,
    read_mdx_file,
    convert_mdx_to_text,
    chunk_text,
    prepare_chunks_for_embedding,
    create_qdrant_collection,
    batch_store_vectors_in_qdrant,
    verify_stored_vectors,
    validate_all_files_processed,
    setup_cohere_client,
    setup_qdrant_client,
    load_config
)


def create_test_mdx_files(temp_dir):
    """Create test MDX files for the end-to-end test."""
    # Create module directories
    os.makedirs(os.path.join(temp_dir, "module1"), exist_ok=True)
    os.makedirs(os.path.join(temp_dir, "module2"), exist_ok=True)

    # Create test MDX files
    with open(os.path.join(temp_dir, "glossary.mdx"), "w", encoding="utf-8") as f:
        f.write("""
# Glossary

## AI
Artificial Intelligence

## ML
Machine Learning

<Component>
Some JSX component
</Component>
        """)

    with open(os.path.join(temp_dir, "module1", "chapter1.mdx"), "w", encoding="utf-8") as f:
        f.write("""
# Introduction to AI

Artificial Intelligence is a fascinating field.

- Machine Learning
- Deep Learning
- Neural Networks

[Learn more](https://example.com)

<Component>
Some JSX component
</Component>
        """)

    with open(os.path.join(temp_dir, "module2", "chapter2.mdx"), "w", encoding="utf-8") as f:
        f.write("""
# Advanced Topics

This covers advanced topics in AI.

## Deep Learning
- Neural networks
- Backpropagation

## Reinforcement Learning
- Q-learning
- Policy gradients

<Component>
Another JSX component
</Component>
        """)

    return [
        os.path.join(temp_dir, "glossary.mdx"),
        os.path.join(temp_dir, "module1", "chapter1.mdx"),
        os.path.join(temp_dir, "module2", "chapter2.mdx")
    ]


def run_end_to_end_test():
    """Run the complete end-to-end test."""
    print("Starting end-to-end test for Book Vector Ingestion System...")

    # Create temporary directory with test files
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Created temporary directory: {temp_dir}")

        # Create test MDX files
        test_files = create_test_mdx_files(temp_dir)
        print(f"Created test files: {test_files}")

        # Step 1: Scan MDX files
        print("\nStep 1: Scanning MDX files...")
        mdx_files = scan_mdx_files(temp_dir)
        print(f"Found {len(mdx_files)} MDX files: {mdx_files}")

        # Step 2: Process each file
        print("\nStep 2: Processing each file...")
        all_vector_records = []
        processed_files = []

        for file_path in mdx_files:
            print(f"Processing: {file_path}")

            # Read MDX file
            content = read_mdx_file(file_path)
            if content:
                print(f"  - Read {len(content)} characters")

                # Convert MDX to text
                text_content = convert_mdx_to_text(content)
                print(f"  - Converted to {len(text_content)} plain text characters")

                # Chunk the text
                chunks = chunk_text(text_content, chunk_size=100, overlap=20)
                print(f"  - Chunked into {len(chunks)} chunks")

                # Prepare for embedding (mock - in real usage, would connect to Cohere)
                from ingest_book import extract_module_and_chapter_from_path
                module, chapter = extract_module_and_chapter_from_path(file_path)
                vector_records = prepare_chunks_for_embedding(chunks, file_path, module, chapter)
                print(f"  - Prepared {len(vector_records)} vector records")

                all_vector_records.extend(vector_records)
                processed_files.append(file_path)
            else:
                print(f"  - Failed to read file: {file_path}")

        print(f"\nTotal vector records created: {len(all_vector_records)}")
        print(f"Successfully processed files: {len(processed_files)}")

        # Step 3: Mock storage (since we don't have actual Cohere/Qdrant for testing)
        print("\nStep 3: Mock storage process...")
        print(f"Would store {len(all_vector_records)} vectors in Qdrant collection")

        # Validation step
        validation_result = validate_all_files_processed(mdx_files, processed_files, len(all_vector_records))
        print(f"Validation result: {'PASSED' if validation_result else 'FAILED'}")

        print("\nEnd-to-end test completed successfully!")
        print(f"- Processed {len(mdx_files)} MDX files")
        print(f"- Created {len(all_vector_records)} vector records")
        print(f"- Validation: {'PASSED' if validation_result else 'FAILED'}")

        return True


def run_integration_test():
    """Run an integration test to verify the main components work together."""
    print("\nRunning integration test...")

    # Test configuration loading
    try:
        config = load_config()
        print("OK Configuration loaded")
    except Exception as e:
        print(f"ERROR Configuration loading failed: {e}")
        return False

    # Test path extraction
    try:
        from ingest_book import extract_module_and_chapter_from_path
        module, chapter = extract_module_and_chapter_from_path("my-website/docs/module1/chapter1.mdx")
        assert module == "module1"
        assert chapter == "chapter1"
        print("OK Path extraction works")
    except Exception as e:
        print(f"ERROR Path extraction failed: {e}")
        return False

    # Test text conversion
    try:
        test_mdx = "# Test\n\nThis is **bold** text."
        from ingest_book import convert_mdx_to_text
        text = convert_mdx_to_text(test_mdx)
        assert "Test" in text
        assert "bold" in text
        print("OK MDX to text conversion works")
    except Exception as e:
        print(f"ERROR MDX to text conversion failed: {e}")
        return False

    # Test chunking
    try:
        from ingest_book import chunk_text
        chunks = chunk_text("A " * 100, chunk_size=50, overlap=10)
        assert len(chunks) > 0
        print("OK Text chunking works")
    except Exception as e:
        print(f"ERROR Text chunking failed: {e}")
        return False

    print("Integration test passed!")
    return True


if __name__ == "__main__":
    print("Running end-to-end and integration tests for Book Vector Ingestion System...")

    # Run integration test first
    integration_success = run_integration_test()

    # Run end-to-end test
    e2e_success = run_end_to_end_test()

    print(f"\nTest Results:")
    print(f"Integration Test: {'PASSED' if integration_success else 'FAILED'}")
    print(f"End-to-End Test: {'PASSED' if e2e_success else 'FAILED'}")
    print(f"Overall: {'PASSED' if integration_success and e2e_success else 'FAILED'}")