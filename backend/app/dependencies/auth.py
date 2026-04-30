"""
認証依存関係
FastAPI Depends() で使用するユーザー認証・ロール制御
"""

from typing import List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.auth_service import verify_token
from app.models.user import User

# OAuthトークンスキーム
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    JWTトークンからログイン中のユーザーを取得
    トークン無効またはユーザーが存在しない場合は401を返す
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="認証情報が無効です",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = verify_token(token)
    if payload is None:
        raise credentials_exception

    user_id: int = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception

    return user


def require_roles(*roles: str):
    """
    指定されたロールのいずれかを持つユーザーのみアクセスを許可する依存関係ファクトリ
    使用例: Depends(require_roles('admin', 'room_manager'))
    """
    def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"このリソースには {', '.join(roles)} ロールが必要です"
            )
        return current_user
    return checker
