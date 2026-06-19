import pytest
from ingest_book import convert_mdx_to_text


class TestMdxConversion:
    def test_basic_conversion(self):
        mdx = "# Introduction\n\nThis is **bold** and *italic*."
        result = convert_mdx_to_text(mdx)
        assert "Introduction" in result
        assert "bold" in result
        assert "italic" in result

    def test_code_blocks_removed(self):
        mdx = "Text\n```python\nprint('hello')\n```\nMore text"
        result = convert_mdx_to_text(mdx)
        assert "print('hello')" not in result
        assert "Text" in result
        assert "More text" in result

    def test_jsx_components_removed(self):
        mdx = "Before\n<Component prop=\"value\">Content</Component>\nAfter"
        result = convert_mdx_to_text(mdx)
        assert "Content" in result
        assert "<Component" not in result

    def test_markdown_links_stripped(self):
        mdx = "Click [here](http://example.com) for info"
        result = convert_mdx_to_text(mdx)
        assert "here" in result
        assert "http://" not in result

    def test_markdown_images_keep_alt(self):
        mdx = "![Robot Image](img/robot.png)"
        result = convert_mdx_to_text(mdx)
        assert "Robot Image" in result

    def test_empty_content(self):
        assert convert_mdx_to_text("") == ""

    def test_imports_and_exports_removed(self):
        mdx = "import Component from './Component'\nexport const x = 1\n\n# Hello"
        result = convert_mdx_to_text(mdx)
        assert "import" not in result
        assert "Hello" in result

    def test_bullet_lists_stripped(self):
        mdx = "- Item 1\n- Item 2\n* Item 3"
        result = convert_mdx_to_text(mdx)
        assert "Item 1" in result
        assert "Item 2" in result

    def test_numbered_lists_stripped(self):
        mdx = "1. First\n2. Second"
        result = convert_mdx_to_text(mdx)
        assert "First" in result
        assert "Second" in result

    def test_headers_stripped(self):
        mdx = "## Section Title\n### Subsection"
        result = convert_mdx_to_text(mdx)
        assert "Section Title" in result
        assert "Subsection" in result
        assert "##" not in result
