"""
FastAPIアプリケーション エントリーポイント
ミドルウェア・ルーター・ヘルスチェックを設定する
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, students, attendances, contacts, sales, dashboard, ai, prospects

# FastAPIアプリ作成
app = FastAPI(
    title="学習塾CRM",
    description="学習塾校務管理システムのCRM機能API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORSミドルウェア設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:5173",  # Vite開発サーバー
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ヘルスチェックエンドポイント (Railway の healthcheck に使用)
@app.get("/api/health", tags=["ヘルス"])
def health_check():
    """サーバーの稼働確認"""
    return {"status": "ok", "version": "1.0.0"}


# 全ルーターを /api プレフィックスでマウント
app.include_router(auth.router, prefix="/api")
app.include_router(students.router, prefix="/api")
app.include_router(attendances.router, prefix="/api")
app.include_router(contacts.contact_router, prefix="/api")
app.include_router(contacts.score_router, prefix="/api")
app.include_router(contacts.payment_router, prefix="/api")
app.include_router(sales.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(ai.router, prefix="/api")
app.include_router(prospects.router, prefix="/api")
