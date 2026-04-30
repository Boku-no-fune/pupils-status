"""
生徒スキーマ
"""

from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import date, datetime


class TeacherBrief(BaseModel):
    id: int
    name: str
    model_config = {"from_attributes": True}


class CourseBrief(BaseModel):
    id: int
    name: str
    subject: Optional[str] = None
    model_config = {"from_attributes": True}


class EnrollmentOut(BaseModel):
    id: int
    course_id: int
    course: Optional[CourseBrief] = None
    started_at: date
    ended_at: Optional[date] = None
    change_type: str
    model_config = {"from_attributes": True}


class EnrollmentEventOut(BaseModel):
    id: int
    event_type: str
    occurred_at: datetime
    note: Optional[str] = None
    model_config = {"from_attributes": True}


class AttendanceOut(BaseModel):
    id: int
    class_date: date
    status: str
    note: Optional[str] = None
    model_config = {"from_attributes": True}


class TestScoreOut(BaseModel):
    id: int
    test_id: str
    test_name: Optional[str] = None
    subject: str
    raw_score: float
    rank: Optional[int] = None
    deviation_value: Optional[float] = None
    test_date: Optional[date] = None
    model_config = {"from_attributes": True}


class TargetSchoolOut(BaseModel):
    id: int
    school_name: str
    priority: int
    recorded_at: Optional[date] = None
    model_config = {"from_attributes": True}


class SchoolGradeOut(BaseModel):
    id: int
    term: str
    subject: str
    score: Optional[float] = None
    grade_notation: Optional[str] = None
    model_config = {"from_attributes": True}


class PaymentOut(BaseModel):
    id: int
    amount: float
    paid_at: Optional[date] = None
    due_at: Optional[date] = None
    category: str
    status: str
    model_config = {"from_attributes": True}


class ParentContactOut(BaseModel):
    id: int
    contact_type: str
    occurred_at: datetime
    summary: Optional[str] = None
    teacher_id: Optional[int] = None
    teacher_name: Optional[str] = None
    model_config = {"from_attributes": True}


class SalesActionOut(BaseModel):
    id: int
    action_type: str
    target_product: Optional[str] = None
    status: str
    note: Optional[str] = None
    actioned_at: Optional[datetime] = None
    assigned_to: Optional[int] = None
    assigned_teacher_name: Optional[str] = None
    model_config = {"from_attributes": True}


class GradeChange(BaseModel):
    subject: str
    change: float  # 前回比の変化量
    direction: str  # "up" / "down" / "stable"


class RiskScore(BaseModel):
    risk_level: str  # "high" / "medium" / "low"
    attendance_rate_30d: float
    score_trend: str  # "declining" / "stable" / "improving"
    factors: List[str]
    suggestions: List[str]


class StudentOut(BaseModel):
    """生徒一覧用 (軽量)"""
    id: int
    name: str
    grade: int
    school: Optional[str] = None
    status: str
    enrolled_at: Optional[date] = None
    trial_at: Optional[date] = None
    withdrawn_at: Optional[date] = None
    assigned_teacher_id: Optional[int] = None
    assigned_teacher_name: Optional[str] = None
    classroom_id: Optional[int] = None
    # ダッシュボード用集計フィールド
    last_visit: Optional[date] = None
    attendance_rate_30d: Optional[float] = None
    recent_grade_change: Optional[GradeChange] = None

    model_config = {"from_attributes": True}


class StudentDetail(StudentOut):
    """生徒詳細用 (全関連データ含む)"""
    enrollment_events: List[EnrollmentEventOut] = []
    enrollments: List[EnrollmentOut] = []
    recent_attendances: List[AttendanceOut] = []
    test_scores: List[TestScoreOut] = []
    target_schools: List[TargetSchoolOut] = []
    school_grades: List[SchoolGradeOut] = []
    parent_contacts: List[ParentContactOut] = []
    payments: List[PaymentOut] = []
    sales_actions: List[SalesActionOut] = []
    risk_score: Optional[RiskScore] = None


class StudentCreate(BaseModel):
    name: str
    grade: int
    school: Optional[str] = None
    status: str = "trial"
    enrolled_at: Optional[date] = None
    trial_at: Optional[date] = None
    assigned_teacher_id: Optional[int] = None
    classroom_id: Optional[int] = None


class StudentUpdate(BaseModel):
    name: Optional[str] = None
    grade: Optional[int] = None
    school: Optional[str] = None
    status: Optional[str] = None
    enrolled_at: Optional[date] = None
    withdrawn_at: Optional[date] = None
    assigned_teacher_id: Optional[int] = None
