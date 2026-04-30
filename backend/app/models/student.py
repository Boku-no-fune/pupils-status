"""
生徒モデル
ステータス: enrolled(在籍) / trial(体験) / on_leave(休会) / withdrawn(退会)
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)

    # 学年: 1=小1, 6=小6, 7=中1, 9=中3, 10=高1, 12=高3
    grade = Column(Integer, nullable=False)
    school = Column(String(200), nullable=True)

    # 在籍ステータス
    status = Column(String(20), nullable=False, default="enrolled")

    enrolled_at = Column(Date, nullable=True)   # 入会日
    trial_at = Column(Date, nullable=True)       # 体験日
    withdrawn_at = Column(Date, nullable=True)   # 退会日

    # 担当講師
    assigned_teacher_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # 所属教室
    classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # リレーション
    assigned_teacher = relationship("User", back_populates="assigned_students",
                                    foreign_keys=[assigned_teacher_id])
    classroom = relationship("Classroom", back_populates="students")
    enrollment_events = relationship("EnrollmentEvent", back_populates="student",
                                     order_by="EnrollmentEvent.occurred_at")
    enrollments = relationship("Enrollment", back_populates="student")
    attendances = relationship("Attendance", back_populates="student",
                               order_by="Attendance.class_date.desc()")
    room_logs = relationship("RoomLog", back_populates="student")
    homeworks = relationship("Homework", back_populates="student")
    test_scores = relationship("TestScore", back_populates="student")
    target_schools = relationship("TargetSchool", back_populates="student")
    school_grades = relationship("SchoolGrade", back_populates="student")
    payments = relationship("Payment", back_populates="student",
                            order_by="Payment.paid_at.desc()")
    parent_contacts = relationship("ParentContact", back_populates="student",
                                   order_by="ParentContact.occurred_at.desc()")
    sales_actions = relationship("SalesAction", back_populates="student",
                                 order_by="SalesAction.actioned_at.desc()")
