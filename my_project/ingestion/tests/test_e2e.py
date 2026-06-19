import os
import tempfile
from unittest.mock import MagicMock, patch
from ingest_book import (
    scan_mdx_files, read_mdx_file, convert_mdx_to_text,
    chunk_text, prepare_chunks_for_embedding,
    validate_all_files_processed,
)


def create_test_mdx_files(temp_dir):
    os.makedirs(os.path.join(temp_dir, "module1"), exist_ok=True)
    os.makedirs(os.path.join(temp_dir, "module2"), exist_ok=True)

    with open(os.path.join(temp_dir, "glossary.mdx"), "w", encoding="utf-8") as f:
        f.write("# Glossary\n\n## AI\nArtificial Intelligence\n")
    with open(os.path.join(temp_dir, "module1", "chapter1.mdx"), "w", encoding="utf-8") as f:
        f.write("# Chapter 1\n\nContent of chapter 1.\n")
    with open(os.path.join(temp_dir, "module2", "chapter2.mdx"), "w", encoding="utf-8") as f:
        f.write("# Chapter 2\n\nContent of chapter 2.\n")


def test_e2e_pipeline():
    with tempfile.TemporaryDirectory() as temp_dir:
        create_test_mdx_files(temp_dir)

        mdx_files = scan_mdx_files(temp_dir)
        assert len(mdx_files) == 3

        all_vector_records = []
        processed_files = []

        for file_path in mdx_files:
            content = read_mdx_file(file_path)
            assert content is not None

            text_content = convert_mdx_to_text(content)
            assert len(text_content) > 0

            chunks = chunk_text(text_content, chunk_size=100, overlap=20)
            assert len(chunks) > 0

            from ingest_book import extract_module_and_chapter_from_path
            module, chapter = extract_module_and_chapter_from_path(file_path)
            vector_records = prepare_chunks_for_embedding(chunks, file_path, module, chapter)

            all_vector_records.extend(vector_records)
            processed_files.append(file_path)

        assert len(all_vector_records) > 0
        assert len(processed_files) == 3

        validation_result = validate_all_files_processed(mdx_files, processed_files, len(all_vector_records))
        assert validation_result is True
