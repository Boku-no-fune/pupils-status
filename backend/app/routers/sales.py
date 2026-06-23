"""
営業ルーター
GET    /api/sales/actions     — 営業アクション一覧
POST   /api/sales/actions     — 営業アクション登録
PATCH  /api/sales/actions/{id} — 営業アクション更新
GET    /api/sales/goals       — 営業目標一覧
POST   /api/sales/goals       — 営業目標登録
GET    /api/sales/progress    — 目標進捗
GET    /api/sales/report      — 期別サマリーレポート
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.sales import SalesAction, SalesGoal
from app.schemas.sales import SalesActionCreate, SalesActionUpdate, SalesGoalCreate
from app.services.dashboard_service import get_sales_progress
from app.dependencies.auth import get_current_user, require_roles

router = APIRouter(prefix="/sales", tags=["営業"])


@router.get("/actions")
def list_sales_actions(
    student_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    assigned_to: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager")),
):
    """営業アクション一覧"""
    query = db.query(SalesAction)
    if student_id:
        query = query.filter(SalesAction.student_id == student_id)
    if status:
        query = query.filter(SalesAction.status == status)
    if assigned_to:
        query = query.filter(SalesAction.assigned_to == assigned_to)

    # room_managerは自教室の生徒のみ
    if current_user.role == "room_manager":
        from app.models.student import Student
        student_ids = [
            r[0] for r in db.query(Student.id).filter(
                Student.classroom_id == current_user.classroom_id
            ).all()
        ]
        query = query.filter(SalesAction.student_id.in_(student_ids))

    records = query.order_by(SalesAction.actioned_at.desc()).all()
    return [
        {
            "id": r.id,
            "student_id": r.student_id,
            "student_name": r.student.name if r.student else None,
            "action_type": r.action_type,
            "target_product": r.target_product,
            "status": r.status,
            "note": r.note,
            "actioned_at": r.actioned_at,
            "assigned_to": r.assigned_to,
            "assigned_teacher_name": r.assigned_teacher.name if r.assigned_teacher else None,
        }
        for r in records
    ]


@router.get("/campaign-rows")
def campaign_rows(
    product: str = Query(...),
    show_all: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager", "teacher")),
):
    """
    指定キャンペーン(product)のアプローチ状況一覧。
    在籍生は「正会員」、それ以外は通常のアクションを表示。クリックで生徒ページへ。
    講師は既定で担当生徒のみ (show_all=trueで全件)。
    """
    from app.models.student import Student
    from app.models.class_group import student_teachers

    q = db.query(SalesAction).filter(SalesAction.target_product == product)

    if current_user.role == "room_manager":
        sids = [r[0] for r in db.query(Student.id).filter(Student.classroom_id == current_user.classroom_id).all()]
        q = q.filter(SalesAction.student_id.in_(sids))
    elif current_user.role == "teacher" and not show_all:
        st_sub = db.query(student_teachers.c.student_id).filter(student_teachers.c.user_id == current_user.id).subquery()
        q = q.filter(
            (SalesAction.student_id.in_(st_sub)) |
            (SalesAction.student_id.in_(db.query(Student.id).filter(Student.assigned_teacher_id == current_user.id)))
        )

    records = q.all()
    rows = []
    for r in records:
        s = r.student
        is_member = s and s.status == "enrolled"
        rows.append({
            "id": r.id,
            "student_id": r.student_id,
            "student_name": s.name if s else None,
            "grade": s.grade if s else None,
            "class_label": (s.class_group.name if s and s.class_group else None),
            "status": r.status,
            "action_type": r.action_type,
            "is_member": bool(is_member),
            "note": r.note,
            "actioned_at": r.actioned_at,
            "assigned_teacher_name": r.assigned_teacher.name if r.assigned_teacher else None,
        })
    # 正会員→申込済→交渉中→… の順で並べる
    order = {"signed_up": 0, "in_progress": 1, "pending": 2, "declined": 3}
    rows.sort(key=lambda x: (0 if x["is_member"] else 1, order.get(x["status"], 9)))
    return rows


@router.post("/actions", status_code=201)
def create_sales_action(
    data: SalesActionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager")),
):
    """営業アクションを登録"""
    action = SalesAction(**data.model_dump())
    if not action.assigned_to:
        action.assigned_to = current_user.id
    db.add(action)
    db.commit()
    return {"id": action.id}


@router.patch("/actions/{action_id}")
def update_sales_action(
    action_id: int,
    data: SalesActionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager")),
):
    """営業アクションのステータスを更新"""
    action = db.query(SalesAction).filter(SalesAction.id == action_id).first()
    if not action:
        raise HTTPException(status_code=404, detail="アクションが見つかりません")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(action, field, value)

    db.commit()
    return {"message": "更新しました"}


@router.get("/goals")
def list_goals(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager")),
):
    """営業目標一覧"""
    goals = db.query(SalesGoal).order_by(SalesGoal.created_at.desc()).all()
    return [
        {
            "id": g.id,
            "goal_type": g.goal_type,
            "target_product": g.target_product,
            "target_count": g.target_count,
            "period": g.period,
            "created_at": g.created_at,
        }
        for g in goals
    ]


@router.post("/goals", status_code=201)
def create_goal(
    data: SalesGoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager")),
):
    """営業目標を登録"""
    goal = SalesGoal(**data.model_dump(), created_by=current_user.id)
    db.add(goal)
    db.commit()
    return {"id": goal.id}


@router.get("/progress")
def get_progress(
    period: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager", "teacher")),
):
    """営業目標の達成進捗 (全キャンペーン)"""
    return get_sales_progress(db, period)


@router.get("/report")
def get_report(
    period: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager")),
):
    """上司報告用サマリーレポートを生成"""
    progress_list = get_sales_progress(db, period)

    if not progress_list:
        return {"message": "該当する目標データがありません"}

    p = progress_list[0]
    report_text = (
        f"■ {p['target_product'] or p['goal_type']} 営業報告 ({p['period']})\n\n"
        f"目標: {p['target_count']} 名\n"
        f"申込済: {p['signed_up']} 名 ({p['progress_pct']:.0f}%)\n"
        f"交渉中: {p['in_progress']} 名\n"
        f"辞退: {p['declined']} 名\n"
        f"未着手: {p['not_started']} 名\n\n"
        f"達成率 {p['progress_pct']:.0f}% です。"
        f"{'引き続きアプローチを強化します。' if p['progress_pct'] < 80 else '目標達成に向け順調です。'}"
    )

    return {
        "period": p["period"],
        "report_text": report_text,
        "data": p,
    }
