from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    api_key: str = "change-me"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/invoice_ai"

    model_config = SettingsConfigDict(env_prefix="INVOICE_AI_", env_file=".env", extra="ignore")


settings = Settings()
