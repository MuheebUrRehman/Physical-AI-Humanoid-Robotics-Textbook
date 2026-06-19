import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone


@pytest.mark.asyncio
async def test_initialize_server_creates_store():
    with patch("chatkit_server.SQLiteStore") as mock_store_cls:
        mock_store = AsyncMock()
        mock_store.initialize = AsyncMock()
        mock_store_cls.return_value = mock_store

        from chatkit_server import initialize_chatkit_server
        server = await initialize_chatkit_server(":memory:")

        assert server is not None
        mock_store.initialize.assert_awaited_once()


@pytest.mark.asyncio
async def test_respond_guardrail_tripwire():
    from chatkit_server import CustomChatKitServer
    from agents import InputGuardrailTripwireTriggered
    from agents.guardrail import InputGuardrailResult, InputGuardrail, GuardrailFunctionOutput
    from chatkit.types import ThreadMetadata, UserMessageItem, ActiveStatus
    from models.chat import RequestContext

    store = AsyncMock()
    store.load_thread_items = AsyncMock(return_value=MagicMock(data=[]))

    server = CustomChatKitServer(store=store)

    thread = ThreadMetadata(
        id="thread-1",
        title="Test",
        created_at=datetime.now(timezone.utc),
        status=ActiveStatus(),
        allowed_image_domains=[],
    )

    user_msg = MagicMock(spec=UserMessageItem)
    user_msg.content = [MagicMock(text="What is ROS 2?")]
    type(user_msg.content[0]).text = "What is ROS 2?"

    context = RequestContext(user_id="student1")

    guardrail_func_output = GuardrailFunctionOutput(
        tripwire_triggered=True,
        output_info="Off-topic query detected"
    )
    guardrail_result = InputGuardrailResult(
        guardrail=MagicMock(spec=InputGuardrail),
        output=guardrail_func_output,
    )

    async def _raising_gen(*args, **kwargs):
        raise InputGuardrailTripwireTriggered(guardrail_result=guardrail_result)
        yield  # pragma: no cover

    with patch("chatkit_server.get_relevant_chunks", new_callable=AsyncMock, return_value=[]), \
         patch("chatkit_server.Runner.run_streamed") as mock_run, \
         patch("chatkit_server.stream_agent_response", new_callable=MagicMock) as mock_stream:

        mock_run.return_value = MagicMock()
        mock_stream.side_effect = _raising_gen

        events = []
        async for event in server.respond(thread, user_msg, context):
            events.append(event)

        assert len(events) == 1
        assert events[0].code == "custom"
        assert "Physical AI and Robotics" in events[0].message
        assert events[0].allow_retry is False


@pytest.mark.asyncio
async def test_respond_generic_error_yields_error_event():
    from chatkit_server import CustomChatKitServer
    from chatkit.types import ThreadMetadata, UserMessageItem, ActiveStatus
    from models.chat import RequestContext

    store = AsyncMock()
    store.load_thread_items = AsyncMock(return_value=MagicMock(data=[]))

    server = CustomChatKitServer(store=store)

    thread = ThreadMetadata(
        id="thread-1",
        title="Test",
        created_at=datetime.now(timezone.utc),
        status=ActiveStatus(),
        allowed_image_domains=[],
    )

    user_msg = MagicMock(spec=UserMessageItem)
    user_msg.content = [MagicMock(text="Some query")]
    type(user_msg.content[0]).text = "Some query"

    context = RequestContext(user_id="student1")

    async def _raising_gen(*args, **kwargs):
        raise RuntimeError("Unexpected failure")
        yield  # pragma: no cover

    with patch("chatkit_server.get_relevant_chunks", new_callable=AsyncMock, return_value=[]), \
         patch("chatkit_server.Runner.run_streamed") as mock_run, \
         patch("chatkit_server.stream_agent_response", new_callable=MagicMock) as mock_stream:

        mock_run.return_value = MagicMock()
        mock_stream.side_effect = _raising_gen

        events = []
        async for event in server.respond(thread, user_msg, context):
            events.append(event)

        assert len(events) == 1
        assert events[0].code == "custom"
        assert "something went wrong" in events[0].message
        assert events[0].allow_retry is True


