"""
講座モデル
"""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)  # 例: 中学英語, 高校数学
    subject = Column(String(50), nullable=True)  # 例: 英語, 数学
    description = Column(String(500), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # リレーション
    enrollments = relationship("Enrollment", back_populates="course")
