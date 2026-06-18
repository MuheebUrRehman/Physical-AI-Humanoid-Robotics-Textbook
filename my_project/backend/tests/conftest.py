import os
import sys
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# Ensure the backend root is on sys.path so test imports like `from retrieval import ...` work.
_backend_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _backend_root not in sys.path:
    sys.path.insert(0, _backend_root)

# Set dummy API keys at module level so Config.validate() passes at import time.
# These are never actually called — all external dependencies are mocked in tests.
os.environ.setdefault("COHERE_API_KEY", "test-cohere-key")
os.environ.setdefault("QDRANT_API_KEY", "test-qdrant-key")
os.environ.setdefault("LLM_API_KEY", "test-llm-key")
os.environ.setdefault("QDRANT_HOST", "localhost")


@pytest.fixture
def mock_chunks():
    """Sample chunks with source metadata matching retrieval.py dict format."""
    return [
        {"text": "ROS 2 uses nodes, topics, and services for communication.", "source": "module1/chapter1.mdx", "module": "module1", "chapter": "chapter1"},
        {"text": "URDF describes robot kinematics and visual properties.", "source": "module1/chapter3.mdx", "module": "module1", "chapter": "chapter3"},
        {"text": "Gazebo provides physics simulation with gravity and collisions.", "source": "module2/chapter1.mdx", "module": "module2", "chapter": "chapter1"},
    ]


@pytest.fixture
def mock_empty_chunks():
    """Empty chunk list for edge case testing."""
    return []
