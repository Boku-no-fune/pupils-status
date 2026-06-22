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
    get_stat_students,
)
from app.services.student_service import get_student_list
from app.services.risk_service import get_all_risk_students
from app.services.learning_service import get_learning_progress
from app.dependencies.auth import get_current_user, require_roles
from app.models.class_group import ClassGroup
from app.models.student import Student

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
    school_type: Optional[str] = Query(None),
    division: Optional[str] = Query(None),
    sort_by: str = Query("grade"),
    sort_dir: str = Query("asc"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Tab1: 生徒一覧 (会員番号・クラス・出席率・成績変化付き)"""
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
        school_type=school_type,
        division=division,
        sort_by=sort_by,
        sort_dir=sort_dir,
        page=page,
        per_page=per_page,
    )


@router.get("/stat-students")
def stat_students(
    kind: str = Query(..., description="on_leave / high_risk / low_attendance"),
    classroom_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager")),
):
    """上部サマリーカードのドリルダウン (クリックで該当生徒をポップアップ表示)"""
    if current_user.role == "room_manager" and not classroom_id:
        classroom_id = current_user.classroom_id
    return get_stat_students(db, kind, classroom_id)


@router.get("/classes")
def list_classes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """クラス一覧 (グラフのクラス別絞り込み・比較用)。在籍生徒数も付加。"""
    classes = db.query(ClassGroup).order_by(ClassGroup.sort_order).all()
    out = []
    for c in classes:
        count = db.query(Student).filter(
            Student.class_group_id == c.id,
            Student.status.in_(["enrolled", "trial"]),
        ).count()
        out.append({
            "id": c.id,
            "name": c.name,
            "grade": c.grade,
            "level": c.level,
            "student_count": count,
            "teachers": [{"id": t.id, "name": t.name} for t in c.teachers],
        })
    return out


@router.get("/learning-progress")
def learning_progress_tab(
    classroom_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager")),
):
    """Tab5: 学習進捗 (映像視聴ログ・宿題提出率)"""
    if current_user.role == "room_manager" and not classroom_id:
        classroom_id = current_user.classroom_id
    return get_learning_progress(db, classroom_id)


@router.get("/attendance-trend")
def attendance_trend_tab(
    classroom_id: Optional[int] = Query(None),
    class_group_id: Optional[int] = Query(None),
    months: int = Query(6, ge=1, le=12),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager")),
):
    """Tab2: 月別出席率推移 (折れ線グラフ用、クラス別絞り込み可)"""
    if current_user.role == "room_manager" and not classroom_id:
        classroom_id = current_user.classroom_id
    return get_attendance_trend(db, classroom_id, months, class_group_id)


@router.get("/score-trend")
def score_trend_tab(
    classroom_id: Optional[int] = Query(None),
    class_group_id: Optional[int] = Query(None),
    test_type: Optional[str] = Query(None),
    months: int = Query(6, ge=1, le=24),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager")),
):
    """Tab2: 科目別平均スコア推移 (クラス別・試験種別切替可)"""
    if current_user.role == "room_manager" and not classroom_id:
        classroom_id = current_user.classroom_id
    return get_score_trend(db, classroom_id, months, class_group_id, test_type)


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


@router.get("/teachers")
def list_teachers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """講師一覧 (担当講師の追加候補)。admin/教室長/講師を対象。"""
    teachers = db.query(User).filter(
        User.role.in_(["admin", "room_manager", "teacher"])
    ).order_by(User.name).all()
    return [{"id": t.id, "name": t.name, "role": t.role} for t in teachers]


@router.get("/sales-progress")
def sales_progress_tab(
    period: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager")),
):
    """Tab3: 営業目標進捗"""
    return get_sales_progress(db, period)
