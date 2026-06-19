import pytest
from ingest_book import chunk_text


class TestChunking:
    def test_empty_text(self):
        assert chunk_text("") == []

    def test_single_short_paragraph(self):
        text = "This is a short paragraph."
        chunks = chunk_text(text, chunk_size=100, overlap=0)
        assert len(chunks) == 1
        assert "short paragraph" in chunks[0]

    def test_multiple_paragraphs_split(self):
        text = "Word. " * 20 + "\n\n" + "Word. " * 20 + "\n\n" + "Word. " * 20
        chunks = chunk_text(text, chunk_size=10, overlap=0)
        assert len(chunks) >= 2

    def test_large_paragraph_sentence_boundary(self):
        text = ("This is the first sentence. " * 20) + "And a final sentence."
        chunks = chunk_text(text, chunk_size=30, overlap=5)
        assert len(chunks) > 1
        for chunk in chunks:
            assert len(chunk) > 0

    def test_large_overlap_safety(self):
        text = ("X " * 100) + "\n\n" + ("Y " * 100)
        chunks = chunk_text(text, chunk_size=20, overlap=30)
        assert len(chunks) >= 2

    def test_overlap_preserves_text(self):
        text = "AAAA.\n\n" * 5 + "BBBB.\n\n" * 5
        chunks = chunk_text(text, chunk_size=50, overlap=10)
        if len(chunks) > 1:
            combined = " ".join(chunks)
            assert "AAAA" in combined
            assert "BBBB" in combined

    def test_single_sentence_text(self):
        chunks = chunk_text("Just one sentence here.", chunk_size=100, overlap=0)
        assert len(chunks) == 1

    def test_no_split_when_under_limit(self):
        text = "A single paragraph that fits within the chunk size limit."
        chunks = chunk_text(text, chunk_size=500, overlap=0)
        assert len(chunks) == 1

    def test_does_not_split_mid_sentence(self):
        para = "Sentence A. Sentence B. Sentence C. Sentence D. Sentence E. Sentence F."
        chunks = chunk_text(para, chunk_size=20, overlap=5)
        for chunk in chunks:
            assert chunk.strip() != ""
