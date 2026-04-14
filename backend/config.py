from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str

    # JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # App
    app_name: str = "BlueCrow Compliance Portal"
    debug: bool = False

    class Config:
        env_file = ".env"


# Instância global — importar com: from backend.config import settings
settings = Settings()
