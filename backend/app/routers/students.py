"""
生徒ルーター
GET    /api/students         — 生徒一覧 (フィルタ・ページネーション付き)
POST   /api/students         — 生徒登録
GET    /api/students/{id}    — 生徒詳細 (全関連データ)
PATCH  /api/students/{id}    — 生徒情報更新
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.student import Student
from app.schemas.student import StudentCreate, StudentUpdate
from app.services.student_service import get_student_list, get_student_detail
from app.dependencies.auth import get_current_user, require_roles

router = APIRouter(prefix="/students", tags=["生徒"])


@router.get("")
def list_students(
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
    """
    生徒一覧を取得
    ロール別アクセス制御:
    - admin: 全教室
    - room_manager: 自教室のみ
    - teacher: 担当生徒のみ
    """
    # ロール別フィルタ
    if current_user.role == "room_manager" and not classroom_id:
        classroom_id = current_user.classroom_id
    elif current_user.role == "teacher":
        teacher_id = current_user.id
    elif current_user.role == "parttime":
        raise HTTPException(status_code=403, detail="アクセス権限がありません")

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


@router.post("", status_code=201)
def create_student(
    data: StudentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager")),
):
    """新規生徒登録"""
    student = Student(**data.model_dump())
    if current_user.role == "room_manager":
        student.classroom_id = current_user.classroom_id
    db.add(student)
    db.commit()
    db.refresh(student)
    return {"id": student.id, "name": student.name}


@router.get("/{student_id}")
def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """生徒詳細を全関連データと共に取得"""
    # ロール別アクセス制御
    if current_user.role == "teacher":
        student = db.query(Student).filter(Student.id == student_id).first()
        if student and student.assigned_teacher_id != current_user.id:
            raise HTTPException(status_code=403, detail="担当外の生徒です")
    elif current_user.role == "parttime":
        raise HTTPException(status_code=403, detail="アクセス権限がありません")

    detail = get_student_detail(student_id, db)
    if not detail:
        raise HTTPException(status_code=404, detail="生徒が見つかりません")
    return detail


@router.patch("/{student_id}")
def update_student(
    student_id: int,
    data: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager", "teacher")),
):
    """生徒情報を更新"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="生徒が見つかりません")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(student, field, value)

    db.commit()
    return {"message": "更新しました"}