@pytest.mark.asyncio
async def test_respond_includes_history():
    from chatkit_server import CustomChatKitServer
    from chatkit.types import ThreadMetadata, UserMessageItem, ActiveStatus
    from models.chat import RequestContext
    from chatkit.store import Page

    store = AsyncMock()

    # Mock conversation history with one user message and one assistant message
    prev_user = MagicMock()
    prev_user.type = "user_message"
    prev_user.content = [MagicMock(text="What is kinematics?")]
    type(prev_user.content[0]).text = "What is kinematics?"

    prev_assistant = MagicMock()
    prev_assistant.type = "assistant_message"
    prev_assistant.content = [MagicMock(text="Kinematics is the study of motion.")]
    type(prev_assistant.content[0]).text = "Kinematics is the study of motion."

    store.load_thread_items = AsyncMock(return_value=Page(
        data=[prev_user, prev_assistant], has_more=False
    ))

    server = CustomChatKitServer(store=store)

    thread = ThreadMetadata(
        id="thread-1",
        title="Test",
        created_at=datetime.now(timezone.utc),
        status=ActiveStatus(),
        allowed_image_domains=[],
    )

    user_msg = MagicMock(spec=UserMessageItem)
    user_msg.content = [MagicMock(text="Tell me more")]
    type(user_msg.content[0]).text = "Tell me more"

    context = RequestContext(user_id="student1")

    with patch("chatkit_server.get_relevant_chunks", new_callable=AsyncMock, return_value=[]), \
         patch("chatkit_server.Runner.run_streamed") as mock_run, \
         patch("chatkit_server.stream_agent_response") as mock_stream:

        mock_run.return_value = MagicMock()
        captured_instructions = []

        def capture_agent(**kwargs):
            if "instructions" in kwargs:
                captured_instructions.append(kwargs["instructions"])
            return MagicMock()

        with patch("chatkit_server.Agent", side_effect=capture_agent):
            mock_stream.return_value.__aiter__.return_value = iter([])

            events = []
            async for event in server.respond(thread, user_msg, context):
                events.append(event)

        assert len(captured_instructions) > 0
        instr_func = captured_instructions[0]
        ctx_wrapper = MagicMock()
        ctx_wrapper.context = {"book_chunks": []}
        result = instr_func(ctx_wrapper, MagicMock())
        assert "User:" in result
        assert "Assistant:" in result
        assert "What is kinematics?" in result
        assert "Kinematics is the study of motion." in result


@pytest.mark.asyncio
async def test_respond_includes_page_context():
    from chatkit_server import CustomChatKitServer
    from chatkit.types import ThreadMetadata, UserMessageItem, ActiveStatus
    from models.chat import RequestContext, PageContext

    store = AsyncMock()
    store.load_thread_items = AsyncMock(return_value=MagicMock(data=[]))

    server = CustomChatKitServer(store=store)

    thread = ThreadMetadata(
        id="thread-1",
        title="Test",
        created_at=datetime.now(timezone.utc),
        status=ActiveStatus(),
        allowed_image_domains=[],
    )

    user_msg = MagicMock(spec=UserMessageItem)
    user_msg.content = [MagicMock(text="Explain this")]
    type(user_msg.content[0]).text = "Explain this"

    page_ctx = PageContext(
        url="/docs/module1/chapter1",
        title="Foundations of Physical AI",
        headings=["Embodied Intelligence", "Kinematics & Dynamics"],
    )
    context = RequestContext(user_id="student1", page_context=page_ctx)

    with patch("chatkit_server.get_relevant_chunks", new_callable=AsyncMock, return_value=[]), \
         patch("chatkit_server.Runner.run_streamed") as mock_run, \
         patch("chatkit_server.stream_agent_response") as mock_stream:

        mock_run.return_value = MagicMock()
        captured_instructions = []

        def capture_agent(**kwargs):
            if "instructions" in kwargs:
                captured_instructions.append(kwargs["instructions"])
            return MagicMock()

        with patch("chatkit_server.Agent", side_effect=capture_agent):
            mock_stream.return_value.__aiter__.return_value = iter([])

            events = []
            async for event in server.respond(thread, user_msg, context):
                events.append(event)

        assert len(captured_instructions) > 0
        instr_func = captured_instructions[0]
        ctx_wrapper = MagicMock()
        ctx_wrapper.context = {"book_chunks": []}
        result = instr_func(ctx_wrapper, MagicMock())
        assert "STUDENT CONTEXT" in result
        assert "Foundations of Physical AI" in result
        assert "/docs/module1/chapter1" in result
        assert "Embodied Intelligence" in result
        assert "Kinematics & Dynamics" in result
