import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.asyncio
async def test_guardrail_passes_relevant_query():
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
async def test_guardrail_passes_verbose_yes():
    from agent import check_query_relevance

    mock_result = MagicMock()
    mock_result.final_output = "Yes, this query appears to be about robotics."

    with patch("agent.Runner.run", new_callable=AsyncMock) as mock_runner:
        mock_runner.return_value = mock_result
        result = await check_query_relevance.run(
            MagicMock(), MagicMock(), "What are actuators?"
        )

    assert result.output.tripwire_triggered is False
    assert result.output.output_info is None


@pytest.mark.asyncio
async def test_guardrail_fails_open_on_error():
    from agent import check_query_relevance

    with patch("agent.Runner.run", new_callable=AsyncMock) as mock_runner:
        mock_runner.side_effect = Exception("Judge error")
        result = await check_query_relevance.run(
            MagicMock(), MagicMock(), "some query"
        )

    assert result.output.tripwire_triggered is False
    assert "Unable to verify" in str(result.output.output_info)
