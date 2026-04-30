"""
アプリケーション設定
環境変数から設定を読み込む (pydantic-settings)
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # データベース
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/pupils_status"

    # JWT認証
    SECRET_KEY: str = "change-me-in-production-use-secrets-token-urlsafe-32"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24時間

    # CORS
    FRONTEND_URL: str = "http://localhost:5173"

    # Claude API (任意 — 設定するとリアルAIが有効になる)
    ANTHROPIC_API_KEY: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
