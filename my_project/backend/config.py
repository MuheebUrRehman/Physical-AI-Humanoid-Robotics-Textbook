import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration class to manage environment variables and settings."""

    COHERE_API_KEY: str = os.getenv("COHERE_API_KEY", "")
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    COHERE_MODEL: str = os.getenv("COHERE_MODEL", "embed-multilingual-v3.0")

    LLM_API_KEY: str = (
        os.getenv("LLM_API_KEY")
        or os.getenv("OPENROUTER_API_KEY")
        or os.getenv("GEMINI_API_KEY", "")
    )
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "qwen/qwen3-coder")

    LLM_SITE_URL: str = os.getenv(
        "LLM_SITE_URL",
        "https://physical-ai-humanoid-robotics-textb-three-alpha.vercel.app",
    )
    LLM_APP_NAME: str = os.getenv("LLM_APP_NAME", "Physical AI Textbook")

    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT: int = int(os.getenv("QDRANT_PORT", 6333))
    QDRANT_COLLECTION_NAME: str = os.getenv("QDRANT_COLLECTION_NAME", "book_vectors")

    TOP_K: int = int(os.getenv("TOP_K", 3))
    QUERY_TIMEOUT: int = int(os.getenv("QUERY_TIMEOUT", 30))
    STREAMING_ENABLED: bool = os.getenv("STREAMING_ENABLED", "true").lower() == "true"
    RELEVANCE_THRESHOLD: float = float(os.getenv("RELEVANCE_THRESHOLD", "0.0"))

    @classmethod
    def validate(cls) -> None:
        if not cls.COHERE_API_KEY:
            raise ValueError("COHERE_API_KEY environment variable is required")
        if not cls.QDRANT_API_KEY:
            raise ValueError("QDRANT_API_KEY environment variable is required")
        if not cls.LLM_API_KEY:
            raise ValueError(
                "LLM_API_KEY (or OPENROUTER_API_KEY / GEMINI_API_KEY) "
                "environment variable is required"
            )
        if not cls.QDRANT_HOST:
            raise ValueError("QDRANT_HOST environment variable is required")
