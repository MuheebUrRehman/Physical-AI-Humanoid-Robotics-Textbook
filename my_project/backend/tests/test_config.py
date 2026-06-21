import os
import pytest


def test_config_validate_success():
    from config import Config
    Config.validate()


def test_config_defaults():
    from config import Config
    assert Config.TOP_K == 3
    assert Config.QUERY_TIMEOUT == 30
    assert Config.RELEVANCE_THRESHOLD == 0.0
    assert Config.COHERE_MODEL == "embed-multilingual-v3.0"
    assert Config.LLM_MODEL == "qwen/qwen3-coder"
    assert Config.QDRANT_COLLECTION_NAME == "book_vectors"


def test_config_cohere_model_in_env():
    assert os.getenv("COHERE_MODEL", "embed-multilingual-v3.0") == "embed-multilingual-v3.0"


def test_config_validation_fails_without_api_keys(monkeypatch):
    from config import Config
    monkeypatch.setattr(Config, "COHERE_API_KEY", "")
    monkeypatch.setattr(Config, "QDRANT_API_KEY", "")
    monkeypatch.setattr(Config, "LLM_API_KEY", "")
    monkeypatch.setattr(Config, "QDRANT_HOST", "")
    with pytest.raises(ValueError):
        Config.validate()
