import pytest
from ingest_book import extract_module_and_chapter_from_path, validate_file_path


class TestExtractModuleAndChapter:
    def test_normal_path(self):
        module, chapter = extract_module_and_chapter_from_path("my-website/docs/module1/chapter1.mdx")
        assert module == "module1"
        assert chapter == "chapter1"

    def test_glossary_file(self):
        module, chapter = extract_module_and_chapter_from_path("my-website/docs/glossary.mdx")
        assert module == "root"
        assert chapter == "glossary"

    def test_path_with_dot_prefix(self):
        module, chapter = extract_module_and_chapter_from_path("./my-website/docs/module2/chapter3.mdx")
        assert module == "module2"
        assert chapter == "chapter3"

    def test_windows_path_separators(self):
        module, chapter = extract_module_and_chapter_from_path("docs\\module1\\chapter1.mdx")
        assert module == "module1"
        assert chapter == "chapter1"

    def test_no_docs_in_path(self):
        module, chapter = extract_module_and_chapter_from_path("/other/module2/chapter5.mdx")
        assert module == "module2"
        assert chapter == "chapter5"

    def test_single_segment_path(self):
        module, chapter = extract_module_and_chapter_from_path("standalone.mdx")
        assert module == "unknown"
        assert chapter == "standalone"


class TestValidateFilePath:
    def test_valid_path(self):
        assert validate_file_path("my-website/docs/module1/chapter1.mdx", "my-website/docs") is True

    def test_path_traversal_attempt(self):
        assert validate_file_path("my-website/docs/../secret.txt", "my-website/docs") is False

    def test_path_outside_base(self):
        assert validate_file_path("/tmp/secret.txt", "my-website/docs") is False

    def test_url_encoded_traversal_decoded_and_blocked(self):
        assert validate_file_path("my-website/docs/%2e%2e%2fsecret.txt", "my-website/docs") is False

    def test_identical_path(self):
        assert validate_file_path("my-website/docs", "my-website/docs") is True

    def test_nonexistent_base_dir(self):
        assert validate_file_path("some/file.mdx", "/nonexistent/path") is False
