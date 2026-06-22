"""
テスト成績・志望校・学校成績モデル
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date, Float, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class TestScore(Base):
    """
    塾内テスト成績
    item_results: 設問別正誤データ (JSON)
    """
    __tablename__ = "test_scores"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)

    test_id = Column(String(50), nullable=False, index=True)  # 例: "2024-09"
    test_name = Column(String(100), nullable=True)             # 例: "2024年9月模試"
    # 試験種別: 塾内試験A/塾内試験B/業者模試A/業者模試B/学校定期テスト/その他
    test_type = Column(String(30), nullable=True, index=True)
    subject = Column(String(20), nullable=False)               # 国語/数学/英語/理科/社会
    raw_score = Column(Float, nullable=False)
    rank = Column(Integer, nullable=True)                      # 順位
    deviation_value = Column(Float, nullable=True)             # 偏差値
    item_results = Column(JSON, nullable=True)                 # 設問別結果 (JSONB)

    test_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # リレーション
    student = relationship("Student", back_populates="test_scores")


class TargetSchool(Base):
    """
    志望校
    priority: 第一志望=1, 第二志望=2 ...
    """
    __tablename__ = "target_schools"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)

    school_name = Column(String(200), nullable=False)
    priority = Column(Integer, nullable=False, default=1)
    recorded_at = Column(Date, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # リレーション
    student = relationship("Student", back_populates="target_schools")


class SchoolGrade(Base):
    """
    学校の成績 (通知表)
    term: "2024-前期" など
    grade_notation: 5段階/ABC評価など
    """
    __tablename__ = "school_grades"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)

    term = Column(String(50), nullable=False)   # 例: "2024-前期"
    subject = Column(String(20), nullable=False)
    score = Column(Float, nullable=True)
    grade_notation = Column(String(10), nullable=True)  # 例: "4", "B+"

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # リレーション
    student = relationship("Student", back_populates="school_grades")
