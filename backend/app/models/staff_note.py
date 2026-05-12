"""
スタッフ記録モデル
講師が入力する電話報告・保護者面談・生徒ミーティング記録など
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class StaffNote(Base):
    """
    講師記録
    note_type: 電話報告 / 保護者面談 / 生徒ミーティング / その他
    """
    __tablename__ = "staff_notes"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    note_type = Column(String(30), nullable=False)   # 電話報告/保護者面談/生徒ミーティング/その他
    content = Column(Text, nullable=False)            # 記録内容
    occurred_at = Column(DateTime(timezone=True), nullable=False)  # 発生日時

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # リレーション
    student = relationship("Student", back_populates="staff_notes")
    teacher = relationship("User", back_populates="staff_notes")
