"""
出欠・入退室ログモデル
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Attendance(Base):
    """
    出欠記録
    status: present(出席) / absent(欠席) / late(遅刻) / early_leave(早退)
    """
    __tablename__ = "attendances"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)

    class_date = Column(Date, nullable=False, index=True)
    status = Column(String(20), nullable=False, default="present")
    note = Column(Text, nullable=True)

    # 欠席時のフォロー: 映像視聴 / 振替 / None
    makeup_type = Column(String(20), nullable=True)
    makeup_note = Column(String(100), nullable=True)   # 振替先クラス・視聴映像名など

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # リレーション
    student = relationship("Student", back_populates="attendances")


class RoomLog(Base):
    """
    入退室ログ (ICカード・QRコード読み取り等)
    """
    __tablename__ = "room_logs"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)

    entered_at = Column(DateTime(timezone=True), nullable=False)
    exited_at = Column(DateTime(timezone=True), nullable=True)  # Null = まだ退室していない

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # リレーション
    student = relationship("Student", back_populates="room_logs")
