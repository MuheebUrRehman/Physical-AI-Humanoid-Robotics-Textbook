import os
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class to manage environment variables and settings."""

    # API Keys
    COHERE_API_KEY: str = os.getenv("COHERE_API_KEY", "")
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # LLM Provider (OpenRouter with Gemini fallback)
    # Priority: LLM_API_KEY → OPENROUTER_API_KEY → GEMINI_API_KEY
    LLM_API_KEY: str = (
        os.getenv("LLM_API_KEY")
        or os.getenv("OPENROUTER_API_KEY")
        or os.getenv("GEMINI_API_KEY", "")
    )
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "qwen/qwen3-coder")

    # OpenRouter identity headers
    LLM_SITE_URL: str = os.getenv(
        "LLM_SITE_URL",
        "https://physical-ai-humanoid-robotics-textbook.vercel.app",
    )
    LLM_APP_NAME: str = os.getenv("LLM_APP_NAME", "Physical AI Textbook")

    # Qdrant Configuration
    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT: int = int(os.getenv("QDRANT_PORT", 6333))
    QDRANT_COLLECTION_NAME: str = os.getenv("QDRANT_COLLECTION_NAME", "book_vectors")

    # Application Settings
    TOP_K: int = int(os.getenv("TOP_K", 5))
    QUERY_TIMEOUT: int = int(os.getenv("QUERY_TIMEOUT", 30))
    STREAMING_ENABLED: bool = os.getenv("STREAMING_ENABLED", "true").lower() == "true"

    # Validation
    @classmethod
    def validate(cls) -> None:
        """Validate that required configuration values are present."""
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
