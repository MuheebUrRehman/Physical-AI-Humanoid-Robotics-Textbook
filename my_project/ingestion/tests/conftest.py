import os
import sys
import tempfile
import pytest

_ingestion_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ingestion_root not in sys.path:
    sys.path.insert(0, _ingestion_root)

os.environ.setdefault("COHERE_API_KEY", "test-cohere-key")
os.environ.setdefault("QDRANT_API_KEY", "test-qdrant-key")
os.environ.setdefault("QDRANT_HOST", "localhost")


@pytest.fixture
def temp_docs_dir():
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "module1"), exist_ok=True)
        os.makedirs(os.path.join(tmp, "module2"), exist_ok=True)

        with open(os.path.join(tmp, "glossary.mdx"), "w", encoding="utf-8") as f:
            f.write("# Glossary\n\n## AI\nArtificial Intelligence\n")
        with open(os.path.join(tmp, "module1", "chapter1.mdx"), "w", encoding="utf-8") as f:
            f.write("# Chapter 1\n\nContent here.\n")

        yield tmp
