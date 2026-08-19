from functools import lru_cache
from typing import List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application Settings loaded from environment variables and .env file.
    Provides sensible defaults for local development.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "Online Coding Judge API"
    app_env: str = Field(default="development", description="Environment: development or production")

    database_url: str = Field(
        default=(
            "mssql+pyodbc://@localhost\\SQLEXPRESS/"
            "OnlineCodingJudge"
            "?driver=ODBC+Driver+18+for+SQL+Server"
            "&trusted_connection=yes"
            "&TrustServerCertificate=yes"
        ),
        description="SQLAlchemy database connection string",
    )

    jwt_secret_key: str = Field(
        default="change-this-secret-key-in-production",
        description="Secret key used for signing JWT tokens",
    )
    jwt_algorithm: str = Field(
        default="HS256",
        description="Algorithm used for signing JWT tokens",
    )
    jwt_access_token_expire_minutes: int = Field(
        default=30,
        description="Access token expiration time in minutes",
    )

    cors_origins: Union[List[str], str] = Field(
        default=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ],
        description="Allowed CORS origins for the API",
    )

    time_limit_seconds: float = Field(
        default=2.0,
        description="Execution time limit per test case in seconds",
    )
    max_output_size: int = Field(
        default=1_000_000,
        description="Maximum stdout capture size in bytes (1 MB)",
    )
    max_source_code_size: int = Field(
        default=50_000,
        description="Maximum source code character length (50 KB)",
    )
    max_input_size: int = Field(
        default=50_000,
        description="Maximum test case input size in characters (50 KB)",
    )
    max_test_cases_per_submission: int = Field(
        default=100,
        description="Maximum test cases evaluated per submission",
    )
    supported_languages: List[str] = Field(
        default=["python"],
        description="Supported programming languages for code submission",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"


@lru_cache()
def get_settings() -> Settings:
    """Singleton cached instance of application settings."""
    return Settings()
