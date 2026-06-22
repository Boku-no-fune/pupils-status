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
    sort_by: str = Query("grade"),
    sort_dir: str = Query("asc"),
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
        sort_by=sort_by,
        sort_dir=sort_dir,
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
        if student:
            teacher_ids = {t.id for t in student.teachers}
            if student.assigned_teacher_id != current_user.id and current_user.id not in teacher_ids:
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
from typing import List
from app.models.staff_note import StaffNote

class StaffNoteCreate(PydanticBase):
    note_type: str
    content: str
    tags: Optional[List[str]] = None
    occurred_at: datetime


@router.get("/{student_id}/activities")
def list_activities(
    student_id: int,
    month: str = Query(..., description="YYYY-MM"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """指定月のスタッフ記録+保護者アプローチ明細 (月別実施状況のポップアップ用)"""
    from app.services.activity_service import get_student_activities
    return get_student_activities(db, student_id, month)


@router.get("/{student_id}/staff-notes")
def list_staff_notes(
    student_id: int,
    tag: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """スタッフ記録一覧 (タグ・キーワード検索対応)"""
    notes = db.query(StaffNote).filter(
        StaffNote.student_id == student_id
    ).order_by(StaffNote.occurred_at.desc()).all()

    def matches(n):
        if tag and tag not in (n.tags or []):
            return False
        if search:
            kw = search.lower()
            hay = f"{n.content} {n.note_type} {' '.join(n.tags or [])}".lower()
            if kw not in hay:
                return False
        return True

    return [
        {
            "id": n.id,
            "note_type": n.note_type,
            "content": n.content,
            "tags": n.tags or [],
            "occurred_at": n.occurred_at,
            "teacher_id": n.teacher_id,
            "teacher_name": n.teacher.name if n.teacher else None,
        }
        for n in notes if matches(n)
    ]


@router.post("/{student_id}/staff-notes", status_code=201)
def create_staff_note(
    student_id: int,
    data: StaffNoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager", "teacher")),
):
    """スタッフ記録を追加 (本文中の #タグ を自動抽出してtagsに統合)"""
    import re
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="生徒が見つかりません")

    # 本文からハッシュタグを抽出し、明示tagsとマージ
    extracted = re.findall(r"#[^\s#　]+", data.content)
    tags = list(dict.fromkeys((data.tags or []) + extracted))

    note = StaffNote(
        student_id=student_id,
        teacher_id=current_user.id,
        note_type=data.note_type,
        content=data.content,
        tags=tags or None,
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


# ===========================================================================
# 詳細ページ追加項目の CRUD
# ===========================================================================

from datetime import date as _date
from app.models.student_extras import (
    StudentPhone, SpecialNote, ProfileMemo, ParentRequest, ExamCertification,
)
from app.models.test_score import TestScore
from app.models.class_group import student_teachers as _student_teachers


def _get_student_or_404(student_id: int, db: Session) -> Student:
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="生徒が見つかりません")
    return student


# ----- 特記事項 -----
class SpecialNoteCreate(PydanticBase):
    content: str
    importance: str = "中"


@router.post("/{student_id}/special-notes", status_code=201)
def create_special_note(
    student_id: int, data: SpecialNoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager", "teacher")),
):
    _get_student_or_404(student_id, db)
    note = SpecialNote(student_id=student_id, content=data.content, importance=data.importance)
    db.add(note)
    db.commit()
    db.refresh(note)
    return {"id": note.id, "content": note.content, "importance": note.importance, "created_at": note.created_at}


@router.delete("/{student_id}/special-notes/{note_id}")
def delete_special_note(
    student_id: int, note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager", "teacher")),
):
    note = db.query(SpecialNote).filter(
        SpecialNote.id == note_id, SpecialNote.student_id == student_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="記録が見つかりません")
    db.delete(note)
    db.commit()
    return {"message": "削除しました"}


# ----- プロフィール定型メモ -----
class ProfileMemoCreate(PydanticBase):
    category: str
    content: str


@router.post("/{student_id}/profile-memos", status_code=201)
def create_profile_memo(
    student_id: int, data: ProfileMemoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager", "teacher")),
):
    _get_student_or_404(student_id, db)
    memo = ProfileMemo(student_id=student_id, category=data.category, content=data.content)
    db.add(memo)
    db.commit()
    db.refresh(memo)
    return {"id": memo.id, "category": memo.category, "content": memo.content, "created_at": memo.created_at}


@router.delete("/{student_id}/profile-memos/{memo_id}")
def delete_profile_memo(
    student_id: int, memo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager", "teacher")),
):
    memo = db.query(ProfileMemo).filter(
        ProfileMemo.id == memo_id, ProfileMemo.student_id == student_id).first()
    if not memo:
        raise HTTPException(status_code=404, detail="メモが見つかりません")
    db.delete(memo)
    db.commit()
    return {"message": "削除しました"}


# ----- 保護者要望・クレーム -----
class ParentRequestCreate(PydanticBase):
    request_type: str = "要望"
    content: str
    status: str = "対応中"
    occurred_at: Optional[datetime] = None


class ParentRequestUpdate(PydanticBase):
    status: str


@router.post("/{student_id}/parent-requests", status_code=201)
def create_parent_request(
    student_id: int, data: ParentRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager", "teacher")),
):
    _get_student_or_404(student_id, db)
    req = ParentRequest(
        student_id=student_id,
        request_type=data.request_type,
        content=data.content,
        status=data.status,
        occurred_at=data.occurred_at or datetime.now(),
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return {"id": req.id, "request_type": req.request_type, "content": req.content,
            "status": req.status, "occurred_at": req.occurred_at}


@router.patch("/{student_id}/parent-requests/{req_id}")
def update_parent_request(
    student_id: int, req_id: int, data: ParentRequestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager", "teacher")),
):
    req = db.query(ParentRequest).filter(
        ParentRequest.id == req_id, ParentRequest.student_id == student_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="記録が見つかりません")
    req.status = data.status
    db.commit()
    return {"message": "更新しました"}


@router.delete("/{student_id}/parent-requests/{req_id}")
def delete_parent_request(
    student_id: int, req_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager", "teacher")),
):
    req = db.query(ParentRequest).filter(
        ParentRequest.id == req_id, ParentRequest.student_id == student_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="記録が見つかりません")
    db.delete(req)
    db.commit()
    return {"message": "削除しました"}


# ----- 電話番号メモ (番号は連携・メモは手入力) -----
class PhoneCreate(PydanticBase):
    phone_number: str
    memo: Optional[str] = None


class PhoneMemoUpdate(PydanticBase):
    memo: Optional[str] = None


@router.post("/{student_id}/phones", status_code=201)
def create_phone(
    student_id: int, data: PhoneCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager", "teacher")),
):
    _get_student_or_404(student_id, db)
    count = db.query(StudentPhone).filter(StudentPhone.student_id == student_id).count()
    if count >= 3:
        raise HTTPException(status_code=400, detail="電話番号は3件までです")
    phone = StudentPhone(student_id=student_id, phone_number=data.phone_number,
                         memo=data.memo, position=count)
    db.add(phone)
    db.commit()
    db.refresh(phone)
    return {"id": phone.id, "phone_number": phone.phone_number, "memo": phone.memo, "position": phone.position}


@router.patch("/{student_id}/phones/{phone_id}")
def update_phone_memo(
    student_id: int, phone_id: int, data: PhoneMemoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager", "teacher")),
):
    phone = db.query(StudentPhone).filter(
        StudentPhone.id == phone_id, StudentPhone.student_id == student_id).first()
    if not phone:
        raise HTTPException(status_code=404, detail="電話番号が見つかりません")
    phone.memo = data.memo
    db.commit()
    return {"message": "更新しました"}


@router.delete("/{student_id}/phones/{phone_id}")
def delete_phone(
    student_id: int, phone_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager", "teacher")),
):
    phone = db.query(StudentPhone).filter(
        StudentPhone.id == phone_id, StudentPhone.student_id == student_id).first()
    if not phone:
        raise HTTPException(status_code=404, detail="電話番号が見つかりません")
    db.delete(phone)
    db.commit()
    return {"message": "削除しました"}


# ----- 試験成績の手入力 (他タブにも反映される) -----
class TestScoreCreate(PydanticBase):
    test_id: str
    test_name: Optional[str] = None
    test_type: Optional[str] = "その他"
    subject: str
    raw_score: float
    rank: Optional[int] = None
    deviation_value: Optional[float] = None
    test_date: Optional[_date] = None


@router.post("/{student_id}/test-scores", status_code=201)
def create_test_score(
    student_id: int, data: TestScoreCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager", "teacher")),
):
    _get_student_or_404(student_id, db)
    ts = TestScore(student_id=student_id, **data.model_dump())
    db.add(ts)
    db.commit()
    db.refresh(ts)
    return {"id": ts.id, "message": "成績を登録しました"}


@router.delete("/{student_id}/test-scores/{score_id}")
def delete_test_score(
    student_id: int, score_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager", "teacher")),
):
    ts = db.query(TestScore).filter(
        TestScore.id == score_id, TestScore.student_id == student_id).first()
    if not ts:
        raise HTTPException(status_code=404, detail="成績が見つかりません")
    db.delete(ts)
    db.commit()
    return {"message": "削除しました"}


# ----- 英検・漢検 -----
class ExamCertCreate(PydanticBase):
    exam_type: str
    level: str
    score: Optional[int] = None
    result: str = "合格"
    exam_date: Optional[_date] = None


@router.post("/{student_id}/exam-certs", status_code=201)
def create_exam_cert(
    student_id: int, data: ExamCertCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager", "teacher")),
):
    _get_student_or_404(student_id, db)
    cert = ExamCertification(student_id=student_id, **data.model_dump())
    db.add(cert)
    db.commit()
    db.refresh(cert)
    return {"id": cert.id, "message": "登録しました"}


@router.delete("/{student_id}/exam-certs/{cert_id}")
def delete_exam_cert(
    student_id: int, cert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager", "teacher")),
):
    cert = db.query(ExamCertification).filter(
        ExamCertification.id == cert_id, ExamCertification.student_id == student_id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="記録が見つかりません")
    db.delete(cert)
    db.commit()
    return {"message": "削除しました"}


# ----- 担当講師の追加・削除 (複数担当) -----
class TeacherAssign(PydanticBase):
    user_id: int


@router.post("/{student_id}/teachers", status_code=201)
def add_teacher(
    student_id: int, data: TeacherAssign,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager")),
):
    student = _get_student_or_404(student_id, db)
    teacher = db.query(User).filter(User.id == data.user_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="講師が見つかりません")
    if teacher not in student.teachers:
        student.teachers.append(teacher)
        # 代表担当が未設定なら設定
        if not student.assigned_teacher_id:
            student.assigned_teacher_id = teacher.id
        db.commit()
    return {"message": "担当講師を追加しました",
            "teachers": [{"id": t.id, "name": t.name} for t in student.teachers]}


@router.delete("/{student_id}/teachers/{user_id}")
def remove_teacher(
    student_id: int, user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager")),
):
    student = _get_student_or_404(student_id, db)
    teacher = db.query(User).filter(User.id == user_id).first()
    if teacher and teacher in student.teachers:
        student.teachers.remove(teacher)
        if student.assigned_teacher_id == user_id:
            student.assigned_teacher_id = student.teachers[0].id if student.teachers else None
        db.commit()
    return {"message": "担当講師を外しました",
            "teachers": [{"id": t.id, "name": t.name} for t in student.teachers]}
