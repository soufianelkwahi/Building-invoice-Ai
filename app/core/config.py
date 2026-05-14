from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Invoice AI"
    debug: bool = True
    database_url: str = "sqlite:///./data/invoices.db"
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = "google/gemma-4-26b-a4b-it:free"
    api_key: str = "sk-invoice-ai-dev"
    upload_dir: str = "./data/raw"
    allowed_extensions: list[str] = [".pdf", ".png", ".jpg", ".jpeg", ".tiff"]
    max_file_size: int = 10 * 1024 * 1024

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
