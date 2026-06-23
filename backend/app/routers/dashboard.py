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
from app.services.activity_service import get_activity_matrix
from app.dependencies.auth import get_current_user, require_roles
from app.models.class_group import ClassGroup
from app.models.student import Student

router = APIRouter(prefix="/dashboard", tags=["ダッシュボード"])


def teacher_student_ids(db: Session, user: User):
    """講師の担当生徒ID一覧 (複数担当 student_teachers + 代表担当)。講師以外はNone。"""
    from app.models.class_group import student_teachers
    ids = {r[0] for r in db.query(student_teachers.c.student_id).filter(student_teachers.c.user_id == user.id).all()}
    ids |= {r[0] for r in db.query(Student.id).filter(Student.assigned_teacher_id == user.id).all()}
    return list(ids)


def effective_student_ids(db: Session, user: User, show_all: bool):
    """講師かつ show_all でない場合のみ担当生徒IDで絞り込む。それ以外は None (絞り込みなし)。"""
    if user.role == "teacher" and not show_all:
        return teacher_student_ids(db, user)
    return None


@router.get("/stats")
def dashboard_stats(
    classroom_id: Optional[int] = Query(None),
    show_all: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager", "teacher")),
):
    """ダッシュボード上部サマリーカード。講師は既定で担当生徒のみ集計。"""
    if current_user.role == "room_manager" and not classroom_id:
        classroom_id = current_user.classroom_id
    sids = effective_student_ids(db, current_user, show_all)
    return get_dashboard_stats(db, classroom_id, sids)


@router.get("/student-list")
def student_list_tab(
    status: Optional[str] = Query(None),
    grade: Optional[int] = Query(None),
    class_group_id: Optional[int] = Query(None),
    teacher_id: Optional[int] = Query(None),
    classroom_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    school_type: Optional[str] = Query(None),
    division: Optional[str] = Query(None),
    sort_by: str = Query("grade"),
    sort_dir: str = Query("asc"),
    show_all: bool = Query(False),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Tab1: 生徒一覧 (会員番号・クラス・出席率・成績変化付き)。講師は既定で担当生徒のみ。"""
    if current_user.role == "room_manager" and not classroom_id:
        classroom_id = current_user.classroom_id
    elif current_user.role == "teacher" and not show_all:
        teacher_id = current_user.id

    return get_student_list(
        db=db,
        status=status,
        grade=grade,
        class_group_id=class_group_id,
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
    show_all: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager", "teacher")),
):
    """上部サマリーカードのドリルダウン (クリックで該当生徒をポップアップ表示)"""
    if current_user.role == "room_manager" and not classroom_id:
        classroom_id = current_user.classroom_id
    result = get_stat_students(db, kind, classroom_id)
    sids = effective_student_ids(db, current_user, show_all)
    if sids is not None:
        sset = set(sids)
        result = [r for r in result if r.get("id") in sset]
    return result


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
    show_all: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager", "teacher")),
):
    """Tab5: 学習進捗 (映像視聴ログ・宿題提出率)。講師は既定で担当生徒のみ。"""
    if current_user.role == "room_manager" and not classroom_id:
        classroom_id = current_user.classroom_id
    sids = effective_student_ids(db, current_user, show_all)
    return get_learning_progress(db, classroom_id, sids)


@router.get("/attendance-trend")
def attendance_trend_tab(
    classroom_id: Optional[int] = Query(None),
    class_group_id: Optional[int] = Query(None),
    months: int = Query(6, ge=1, le=12),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager", "teacher")),
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
    current_user: User = Depends(require_roles("admin", "room_manager", "teacher")),
):
    """Tab2: 科目別平均スコア推移 (クラス別・試験種別切替可)"""
    if current_user.role == "room_manager" and not classroom_id:
        classroom_id = current_user.classroom_id
    return get_score_trend(db, classroom_id, months, class_group_id, test_type)


@router.get("/risk-students")
def risk_students_tab(
    classroom_id: Optional[int] = Query(None),
    show_all: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager", "teacher")),
):
    """Tab4: リスク生徒一覧 (高→中→低順)。講師は既定で担当生徒のみ。"""
    if current_user.role == "room_manager" and not classroom_id:
        classroom_id = current_user.classroom_id
    result = get_all_risk_students(db, classroom_id)
    sids = effective_student_ids(db, current_user, show_all)
    if sids is not None:
        sset = set(sids)
        result = [r for r in result if r.get("student_id") in sset]
    return result


@router.get("/activity-matrix")
def activity_matrix(
    months: int = Query(6, ge=1, le=12),
    classroom_id: Optional[int] = Query(None),
    show_all: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager", "teacher")),
):
    """スタッフ記録・保護者アプローチの月別実施状況 (生徒×月のマトリクス)。講師は既定で担当生徒のみ。"""
    if current_user.role == "room_manager" and not classroom_id:
        classroom_id = current_user.classroom_id
    sids = effective_student_ids(db, current_user, show_all)
    return get_activity_matrix(db, months, classroom_id, sids)


@router.get("/map-data")
def map_data(
    show_all: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager", "teacher")),
):
    """通塾元(生徒の自宅)・通学校の座標 (地図プロット用)。講師は既定で担当生徒のみ。"""
    q = db.query(Student).filter(
        Student.status.in_(["enrolled", "trial", "on_leave"]),
        Student.home_lat.isnot(None),
    )
    sids = effective_student_ids(db, current_user, show_all)
    if sids is not None:
        q = q.filter(Student.id.in_(sids))
    students = q.all()

    student_points = [
        {
            "id": s.id,
            "name": s.name,
            "grade": s.grade,
            "school": s.school,
            "address": s.address,
            "home_lat": s.home_lat,
            "home_lng": s.home_lng,
            "school_lat": s.school_lat,
            "school_lng": s.school_lng,
            "class_label": s.class_group.name if s.class_group else None,
        }
        for s in students
    ]

    # 学校は重複排除して集計 (通学者数付き)
    schools: dict = {}
    for s in students:
        if s.school and s.school_lat is not None:
            if s.school not in schools:
                schools[s.school] = {"name": s.school, "lat": s.school_lat, "lng": s.school_lng, "count": 0}
            schools[s.school]["count"] += 1

    return {
        "classroom": {"name": "学習塾サンプル校", "lat": 35.6618, "lng": 139.7041},
        "students": student_points,
        "schools": list(schools.values()),
    }


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
    current_user: User = Depends(require_roles("admin", "room_manager", "teacher")),
):
    """Tab3: 営業目標進捗"""
    return get_sales_progress(db, period)
