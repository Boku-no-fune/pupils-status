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

    # 部門: 集団 / 個別 / 自立
    division = Column(String(10), nullable=True)

    # コース種別
    # 集団: 低学年/中学受験（国私立）/中学受験（公立中高一貫）/高校受験/大学受験
    # 個別: 中学受験/高校受験/大学受験
    # 自立: 映像/速読/Lepton英語/学研教室
    course_type = Column(String(30), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # リレーション
    enrollments = relationship("Enrollment", back_populates="course")
