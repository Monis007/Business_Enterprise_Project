from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "EnterpriseIQ"
    database_url: str = "sqlite:///./enterpriseiq.db"
    redis_url: str = "redis://localhost:6379/0"
    openai_api_key: str = ""
    gemini_api_key: str = ""
    primary_provider: str = "openai"
    model_name: str = "gpt-4o-mini"
    gemini_model: str = "gemini-1.5-flash"
    min_evidence_score: float = 0.08
    cors_origins: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
