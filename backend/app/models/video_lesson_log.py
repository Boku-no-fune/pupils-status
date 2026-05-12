"""
映像授業視聴ログモデル
外部システムからのインポートデータを格納
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class VideoLessonLog(Base):
    """
    映像授業の視聴ログ
    外部システム（映像授業システム等）からCSVインポートで蓄積
    """
    __tablename__ = "video_lesson_logs"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)

    lesson_name = Column(String(200), nullable=False)       # 授業名
    lesson_category = Column(String(50), nullable=True)     # 科目・カテゴリ
    viewed_at = Column(DateTime(timezone=True), nullable=False)  # 視聴日時
    duration_minutes = Column(Float, nullable=False, default=0)  # 視聴時間（分）
    completion_rate = Column(Float, nullable=True)           # 完了率 (0.0〜100.0)

    # インポート管理
    source_system = Column(String(50), nullable=True)       # 取込元システム名
    imported_at = Column(DateTime(timezone=True), server_default=func.now())

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # リレーション
    student = relationship("Student", back_populates="video_lesson_logs")
