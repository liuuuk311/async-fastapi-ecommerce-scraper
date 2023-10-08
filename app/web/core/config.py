import os
import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, EmailStr, PostgresDsn, validator


class Settings(BaseSettings):
    API_PREFIX: str = "/api/v2"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 15  # = 15 minutes
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # = 30 days
    ALGORITHM = "HS256"

    BACKEND_CORS_ORIGINS: List[Union[AnyHttpUrl, str]] = os.getenv("CORS_ORIGINS", "")

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(";")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PROJECT_NAME: str = "FPV finder"
    VERSION: str = "2.0.5"

    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_DB: str = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT")
    DATABASE_URI: Optional[PostgresDsn] = None

    @validator("DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_HOST"),
            port=values.get("POSTGRES_PORT"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    RESEND_API_KEY: str = os.getenv("RESEND_API_KEY")
    EMAILS_FROM_EMAIL: Optional[EmailStr] = "support@fpvfinder.lucafpv.com"
    EMAILS_FROM_NAME: Optional[str] = "FPVFinder"

    @validator("EMAILS_FROM_NAME")
    def get_project_name(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if not v:
            return values["PROJECT_NAME"]
        return v

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48
    EMAIL_TEMPLATES_DIR: str = ""

    EMAIL_TEST_USER: EmailStr = "test@example.com"  # type: ignore
    FIRST_SUPERUSER: EmailStr = os.getenv("SUPERUSER_EMAIL")
    FIRST_SUPERUSER_PASSWORD: str = os.getenv("SUPERUSER_PASSWORD")
    USERS_OPEN_REGISTRATION: bool = False

    MAX_RETRIES_SECONDS = 60 * 5
    WAIT_SECONDS = 1

    LOG_LEVEL: str = os.getenv("LOG_LEVEL") or "DEBUG"
    ENV: str = os.getenv("ENV", "production")
    IS_PROD: bool = ENV == "production"

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
