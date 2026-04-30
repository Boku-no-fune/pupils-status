"""
データベース接続設定
SQLAlchemy エンジン・セッション・Baseモデルを定義する
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# PostgreSQL接続エンジン
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # 接続の健全性チェック
    pool_size=10,
    max_overflow=20,
)

# セッションファクトリ
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 全モデルの基底クラス
Base = declarative_base()


def get_db():
    """
    FastAPI依存関係: DBセッションを提供し、リクエスト終了時にクローズ
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
