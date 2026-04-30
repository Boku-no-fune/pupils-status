"""
保護者コンタクト・テストスコア・支払いルーター
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.contact import ParentContact
from app.models.test_score import TestScore
from app.models.payment import Payment
from app.schemas.sales import ParentContactCreate
from app.dependencies.auth import get_current_user, require_roles

# 保護者コンタクト
contact_router = APIRouter(prefix="/contacts", tags=["保護者コンタクト"])


@contact_router.get("")
def list_contacts(
    student_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """保護者コンタクト一覧"""
    query = db.query(ParentContact)
    if student_id:
        query = query.filter(ParentContact.student_id == student_id)
    records = query.order_by(ParentContact.occurred_at.desc()).all()
    return [
        {
            "id": r.id,
            "student_id": r.student_id,
            "contact_type": r.contact_type,
            "occurred_at": r.occurred_at,
            "summary": r.summary,
            "teacher_id": r.teacher_id,
            "teacher_name": r.teacher.name if r.teacher else None,
        }
        for r in records
    ]


@contact_router.post("", status_code=201)
def create_contact(
    data: ParentContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager", "teacher")),
):
    """保護者コンタクトを記録"""
    record = ParentContact(
        student_id=data.student_id,
        contact_type=data.contact_type,
        occurred_at=data.occurred_at,
        summary=data.summary,
        teacher_id=data.teacher_id or current_user.id,
    )
    db.add(record)
    db.commit()
    return {"id": record.id}


# テストスコア
score_router = APIRouter(prefix="/test-scores", tags=["テストスコア"])


@score_router.get("")
def list_scores(
    student_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """テストスコア一覧"""
    query = db.query(TestScore)
    if student_id:
        query = query.filter(TestScore.student_id == student_id)
    records = query.order_by(TestScore.test_date.desc(), TestScore.test_id).all()
    return [
        {
            "id": r.id,
            "student_id": r.student_id,
            "test_id": r.test_id,
            "test_name": r.test_name,
            "subject": r.subject,
            "raw_score": r.raw_score,
            "rank": r.rank,
            "deviation_value": r.deviation_value,
            "test_date": r.test_date,
        }
        for r in records
    ]


# 支払い
payment_router = APIRouter(prefix="/payments", tags=["支払い"])


@payment_router.get("")
def list_payments(
    student_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager")),
):
    """支払い一覧"""
    query = db.query(Payment)
    if student_id:
        query = query.filter(Payment.student_id == student_id)
    records = query.order_by(Payment.paid_at.desc()).all()
    return [
        {
            "id": r.id,
            "student_id": r.student_id,
            "amount": r.amount,
            "paid_at": r.paid_at,
            "due_at": r.due_at,
            "category": r.category,
            "status": r.status,
        }
        for r in records
    ]
