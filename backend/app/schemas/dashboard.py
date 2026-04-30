"""
ダッシュボード集計スキーマ
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class DashboardStats(BaseModel):
    """ダッシュボード上部サマリーカード用"""
    total_enrolled: int
    total_trial: int
    total_on_leave: int
    total_withdrawn: int
    high_risk_count: int
    avg_attendance_rate: float


class AttendanceTrendPoint(BaseModel):
    """出席率推移 (Tab2 折れ線グラフ用)"""
    month: str          # 例: "2024-10"
    present_count: int
    absent_count: int
    late_count: int
    rate: float         # 出席率 (0-100)


class ScoreTrendPoint(BaseModel):
    """成績推移 (Tab2 棒グラフ用)"""
    test_id: str
    test_name: str
    test_date: Optional[str] = None
    scores: Dict[str, float]  # subject -> avg_score


class SalesProgress(BaseModel):
    """営業目標進捗 (Tab3用)"""
    goal_id: int
    goal_type: str
    target_product: Optional[str] = None
    target_count: int
    period: str
    signed_up: int
    in_progress: int
    declined: int
    not_started: int
    progress_pct: float


class RiskStudent(BaseModel):
    """リスク生徒 (Tab4用)"""
    student_id: int
    student_name: str
    grade: int
    status: str
    risk_level: str
    attendance_rate_30d: float
    score_trend: str
    factors: List[str]
    suggestions: List[str]
