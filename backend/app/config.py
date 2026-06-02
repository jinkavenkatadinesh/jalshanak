import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "JalRakshak API"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "b4f8d9c228a6d47b1983fbe2e92cbb32e3612845c478aef9f3a9e3d93bfb1234")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Automatic fallback to SQLite if PostgreSQL URL is not defined
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./jalrakshak.db")

    # Media upload directory
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
