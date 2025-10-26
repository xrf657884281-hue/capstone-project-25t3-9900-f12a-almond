"""
Configuration file for MCP Fake News Detection System
"""
import os
from typing import Optional

class Config:
    """System configuration class"""
    
    # API Configuration
    API_PROVIDER: str = os.getenv("API_PROVIDER", "openai")  # "openai" only
    
    # OpenAI API Keys
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", "os.getenv("OPENAI_API_KEY")")
    
    # Database Configuration
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DATABASE: str = os.getenv("MONGODB_DATABASE", "fakenews_db")
    
    # Model Configuration
    DEFAULT_GPT_MODEL: str = "gpt-4o"
    AVAILABLE_GPT_MODELS: list = ["gpt-3.5-turbo", "gpt-4", "gpt-4o", "gpt-4-turbo-preview"]
    
    # Detection Configuration
    DETECTION_THRESHOLD: float = 0.5
    CONFIDENCE_THRESHOLD: float = 0.7
    
    # Generation Configuration
    MAX_TOKENS: int = 500
    TEMPERATURE: float = 0.8
    TOP_P: float = 0.9
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/fakenews.log")
    
    # Security Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate configuration completeness"""
        if not cls.OPENAI_API_KEY:
            print("Warning: OPENAI_API_KEY not set. Services will not work.")
            return False
        return True
    
    @classmethod
    def get_api_client_config(cls) -> dict:
        """Get API client configuration"""
        return {
            "api_key": cls.OPENAI_API_KEY,
            "timeout": 30,
            "max_retries": 3
        }
    
    @classmethod
    def get_default_model(cls) -> str:
        """Get default model"""
        return cls.DEFAULT_GPT_MODEL
