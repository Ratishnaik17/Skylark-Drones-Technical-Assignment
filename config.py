from functools import lru_cache

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load .env file
load_dotenv()


class Settings(BaseSettings):
    """Application configuration."""

    # ==========================
    # LLM Configuration
    # ==========================
    OPENAI_API_KEY: str | None = Field(default=None)
    MISTRAL_API_KEY: str | None = Field(default=None)

    # ==========================
    # Monday.com Configuration
    # ==========================
    MONDAY_API_TOKEN: str
    MONDAY_API_URL: str = "https://api.monday.com/v2"

    DEALS_BOARD_ID: int
    WORK_ORDERS_BOARD_ID: int

    # ==========================
    # FastAPI
    # ==========================
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # ==========================
    # Streamlit
    # ==========================
    STREAMLIT_SERVER_PORT: int = 8501

    # ==========================
    # Logging
    # ==========================
    LOG_LEVEL: str = "INFO"

    # ==========================
    # Cache
    # ==========================
    CACHE_TTL: int = 300

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()


settings = get_settings()