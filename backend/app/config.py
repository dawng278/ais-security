from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    app_name: str = "GradingGuard AI"
    env: str = "development"
    mock_llm: bool = True
    frontend_origin: str = "http://localhost:3000"
    cors_allowed_origins: str = "http://localhost:3000,http://localhost:3001"
    security_database_url: str = "sqlite:///./.local/gradingguard_security.db"
    test_database_url: str | None = None
    auth_token_secret: str = "development-only-change-me"
    auth_issuer: str = "gradingguard-local"
    auth_audience: str = "gradingguard-gateway"
    max_candidate_content_chars: int = 12000
    max_request_body_chars: int = 20000
    rate_limit_window_seconds: int = 60
    rate_limit_max_requests: int = 120

settings = Settings()


def allowed_cors_origins() -> list[str]:
    origins = [origin.strip() for origin in settings.cors_allowed_origins.split(",") if origin.strip()]
    if settings.frontend_origin and settings.frontend_origin not in origins:
        origins.append(settings.frontend_origin)
    return origins
