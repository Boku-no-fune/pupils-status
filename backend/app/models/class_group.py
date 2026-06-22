"""
クラス（集団部門の組分け）モデルと、複数担当講師の多対多関連テーブル

クラス命名規則:
  中1: 1G-1, 1G-2, 1L-1, 1L-2, 1T-1
  中2: 2G-1, 2G-2, 2L-1, 2L-2, 2T-1
  中3: 3R-1, 3R-2, 3D-1, 3D-2, 3T-1
  レベル: G/R=標準, L/D=応用, T=難関 (ハイフン後ろは組分け連番)
高校生には集団部門がない。
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


# クラス ⇔ 担当講師 (多対多)
class_teachers = Table(
    "class_teachers",
    Base.metadata,
    Column("class_group_id", Integer, ForeignKey("class_groups.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
)

# 生徒 ⇔ 担当講師 (多対多) — 集団生徒はクラスの講師を反映、それ以外は個別設定
student_teachers = Table(
    "student_teachers",
    Base.metadata,
    Column("student_id", Integer, ForeignKey("students.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
)


class ClassGroup(Base):
    __tablename__ = "class_groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(20), nullable=False, index=True)     # 例: "1G-1"
    grade = Column(Integer, nullable=False)                   # 7=中1, 8=中2, 9=中3
    level = Column(String(10), nullable=False)                # 標準 / 応用 / 難関
    sort_order = Column(Integer, nullable=False, default=0)   # 一覧の並び順
    classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # リレーション
    students = relationship("Student", back_populates="class_group")
    teachers = relationship("User", secondary=class_teachers, back_populates="teaching_classes")
