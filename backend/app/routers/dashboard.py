"""
ダッシュボードルーター
全4タブ用の集計エンドポイント
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.services.dashboard_service import (
    get_dashboard_stats,
    get_attendance_trend,
    get_score_trend,
    get_sales_progress,
)
from app.services.student_service import get_student_list
from app.services.risk_service import get_all_risk_students
from app.dependencies.auth import get_current_user, require_roles

router = APIRouter(prefix="/dashboard", tags=["ダッシュボード"])


@router.get("/stats")
def dashboard_stats(
    classroom_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager")),
):
    """ダッシュボード上部サマリーカード"""
    if current_user.role == "room_manager" and not classroom_id:
        classroom_id = current_user.classroom_id
    return get_dashboard_stats(db, classroom_id)


@router.get("/student-list")
def student_list_tab(
    status: Optional[str] = Query(None),
    grade: Optional[int] = Query(None),
    teacher_id: Optional[int] = Query(None),
    classroom_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Tab1: 生徒一覧 (last_visit, 出席率, 成績変化付き)"""
    if current_user.role == "room_manager" and not classroom_id:
        classroom_id = current_user.classroom_id
    elif current_user.role == "teacher":
        teacher_id = current_user.id

    return get_student_list(
        db=db,
        status=status,
        grade=grade,
        teacher_id=teacher_id,
        classroom_id=classroom_id,
        search=search,
        page=page,
        per_page=per_page,
    )


@router.get("/attendance-trend")
def attendance_trend_tab(
    classroom_id: Optional[int] = Query(None),
    months: int = Query(6, ge=1, le=12),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager")),
):
    """Tab2: 月別出席率推移 (折れ線グラフ用)"""
    if current_user.role == "room_manager" and not classroom_id:
        classroom_id = current_user.classroom_id
    return get_attendance_trend(db, classroom_id, months)


@router.get("/score-trend")
def score_trend_tab(
    classroom_id: Optional[int] = Query(None),
    months: int = Query(6, ge=1, le=24),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager")),
):
    """Tab2: 科目別平均スコア推移 (棒グラフ用)"""
    if current_user.role == "room_manager" and not classroom_id:
        classroom_id = current_user.classroom_id
    return get_score_trend(db, classroom_id, months)


@router.get("/risk-students")
def risk_students_tab(
    classroom_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager")),
):
    """Tab4: リスク生徒一覧 (高→中→低順)"""
    if current_user.role == "room_manager" and not classroom_id:
        classroom_id = current_user.classroom_id
    return get_all_risk_students(db, classroom_id)


@router.get("/sales-progress")
def sales_progress_tab(
    period: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager")),
):
    """Tab3: 営業目標進捗"""
    return get_sales_progress(db, period)
