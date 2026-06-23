"""
アプローチ指示モデル
管理者(本部・教室長)が 部門/学年/クラス/全体 を対象に出す指示。PDF添付(base64)可。
例: 「6月第2週は返却テストの件を保護者に説明、夏期講習の意義を説明すること」
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class ApproachInstruction(Base):
    __tablename__ = "approach_instructions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)

    # 対象: 全体 / 部門 / 学年 / クラス
    target_type = Column(String(10), nullable=False, default="全体")
    target_value = Column(String(50), nullable=True)   # 例: "集団" / "9" / "3T-1"

    period = Column(String(50), nullable=True)         # 例: "2026-06 第2週"

    # PDF添付 (base64)
    pdf_data = Column(Text, nullable=True)
    pdf_filename = Column(String(255), nullable=True)

    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    creator = relationship("User", foreign_keys=[created_by])
