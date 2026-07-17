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
    student_token_secret: str = "student-development-only-change-me"
    student_access_token_ttl_seconds: int = 1800
    student_refresh_token_ttl_seconds: int = 604800
    student_max_devices: int = 2
    student_session_cookie_name: str = "gg_student_access"
    student_refresh_cookie_name: str = "gg_student_refresh"
    student_login_max_attempts_per_email: int = 5
    student_login_window_seconds_per_email: int = 300
    student_login_max_attempts_per_ip: int = 20
    student_login_window_seconds_per_ip: int = 300
    student_register_max_attempts_per_ip: int = 10
    student_register_window_seconds_per_ip: int = 3600

settings = Settings()


def allowed_cors_origins() -> list[str]:
    origins = [origin.strip() for origin in settings.cors_allowed_origins.split(",") if origin.strip()]
    if settings.frontend_origin and settings.frontend_origin not in origins:
        origins.append(settings.frontend_origin)
    return origins


def student_cookie_secure() -> bool:
    """Cookies must not set Secure over plain HTTP (localhost demo, dev) --
    browsers silently refuse to store them, which is exactly the bug fixed
    previously for the 127.0.0.1/localhost hostname mismatch. Secure is only
    turned on when ENV=production, where the deployment is expected to serve
    over HTTPS."""
    return settings.env == "production"
