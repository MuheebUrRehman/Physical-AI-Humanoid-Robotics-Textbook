import pytest
from unittest.mock import MagicMock


def test_book_knowledge_instructions_includes_chunks(mock_chunks):
    from agent import book_knowledge_instructions

    mock_ctx = MagicMock()
    mock_ctx.context = {"book_chunks": mock_chunks}
    mock_agent = MagicMock()

    prompt = book_knowledge_instructions(mock_ctx, mock_agent)

    assert "ROS 2 uses nodes" in prompt
    assert "from module1/chapter1.mdx" in prompt
    assert "URDF describes robot kinematics" in prompt
    assert "Gazebo provides physics simulation" in prompt


def test_book_knowledge_instructions_handles_string_fallback():
    from agent import book_knowledge_instructions

    mock_ctx = MagicMock()
    mock_ctx.context = {"book_chunks": ["Plain text chunk content"]}
    mock_agent = MagicMock()

    prompt = book_knowledge_instructions(mock_ctx, mock_agent)

    assert "Plain text chunk content" in prompt


def test_book_knowledge_instructions_empty_chunks(mock_empty_chunks):
    from agent import book_knowledge_instructions

    mock_ctx = MagicMock()
    mock_ctx.context = {"book_chunks": mock_empty_chunks}
    mock_agent = MagicMock()

    prompt = book_knowledge_instructions(mock_ctx, mock_agent)

    assert "BOOK CONTENT" in prompt


def test_book_knowledge_instructions_includes_scores():
    from agent import book_knowledge_instructions

    chunks_with_scores = [
        {"text": "ROS 2 content.", "source": "ch1.mdx", "score": 0.92},
        {"text": "Gazebo content.", "source": "ch2.mdx", "score": 0.85},
    ]

    mock_ctx = MagicMock()
    mock_ctx.context = {"book_chunks": chunks_with_scores}
    mock_agent = MagicMock()

    prompt = book_knowledge_instructions(mock_ctx, mock_agent)

    assert "relevance: 0.920" in prompt
    assert "relevance: 0.850" in prompt


def test_book_knowledge_instructions_has_grounding_policy():
    from agent import book_knowledge_instructions

    mock_ctx = MagicMock()
    mock_ctx.context = {"book_chunks": []}
    mock_agent = MagicMock()

    prompt = book_knowledge_instructions(mock_ctx, mock_agent)

    assert "cannot find this in the textbook" in prompt
