"""
宿題モデル
"""

from sqlalchemy import Column, Integer, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Homework(Base):
    __tablename__ = "homeworks"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)

    assigned_date = Column(Date, nullable=False)  # 宿題が出された日
    submitted_at = Column(DateTime(timezone=True), nullable=True)  # 提出日時 (Null = 未提出)
    checked_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # 確認した講師

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # リレーション
    student = relationship("Student", back_populates="homeworks")
    checker = relationship("User", back_populates="checked_homeworks")
