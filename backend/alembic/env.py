"""
Alembic環境設定
app.modelsの全テーブルを自動検出してマイグレーション生成
"""

import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from app.database import Base

# 全モデルをインポート (Alembicがテーブルを検出できるようにする)
import app.models  # noqa

# Alembic Config
config = context.config

# 環境変数のDATABASE_URLを使用
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# ロギング設定
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Baseのメタデータをターゲットに設定
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """オフラインモード: SQLを出力するだけでDBに接続しない"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """オンラインモード: DBに接続してマイグレーションを実行"""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
