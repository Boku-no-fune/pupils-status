"""
出欠ルーター
GET  /api/attendances  — 出欠一覧
POST /api/attendances  — 出欠登録
"""

from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.attendance import Attendance
from app.schemas.sales import AttendanceCreate
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/attendances", tags=["出欠"])


@router.get("")
def list_attendances(
    student_id: Optional[int] = Query(None),
    from_date: Optional[date] = Query(None, alias="from"),
    to_date: Optional[date] = Query(None, alias="to"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """出欠一覧を取得"""
    query = db.query(Attendance)
    if student_id:
        query = query.filter(Attendance.student_id == student_id)
    if from_date:
        query = query.filter(Attendance.class_date >= from_date)
    if to_date:
        query = query.filter(Attendance.class_date <= to_date)

    records = query.order_by(Attendance.class_date.desc()).all()
    return [
        {
            "id": r.id,
            "student_id": r.student_id,
            "class_date": r.class_date,
            "status": r.status,
            "note": r.note,
        }
        for r in records
    ]


@router.post("", status_code=201)
def create_attendance(
    data: AttendanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """出欠を登録 (全ロール可)"""
    record = Attendance(
        student_id=data.student_id,
        class_date=date.fromisoformat(data.class_date),
        status=data.status,
        note=data.note,
    )
    db.add(record)
    db.commit()
    return {"id": record.id}
