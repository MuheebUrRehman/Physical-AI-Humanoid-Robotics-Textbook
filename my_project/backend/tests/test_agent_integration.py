import pytest
from unittest.mock import AsyncMock, MagicMock, patch


def test_book_knowledge_instructions_includes_chunks(mock_chunks):
    """Verify the dynamic instructions function injects chunk text and source into the prompt."""
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
    """Verify backward compatibility: plain string chunks still work."""
    from agent import book_knowledge_instructions

    mock_ctx = MagicMock()
    mock_ctx.context = {"book_chunks": ["Plain text chunk content"]}
    mock_agent = MagicMock()

    prompt = book_knowledge_instructions(mock_ctx, mock_agent)

    assert "Plain text chunk content" in prompt


def test_book_knowledge_instructions_empty_chunks(mock_empty_chunks):
    """Verify the prompt still builds when no chunks are provided."""
    from agent import book_knowledge_instructions

    mock_ctx = MagicMock()
    mock_ctx.context = {"book_chunks": mock_empty_chunks}
    mock_agent = MagicMock()

    prompt = book_knowledge_instructions(mock_ctx, mock_agent)

    assert "BOOK CONTENT" in prompt


@pytest.mark.asyncio
async def test_guardrail_passes_relevant_query():
    """Verify guardrail allows on-topic queries through."""
    from agent import check_query_relevance

    mock_result = MagicMock()
    mock_result.final_output = "yes"

    with patch("agent.Runner.run", new_callable=AsyncMock) as mock_runner:
        mock_runner.return_value = mock_result
        result = await check_query_relevance.run(
            MagicMock(), MagicMock(), "What is ROS 2?"
        )

    assert result.output.tripwire_triggered is False
    assert result.output.output_info is None


@pytest.mark.asyncio
async def test_guardrail_blocks_off_topic_query():
    """Verify guardrail rejects queries unrelated to robotics."""
    from agent import check_query_relevance

    mock_result = MagicMock()
    mock_result.final_output = "no"

    with patch("agent.Runner.run", new_callable=AsyncMock) as mock_runner:
        mock_runner.return_value = mock_result
        result = await check_query_relevance.run(
            MagicMock(), MagicMock(), "What is the weather?"
        )

    assert result.output.tripwire_triggered is True
    assert result.output.output_info is not None


@pytest.mark.asyncio
async def test_guardrail_fails_open_on_error():
    """Verify guardrail allows query through if the judge agent errors."""
    from agent import check_query_relevance

    with patch("agent.Runner.run", new_callable=AsyncMock) as mock_runner:
        mock_runner.side_effect = Exception("Judge error")
        result = await check_query_relevance.run(
            MagicMock(), MagicMock(), "some query"
        )

    assert result.output.tripwire_triggered is False


@pytest.mark.asyncio
async def test_chat_stream_generator_yields_token_events(mock_chunks):
    """Verify the SSE stream generator yields token and final events."""
    from app import chat_stream_generator
    from models.chat import ChatRequest

    request = ChatRequest(
        query="What is ROS 2?",
        user_id="test_user",
        session_id="test_session",
    )

    # Mock get_relevant_chunks to avoid API calls
    with patch("app.get_relevant_chunks", new_callable=AsyncMock) as mock_retrieval:
        mock_retrieval.return_value = mock_chunks

        # Mock the streaming agent
        mock_stream = MagicMock()
        mock_stream.stream_events.return_value.__aiter__.return_value = [
            MagicMock(
                type="raw_response_event",
                data=MagicMock(delta="ROS", response=MagicMock(name="BookKnowledgeAgent")),
            ),
            MagicMock(
                type="raw_response_event",
                data=MagicMock(delta=" 2", response=MagicMock(name="BookKnowledgeAgent")),
            ),
            MagicMock(
                type="run_item_stream_event",
                result=MagicMock(final_output="ROS 2 is a framework for robotics."),
            ),
        ]

        with patch("app.Runner.run_streamed", return_value=mock_stream):
            events = []
            async for event in chat_stream_generator(request):
                events.append(event)

    # Should have 3 events: 2 tokens + 1 final
    assert len(events) == 3
    assert '"type":"token"' in events[0]
    assert '"type":"token"' in events[1]
    assert '"type":"final"' in events[2]
    assert "ROS 2" in events[2]


@pytest.mark.asyncio
async def test_chat_stream_generator_empty_response():
    """Verify error event when agent yields no output."""
    from app import chat_stream_generator
    from models.chat import ChatRequest

    request = ChatRequest(
        query="empty query",
        user_id="test_user",
        session_id="test_session",
    )

    with patch("app.get_relevant_chunks", new_callable=AsyncMock) as mock_retrieval:
        mock_retrieval.return_value = []

        mock_stream = MagicMock()
        mock_stream.stream_events.return_value.__aiter__.return_value = []

        with patch("app.Runner.run_streamed", return_value=mock_stream):
            events = []
            async for event in chat_stream_generator(request):
                events.append(event)

    assert len(events) == 1
    assert "error" in events[0]
    assert "empty response" in events[0].lower()
