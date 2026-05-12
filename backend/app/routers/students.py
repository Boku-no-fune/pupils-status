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
    school_type: Optional[str] = Query(None),
    division: Optional[str] = Query(None),
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
        school_type=school_type,
        division=division,
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


# ===== 写真 =====

from pydantic import BaseModel as PydanticBase

class PhotoPayload(PydanticBase):
    photo_data: Optional[str] = None  # base64文字列


@router.put("/{student_id}/photo")
def upload_photo(
    student_id: int,
    payload: PhotoPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager", "teacher")),
):
    """顔写真をBase64で保存"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="生徒が見つかりません")
    student.photo_data = payload.photo_data
    db.commit()
    return {"message": "写真を保存しました"}


# ===== スタッフ記録 =====

from datetime import datetime
from app.models.staff_note import StaffNote

class StaffNoteCreate(PydanticBase):
    note_type: str
    content: str
    occurred_at: datetime


@router.get("/{student_id}/staff-notes")
def list_staff_notes(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """スタッフ記録一覧"""
    notes = db.query(StaffNote).filter(
        StaffNote.student_id == student_id
    ).order_by(StaffNote.occurred_at.desc()).all()
    return [
        {
            "id": n.id,
            "note_type": n.note_type,
            "content": n.content,
            "occurred_at": n.occurred_at,
            "teacher_id": n.teacher_id,
            "teacher_name": n.teacher.name if n.teacher else None,
        }
        for n in notes
    ]


@router.post("/{student_id}/staff-notes", status_code=201)
def create_staff_note(
    student_id: int,
    data: StaffNoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager", "teacher")),
):
    """スタッフ記録を追加"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="生徒が見つかりません")

    note = StaffNote(
        student_id=student_id,
        teacher_id=current_user.id,
        note_type=data.note_type,
        content=data.content,
        occurred_at=data.occurred_at,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return {"id": note.id, "message": "記録しました"}


@router.delete("/{student_id}/staff-notes/{note_id}")
def delete_staff_note(
    student_id: int,
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager", "teacher")),
):
    """スタッフ記録を削除"""
    note = db.query(StaffNote).filter(
        StaffNote.id == note_id,
        StaffNote.student_id == student_id,
    ).first()
    if not note:
        raise HTTPException(status_code=404, detail="記録が見つかりません")
    db.delete(note)
    db.commit()
    return {"message": "削除しました"}


# ===== 映像授業ログ =====

from app.models.video_lesson_log import VideoLessonLog
import csv
import io

class VideoLogCreate(PydanticBase):
    lesson_name: str
    lesson_category: Optional[str] = None
    viewed_at: datetime
    duration_minutes: float
    completion_rate: Optional[float] = None
    source_system: Optional[str] = None


@router.get("/{student_id}/video-logs")
def list_video_logs(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """映像授業視聴ログ一覧"""
    logs = db.query(VideoLessonLog).filter(
        VideoLessonLog.student_id == student_id
    ).order_by(VideoLessonLog.viewed_at.desc()).limit(200).all()
    return [
        {
            "id": lg.id,
            "lesson_name": lg.lesson_name,
            "lesson_category": lg.lesson_category,
            "viewed_at": lg.viewed_at,
            "duration_minutes": lg.duration_minutes,
            "completion_rate": lg.completion_rate,
            "source_system": lg.source_system,
        }
        for lg in logs
    ]


@router.post("/{student_id}/video-logs", status_code=201)
def create_video_log(
    student_id: int,
    data: VideoLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager")),
):
    """映像授業ログを1件追加"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="生徒が見つかりません")

    log = VideoLessonLog(student_id=student_id, **data.model_dump())
    db.add(log)
    db.commit()
    return {"message": "追加しました"}
