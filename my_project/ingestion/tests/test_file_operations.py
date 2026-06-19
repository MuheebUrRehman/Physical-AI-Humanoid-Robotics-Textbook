import pytest
import os
import tempfile
from unittest.mock import patch
from ingest_book import read_mdx_file, get_all_mdx_files, scan_mdx_files


class TestReadMdxFile:
    def test_read_valid_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mdx", encoding="utf-8", delete=False) as f:
            f.write("# Hello\nWorld")
            path = f.name
        try:
            content = read_mdx_file(path)
            assert content is not None
            assert "# Hello" in content
        finally:
            os.unlink(path)

    def test_file_not_found(self):
        content = read_mdx_file("/nonexistent/file.mdx")
        assert content is None

    def test_oversized_file(self):
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".mdx", delete=False) as f:
            f.write(b"X" * (60 * 1024 * 1024))
            path = f.name
        try:
            content = read_mdx_file(path, max_file_size_mb=50)
            assert content is None
        finally:
            os.unlink(path)

    def test_binary_file_fallback_to_latin1(self):
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".mdx", delete=False) as f:
            f.write(b"\xff\xfe# Hello")
            path = f.name
        try:
            content = read_mdx_file(path)
            assert content is not None
        finally:
            os.unlink(path)


class TestGetAllMdxFiles:
    def test_finds_mdx_files(self, temp_docs_dir):
        files = get_all_mdx_files(temp_docs_dir)
        assert len(files) >= 2
        assert any(f.endswith("glossary.mdx") for f in files)
        assert any(f.endswith("chapter1.mdx") for f in files)

    def test_ignores_non_mdx(self, temp_docs_dir):
        with open(os.path.join(temp_docs_dir, "readme.txt"), "w") as f:
            f.write("not mdx")
        files = get_all_mdx_files(temp_docs_dir)
        assert all(f.endswith(".mdx") for f in files)


class TestScanMdxFiles:
    def test_scan_valid_directory(self, temp_docs_dir):
        files = scan_mdx_files(temp_docs_dir)
        assert len(files) >= 2

    def test_nonexistent_directory(self):
        with pytest.raises(FileNotFoundError):
            scan_mdx_files("/nonexistent/path")
