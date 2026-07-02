from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "GradingGuard AI"
    env: str = "development"
    mock_llm: bool = True
    frontend_origin: str = "http://localhost:3000"

    class Config:
        env_file = ".env"


settings = Settings()
