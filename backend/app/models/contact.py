"""
保護者コンタクト履歴モデル
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class ParentContact(Base):
    """
    保護者とのコンタクト記録
    contact_type: 保護者会/面談/電話報告/テキスト報告/メール
    """
    __tablename__ = "parent_contacts"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    contact_type = Column(String(50), nullable=False)
    occurred_at = Column(DateTime(timezone=True), nullable=False)
    summary = Column(Text, nullable=True)  # 対応内容メモ

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # リレーション
    student = relationship("Student", back_populates="parent_contacts")
    teacher = relationship("User", back_populates="parent_contacts")
