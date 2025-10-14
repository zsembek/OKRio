"""Application configuration utilities."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import AnyHttpUrl, BaseSettings, Field, root_validator, validator


class Settings(BaseSettings):
    """Runtime configuration sourced from environment variables."""

    project_name: str = Field("OKRio", description="Human readable project name")
    environment: str = Field("development", description="Deployment environment name")

    backend_url: AnyHttpUrl = Field(..., alias="BACKEND_URL")
    frontend_url: AnyHttpUrl = Field(..., alias="FRONTEND_URL")
    admin_email: str = Field(..., alias="ADMIN_EMAIL")

    postgres_url: str = Field(..., alias="POSTGRES_URL")
    redis_url: str = Field(..., alias="REDIS_URL")

    jwt_secret: str = Field(..., alias="JWT_SECRET")
    cors_origins: List[AnyHttpUrl] = Field(default_factory=list, alias="CORS_ORIGINS")

    rate_limit_requests: int = Field(1000, alias="RATE_LIMIT_REQUESTS")
    rate_limit_window_seconds: int = Field(60, alias="RATE_LIMIT_WINDOW_SECONDS")

    storage_root: Path = Field(Path("./var/storage"), alias="STORAGE_ROOT")

    azure_tenant_id: str = Field(..., alias="AZURE_TENANT_ID")
    azure_client_id: str = Field(..., alias="AZURE_CLIENT_ID")
    azure_client_secret: str | None = Field(None, alias="AZURE_CLIENT_SECRET")
    azure_redirect_uri_frontend: AnyHttpUrl = Field(..., alias="AZURE_REDIRECT_URI_FRONTEND")
    azure_redirect_uri_backend: AnyHttpUrl | None = Field(
        None, alias="AZURE_REDIRECT_URI_BACKEND"
    )
    azure_logout_redirect_uri: AnyHttpUrl = Field(..., alias="AZURE_LOGOUT_REDIRECT_URI")
    azure_oauth_scopes: str = Field(..., alias="AZURE_OAUTH_SCOPES")
    azure_authority: AnyHttpUrl = Field(..., alias="AZURE_AUTHORITY")
    ms_graph_base_url: AnyHttpUrl = Field(..., alias="MS_GRAPH_BASE_URL")
    ms_graph_scopes: str = Field(..., alias="MS_GRAPH_SCOPES")

    rabbitmq_url: str | None = Field(None, alias="RABBITMQ_URL")

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"

    @validator("cors_origins", pre=True)
    def split_cors_origins(cls, value: str | List[str]) -> List[AnyHttpUrl]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @validator("storage_root", pre=True)
    def expand_storage_root(cls, value: str | Path) -> Path:
        path = Path(value).expanduser()
        base_dir = Path(__file__).resolve().parents[2]
        if not path.is_absolute():
            path = base_dir / path
        return path.resolve()

    @root_validator
    def validate_azure_settings(cls, values: dict[str, object]) -> dict[str, object]:
        """Ensure that Azure OAuth configuration is complete."""

        client_secret = values.get("azure_client_secret")
        frontend_redirect = values.get("azure_redirect_uri_frontend")
        backend_redirect = values.get("azure_redirect_uri_backend")

        if not frontend_redirect:
            raise ValueError("AZURE_REDIRECT_URI_FRONTEND must be provided")

        if backend_redirect is None and client_secret is not None:
            raise ValueError(
                "AZURE_REDIRECT_URI_BACKEND must be configured when AZURE_CLIENT_SECRET is set"
            )

        if backend_redirect is not None and client_secret is None:
            raise ValueError(
                "AZURE_CLIENT_SECRET must be provided when AZURE_REDIRECT_URI_BACKEND is set"
            )

        return values


@lru_cache
def get_settings() -> Settings:
    """Return memoized settings instance."""

    return Settings()
