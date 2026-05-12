"""
ユーザーモデル (講師・管理者・アルバイト)
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)

    # ロール: admin / room_manager / teacher / parttime
    role = Column(String(20), nullable=False, default="teacher")

    # 所属教室 (adminは全教室アクセス可)
    classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # リレーション
    classroom = relationship("Classroom", back_populates="users")
    assigned_students = relationship("Student", back_populates="assigned_teacher",
                                     foreign_keys="Student.assigned_teacher_id")
    parent_contacts = relationship("ParentContact", back_populates="teacher")
    sales_actions = relationship("SalesAction", back_populates="assigned_teacher",
                                 foreign_keys="SalesAction.assigned_to")
    checked_homeworks = relationship("Homework", back_populates="checker")
    created_sales_goals = relationship("SalesGoal", back_populates="creator")
    staff_notes = relationship("StaffNote", back_populates="teacher")
