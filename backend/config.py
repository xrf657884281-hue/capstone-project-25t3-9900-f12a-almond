"""
Configuration file for MCP Fake News Detection System
"""
import os
from typing import Optional

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded .env file")
except ImportError:
    print("⚠️ python-dotenv not installed. Environment variables from .env will not be loaded.")
    print("⚠️ Install with: pip install python-dotenv")

class Config:
    """System configuration class"""
    
    # API Configuration
    API_PROVIDER: str = os.getenv("API_PROVIDER", "openai")  # "openai" only
    
    # OpenAI API Keys
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # News API Configuration
    # Default API key hardcoded for public use (can be overridden by environment variable)
    NEWS_API_KEY: Optional[str] = os.getenv("NEWS_API_KEY", "9dc4f9221b704bde9750032343c57b3c")
    NEWS_API_BASE_URL: str = os.getenv("NEWS_API_BASE_URL", "https://newsapi.org/v2")
    
    # SerpAPI Configuration (Google News search)
    SERPAPI_KEY: Optional[str] = os.getenv("SERPAPI_KEY")
    SERPAPI_BASE_URL: str = "https://serpapi.com/search"
    
    # Database Configuration

    # MONGODB_USER/MONGODB_PASSWORD/MONGODB_HOST/MONGODB_PORT/MONGODB_DATABASE
    MONGODB_USER: Optional[str] = os.getenv("MONGODB_USER", os.getenv("MONGO_INITDB_ROOT_USERNAME", "admin"))
    MONGODB_PASSWORD: Optional[str] = os.getenv("MONGODB_PASSWORD", os.getenv("MONGO_INITDB_ROOT_PASSWORD", "admin123"))
    MONGODB_HOST: str = os.getenv("MONGODB_HOST", "127.0.0.1")
    MONGODB_PORT: str = os.getenv("MONGODB_PORT", "27017")
    MONGODB_DATABASE: str = os.getenv("MONGODB_DATABASE", os.getenv("MONGO_INITDB_DATABASE", "fakenews_db"))
  
    MONGODB_URL: str = os.getenv(
        "MONGODB_URL",
        f"mongodb://{MONGODB_USER}:{MONGODB_PASSWORD}@{MONGODB_HOST}:{MONGODB_PORT}/{MONGODB_DATABASE}?authSource=admin"
    )
    
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
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", SECRET_KEY)
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    
    # PDF Storage Configuration
    PDF_STORAGE_BASE_PATH: str = os.getenv("PDF_STORAGE_BASE_PATH", "storage")
    PDF_AUTO_GENERATE: bool = os.getenv("PDF_AUTO_GENERATE", "true").lower() == "true"
    
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

    @classmethod
    def get_mongo_url(cls) -> str:
        """获取 Mongo 连接字符串（优先使用已设置的 MONGODB_URL）"""
        return cls.MONGODB_URL
    