from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "PlanQuest"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://planquest:planquest_secret@postgres:5432/planquest"

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # Telegram
    BOT_TOKEN: str = ""
    WEBHOOK_URL: str = ""
    MINI_APP_URL: str = ""  # Frontend URL for Telegram Mini App button

    # Security
    SECRET_KEY: str = "change-me-in-production"
    JWT_EXPIRE_DAYS: int = 7

    # AI
    OPENAI_API_KEY: str = ""
    AI_MODEL_DEFAULT: str = "gpt-4o-mini"
    AI_MODEL_ADVANCED: str = "gpt-4o"
    AI_DAILY_LIMIT: int = 30  # max AI calls per premium user per day

    # CORS
    CORS_ORIGINS: list[str] = ["*"]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()
