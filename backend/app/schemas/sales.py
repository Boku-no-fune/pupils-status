"""
営業アクション・目標スキーマ
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SalesActionCreate(BaseModel):
    student_id: int
    action_type: str
    target_product: Optional[str] = None
    status: str = "pending"
    note: Optional[str] = None
    assigned_to: Optional[int] = None
    actioned_at: Optional[datetime] = None


class SalesActionUpdate(BaseModel):
    action_type: Optional[str] = None
    target_product: Optional[str] = None
    status: Optional[str] = None
    note: Optional[str] = None
    assigned_to: Optional[int] = None


class SalesGoalCreate(BaseModel):
    goal_type: str
    target_product: Optional[str] = None
    target_count: int
    period: str


class AttendanceCreate(BaseModel):
    student_id: int
    class_date: str
    status: str = "present"
    note: Optional[str] = None


class ParentContactCreate(BaseModel):
    student_id: int
    contact_type: str
    occurred_at: datetime
    summary: Optional[str] = None
    teacher_id: Optional[int] = None
