"""
Configuration management using Pydantic Settings.
All configuration is loaded from environment variables (.env file).
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
from pathlib import Path


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Environment variables are loaded from .env file automatically.
    All settings have sensible defaults for development.
    """
    
    # ============================================
    # OpenAI Configuration
    # ============================================
    openai_api_key: str
    openai_model: str = "gpt-4o"
    openai_temperature: float = 0.1
    openai_max_tokens: int = 2000
    
    # ============================================
    # Agent Configuration
    # ============================================
    agent_model_name: str = "gpt-4o"
    agent_temperature: float = 0.1
    agent_max_tokens: int = 2000
    agent_system_message: Optional[str] = None
    
    # ============================================
    # SQL Query Tool Configuration
    # ============================================
    sql_model_name: str = "gpt-3.5-turbo"
    sql_temperature: float = 0.1
    sql_max_tokens: int = 2000
    
    # ============================================
    # FAISS Configuration
    # ============================================
    faiss_urls_file: str = "urls.txt"
    faiss_additional_urls: str = ""  # Comma-separated URLs
    faiss_chunk_size: int = 1000
    faiss_chunk_overlap: int = 200
    faiss_cache_enabled: bool = True
    faiss_cache_ttl_days: int = 7
    faiss_tool_name: str = "langsmith_search"
    faiss_tool_description: str = "Search for information about LangSmith. For any questions related to LangSmith, you must use this tool."
    
    # ============================================
    # API Server Configuration
    # ============================================
    api_host: str = "0.0.0.0"
    api_port: int = 9080
    api_env: str = "development"
    api_reload: bool = True
    api_workers: int = 1
    
    # ============================================
    # Database Configuration  
    # ============================================
    crm_database_path: str = "db/crm.db"
    chinook_database_path: str = "db/chinook.db"
    
    # ============================================
    # Rate Limiting
    # ============================================
    rate_limit_enabled: bool = False
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000
    
    # ============================================
    # CORS Configuration
    # ============================================
    cors_enabled: bool = True
    cors_allow_origins: str = "http://localhost:3000,http://localhost:8080"
    
    # ============================================
    # API Documentation (OpenAPI/Swagger)
    # ============================================
    docs_enabled: bool = True
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"
    
    # ============================================
    # Logging Configuration
    # ============================================
    log_level: str = "INFO"
    log_format: str = "text"  # "text" or "json"
    log_file_enabled: bool = False
    log_file_path: str = "logs/api.log"
    
    # ============================================
    # LangSmith (Optional - for tracing)
    # ============================================
    langchain_tracing_v2: bool = False
    langchain_api_key: Optional[str] = None
    langchain_project: str = "agentic-rag-api"
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @property
    def cors_origins_list(self) -> List[str]:
        """
        Parse CORS origins from comma-separated string.
        
        Returns:
            List of allowed origin URLs
        """
        if not self.cors_allow_origins:
            return []
        return [
            origin.strip() 
            for origin in self.cors_allow_origins.split(",") 
            if origin.strip()
        ]
    
    @property
    def faiss_urls_list(self) -> List[str]:
        """
        Get list of URLs to index in FAISS.
        Combines URLs from urls.txt file and FAISS_ADDITIONAL_URLS env variable.
        
        Returns:
            List of URLs to index
        """
        urls = []
        
        # Read from urls.txt file if it exists
        urls_file = self.urls_file_full_path
        if urls_file.exists():
            with open(urls_file, 'r') as f:
                file_urls = [
                    line.strip() 
                    for line in f 
                    if line.strip() and not line.strip().startswith('#')
                ]
                urls.extend(file_urls)
        
        # Add additional URLs from environment variable
        if self.faiss_additional_urls:
            env_urls = [
                url.strip() 
                for url in self.faiss_additional_urls.split(",") 
                if url.strip()
            ]
            urls.extend(env_urls)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_urls = []
        for url in urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)
        
        return unique_urls
    
    @property
    def base_path(self) -> Path:
        """
        Get the base path of the application.
        
        Returns:
            Path to the back-end directory
        """
        return Path(__file__).parent.parent
    
    @property
    def crm_database_full_path(self) -> Path:
        """
        Get the full path to the CRM database.
        
        Returns:
            Absolute path to crm.db
        """
        return self.base_path / self.crm_database_path
    
    @property
    def chinook_database_full_path(self) -> Path:
        """
        Get the full path to the Chinook database.
        
        Returns:
            Absolute path to chinook.db
        """
        return self.base_path / self.chinook_database_path
    
    @property
    def urls_file_full_path(self) -> Path:
        """
        Get the full path to the URLs file.
        
        Returns:
            Absolute path to urls.txt
        """
        return self.base_path / self.faiss_urls_file
    
    @property
    def faiss_cache_dir(self) -> Path:
        """
        Get the FAISS cache directory path.
        
        Returns:
            Path to .faiss_cache directory
        """
        return self.base_path / ".faiss_cache"
    
    @property
    def faiss_cache_path(self) -> Path:
        """
        Get the FAISS cache file path.
        
        Returns:
            Path to FAISS index cache file
        """
        return self.faiss_cache_dir / "faiss_index"
    
    def validate_on_startup(self) -> List[str]:
        """
        Validate configuration on application startup.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check OpenAI API key
        if not self.openai_api_key or self.openai_api_key == "your_openai_api_key_here":
            errors.append("OPENAI_API_KEY is not set or is still the placeholder value")
        
        # Check if urls.txt exists
        if not self.urls_file_full_path.exists():
            errors.append(f"URLs file not found: {self.urls_file_full_path}")
        
        # Validate log level
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level.upper() not in valid_log_levels:
            errors.append(f"Invalid log level: {self.log_level}. Must be one of {valid_log_levels}")
        
        # Validate log format
        if self.log_format not in ["text", "json"]:
            errors.append(f"Invalid log format: {self.log_format}. Must be 'text' or 'json'")
        
        # Validate port
        if not (1024 <= self.api_port <= 65535):
            errors.append(f"Invalid API port: {self.api_port}. Must be between 1024 and 65535")
        
        return errors


# Global settings instance
# This is imported throughout the application
settings = Settings()
