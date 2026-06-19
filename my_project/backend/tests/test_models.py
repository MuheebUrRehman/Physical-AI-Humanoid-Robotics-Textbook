import pytest
from pydantic import ValidationError
from models.chat import (
    ChatRequest, AgentResponse, SSEMessage, ErrorResponse,
    HealthCheckResponse, PageContext, RequestContext,
    ChatKitSessionRequest, ChatKitSessionResponse
)


class TestChatRequest:
    def test_minimal_valid(self):
        req = ChatRequest(query="What is ROS?", user_id="u1", session_id="s1")
        assert req.query == "What is ROS?"

    def test_empty_query_raises(self):
        with pytest.raises(ValidationError):
            ChatRequest(query="", user_id="u1", session_id="s1")

    def test_too_long_query_raises(self):
        with pytest.raises(ValidationError):
            ChatRequest(query="a" * 2001, user_id="u1", session_id="s1")

    def test_missing_user_id_raises(self):
        with pytest.raises(ValidationError):
            ChatRequest(query="hi", session_id="s1")

    def test_missing_session_id_raises(self):
        with pytest.raises(ValidationError):
            ChatRequest(query="hi", user_id="u1")


class TestAgentResponse:
    def test_valid_response(self):
        resp = AgentResponse(answer="ROS 2 is a framework.", confidence=0.95, citations=["doc1"])
        assert resp.answer == "ROS 2 is a framework."
        assert resp.confidence == 0.95
        assert resp.citations == ["doc1"]

    def test_minimal_response(self):
        resp = AgentResponse(answer="Just an answer.", confidence=0.5)
        assert resp.citations == []

    def test_confidence_too_high_raises(self):
        with pytest.raises(ValidationError):
            AgentResponse(answer="x", confidence=1.5)

    def test_confidence_too_low_raises(self):
        with pytest.raises(ValidationError):
            AgentResponse(answer="x", confidence=-0.1)

    def test_missing_answer_raises(self):
        with pytest.raises(ValidationError):
            AgentResponse(confidence=0.8)

    def test_missing_confidence_raises(self):
        with pytest.raises(ValidationError):
            AgentResponse(answer="x")


class TestSSEMessage:
    def test_token_message(self):
        msg = SSEMessage(type="token", content="hello")
        data = msg.model_dump_json()
        assert '"type":"token"' in data
        assert '"content":"hello"' in data

    def test_final_with_agent_response(self):
        ar = AgentResponse(answer="Final answer", confidence=0.9)
        msg = SSEMessage(type="final", content=ar)
        data = msg.model_dump_json()
        assert '"type":"final"' in data
        assert '"answer":"Final answer"' in data
        assert '"confidence":0.9' in data

    def test_error_message(self):
        msg = SSEMessage(type="error", content="Something went wrong")
        data = msg.model_dump_json()
        assert '"type":"error"' in data
        assert '"content":"Something went wrong"' in data


class TestErrorResponse:
    def test_valid_error(self):
        err = ErrorResponse(error="Not found", error_code="NOT_FOUND")
        assert err.error == "Not found"

    def test_with_query_id(self):
        err = ErrorResponse(error="Error", error_code="ERR", query_id="q123")
        assert err.query_id == "q123"


class TestHealthCheckResponse:
    def test_valid_health(self):
        h = HealthCheckResponse(status="healthy", version="0.1.0", timestamp="2025-01-01T00:00:00")
        assert h.status == "healthy"
        assert h.version == "0.1.0"


class TestPageContext:
    def test_minimal(self):
        pc = PageContext(url="http://example.com", title="Test")
        assert pc.headings == []

    def test_with_headings(self):
        pc = PageContext(url="http://example.com", title="Test", headings=["H1", "H2"])
        assert len(pc.headings) == 2


class TestRequestContext:
    def test_minimal(self):
        rc = RequestContext(user_id="student1")
        assert rc.user_id == "student1"
        assert rc.page_context is None

    def test_with_page_context(self):
        pc = PageContext(url="http://example.com", title="Test")
        rc = RequestContext(user_id="student1", page_context=pc)
        assert rc.page_context.title == "Test"


class TestChatKitSessionRequest:
    def test_valid(self):
        req = ChatKitSessionRequest(user_id="student1")
        assert req.user_id == "student1"


class TestChatKitSessionResponse:
    def test_valid(self):
        resp = ChatKitSessionResponse(client_secret="sk-secret", user_id="student1")
        assert resp.thread_id is None
        assert resp.client_secret == "sk-secret"
