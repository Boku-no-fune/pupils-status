"""
受講講座・入退会イベントモデル
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class EnrollmentEvent(Base):
    """
    入退会イベント履歴
    event_type: 資料請求/体験/入会/休会/退会/講習申込 等
    """
    __tablename__ = "enrollment_events"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)

    # イベント種別
    event_type = Column(String(50), nullable=False)
    occurred_at = Column(DateTime(timezone=True), nullable=False)
    note = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # リレーション
    student = relationship("Student", back_populates="enrollment_events")


class Enrollment(Base):
    """
    受講講座 (どの生徒がどの講座を受講しているか)
    change_type: 新規/追加/変更
    """
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)

    started_at = Column(Date, nullable=False)
    ended_at = Column(Date, nullable=True)  # Null = 現在も受講中
    change_type = Column(String(20), nullable=False, default="新規")

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # リレーション
    student = relationship("Student", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")
