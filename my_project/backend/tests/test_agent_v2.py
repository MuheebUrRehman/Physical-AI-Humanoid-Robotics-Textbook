import pytest
from pydantic import ValidationError
from models.chat import AgentResponse

def test_agent_response_validation():
    """Test that AgentResponse correctly validates its fields."""
    # Valid response
    valid_data = {
        "answer": "This is a test answer.",
        "confidence": 0.95,
        "citations": ["doc1.md", "doc2.md"]
    }
    response = AgentResponse(**valid_data)
    assert response.answer == valid_data["answer"]
    assert response.confidence == valid_data["confidence"]
    assert response.citations == valid_data["citations"]

    # Invalid confidence (out of range)
    invalid_data = valid_data.copy()
    invalid_data["confidence"] = 1.5
    with pytest.raises(ValidationError):
        AgentResponse(**invalid_data)

    # Missing required field
    missing_field_data = {
        "confidence": 0.8,
        "citations": []
    }
    with pytest.raises(ValidationError):
        AgentResponse(**missing_field_data)
