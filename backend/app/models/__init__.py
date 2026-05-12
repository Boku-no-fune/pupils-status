"""
全モデルをインポート — Alembicがautogenerateで全テーブルを検出できるようにする
"""

from app.models.classroom import Classroom
from app.models.user import User
from app.models.course import Course
from app.models.student import Student
from app.models.enrollment import EnrollmentEvent, Enrollment
from app.models.attendance import Attendance, RoomLog
from app.models.homework import Homework
from app.models.test_score import TestScore, TargetSchool, SchoolGrade
from app.models.payment import Payment
from app.models.contact import ParentContact
from app.models.sales import SalesAction, SalesGoal
from app.models.staff_note import StaffNote
from app.models.video_lesson_log import VideoLessonLog

__all__ = [
    "Classroom",
    "User",
    "Course",
    "Student",
    "EnrollmentEvent",
    "Enrollment",
    "Attendance",
    "RoomLog",
    "Homework",
    "TestScore",
    "TargetSchool",
    "SchoolGrade",
    "Payment",
    "ParentContact",
    "SalesAction",
    "SalesGoal",
    "StaffNote",
    "VideoLessonLog",
]
