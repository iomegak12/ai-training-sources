"""Configuration settings for the Agentic RAG system."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")
    OPENAI_MAX_TOKENS: int = int(os.getenv("OPENAI_MAX_TOKENS", "2000"))
    OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "0.1"))
    
    # Google Serper API Configuration
    SERPER_API_KEY: str = os.getenv("SERPER_API_KEY", "")
    
    # Document Processing Configuration
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    
    # Wikipedia Configuration
    WIKIPEDIA_TOP_K: int = int(os.getenv("WIKIPEDIA_TOP_K", "1"))
    WIKIPEDIA_DOC_CONTENT_MAX_CHARS: int = int(os.getenv("WIKIPEDIA_DOC_CONTENT_MAX_CHARS", "1000"))
    
    # ArXiv Configuration
    ARXIV_TOP_K: int = int(os.getenv("ARXIV_TOP_K", "1"))
    ARXIV_DOC_CONTENT_MAX_CHARS: int = int(os.getenv("ARXIV_DOC_CONTENT_MAX_CHARS", "1000"))
    
    # LangSmith Document Source
    LANGSMITH_DOCS_URL: str = os.getenv("LANGSMITH_DOCS_URL", "https://docs.smith.langchain.com")
    
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "9090"))
    API_TITLE: str = os.getenv("API_TITLE", "Agentic RAG API")
    API_VERSION: str = os.getenv("API_VERSION", "1.0.0")
    API_DESCRIPTION: str = os.getenv("API_DESCRIPTION", "AI-powered Retrieval-Augmented Generation API with multiple search tools")
    
    # Rate Limiting Configuration
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "false").lower() == "true"
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "10"))
    RATE_LIMIT_PERIOD: int = int(os.getenv("RATE_LIMIT_PERIOD", "60"))  # seconds
    
    # CORS Configuration
    CORS_ENABLED: bool = os.getenv("CORS_ENABLED", "true").lower() == "true"
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required settings are present."""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")
        return True


# Create a singleton instance
settings = Settings()
