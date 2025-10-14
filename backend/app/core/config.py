"""Application configuration utilities."""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Dict, List

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, field_validator, model_validator


class Settings(BaseModel):
    """Runtime configuration sourced from environment variables."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

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

    @field_validator("cors_origins", mode="before")
    def split_cors_origins(cls, value: str | List[str]) -> List[AnyHttpUrl]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @field_validator("storage_root", mode="before")
    def expand_storage_root(cls, value: str | Path) -> Path:
        path = Path(value).expanduser()
        base_dir = Path(__file__).resolve().parents[2]
        if not path.is_absolute():
            path = base_dir / path
        return path.resolve()

    @model_validator(mode="after")
    def validate_azure_settings(cls, values: "Settings") -> "Settings":
        """Ensure that Azure OAuth configuration is complete."""

        client_secret = values.azure_client_secret
        frontend_redirect = values.azure_redirect_uri_frontend
        backend_redirect = values.azure_redirect_uri_backend

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

    @classmethod
    def _load_env_file(cls, path: Path) -> Dict[str, str]:
        data: Dict[str, str] = {}
        if not path.exists():
            return data
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            data[key.strip()] = value.strip().strip('"').strip("'")
        return data

    @classmethod
    def load(cls) -> "Settings":
        """Instantiate settings from environment variables and optional .env file."""

        base_dir = Path(__file__).resolve().parents[2]
        env_file_values = cls._load_env_file(base_dir / ".env")
        combined_env: Dict[str, str] = {**env_file_values, **os.environ}

        init_values: Dict[str, object] = {}
        for field_name, field in cls.model_fields.items():
            alias = field.alias or field_name
            if alias in combined_env:
                init_values[field_name] = combined_env[alias]

        return cls(**init_values)


@lru_cache
def get_settings() -> Settings:
    """Return memoized settings instance."""

    return Settings.load()
