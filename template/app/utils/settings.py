from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "{{APP_NAME}}"
    app_description: str = """
{{APP_DESCRIPTION}}
"""
    app_version: str = "0.1.0"
    fastapi_debug: bool = False
    env: Literal["development", "production", "testing"] = "development"
    fastapi_host: str = "0.0.0.0"
    fastapi_port: int = 8000
    fastapi_reload: bool = True
    fastapi_log_level: str = "info"

    # Database
    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/{{APP_NAME}}"
    )
    test_database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/{{APP_NAME}}_test"
    )

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    def get_database_url(self) -> str:
        if self.env == "testing":
            return self.test_database_url
        return self.database_url


settings = Settings()
