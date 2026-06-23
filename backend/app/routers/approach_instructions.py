"""
アプローチ指示ルーター
GET    /api/approach-instructions          — 一覧 (管理者/教室長/講師)
POST   /api/approach-instructions          — 作成 (管理者/教室長, PDF添付可)
DELETE /api/approach-instructions/{id}      — 削除 (管理者/教室長)
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.student import Student
from app.models.approach_instruction import ApproachInstruction
from app.dependencies.auth import get_current_user, require_roles

router = APIRouter(prefix="/approach-instructions", tags=["アプローチ指示"])


def instruction_matches_student(instr: ApproachInstruction, student: Student) -> bool:
    """指示が対象生徒に該当するか判定"""
    t, v = instr.target_type, instr.target_value
    if t == "全体":
        return True
    if t == "学年":
        return str(student.grade) == str(v)
    if t == "クラス":
        return bool(student.class_group and student.class_group.name == v)
    if t == "部門":
        divisions = {
            e.course.division for e in student.enrollments
            if e.course and e.course.division and not e.ended_at
        }
        return v in divisions
    return False


def serialize(instr: ApproachInstruction, include_pdf: bool = False) -> dict:
    out = {
        "id": instr.id,
        "title": instr.title,
        "content": instr.content,
        "target_type": instr.target_type,
        "target_value": instr.target_value,
        "period": instr.period,
        "has_pdf": bool(instr.pdf_data),
        "pdf_filename": instr.pdf_filename,
        "created_by_name": instr.creator.name if instr.creator else None,
        "created_at": instr.created_at,
    }
    if include_pdf:
        out["pdf_data"] = instr.pdf_data
    return out


@router.get("")
def list_instructions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """アプローチ指示の一覧 (新しい順)"""
    items = db.query(ApproachInstruction).order_by(ApproachInstruction.created_at.desc()).all()
    return [serialize(i) for i in items]


@router.get("/{instruction_id}/pdf")
def get_instruction_pdf(
    instruction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """添付PDF (base64 data URL) を取得"""
    instr = db.query(ApproachInstruction).filter(ApproachInstruction.id == instruction_id).first()
    if not instr or not instr.pdf_data:
        raise HTTPException(status_code=404, detail="PDFがありません")
    return {"pdf_data": instr.pdf_data, "pdf_filename": instr.pdf_filename}


class InstructionCreate(BaseModel):
    title: str
    content: str
    target_type: str = "全体"
    target_value: Optional[str] = None
    period: Optional[str] = None
    pdf_data: Optional[str] = None      # base64 data URL
    pdf_filename: Optional[str] = None


@router.post("", status_code=201)
def create_instruction(
    data: InstructionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager")),
):
    instr = ApproachInstruction(
        title=data.title,
        content=data.content,
        target_type=data.target_type,
        target_value=data.target_value,
        period=data.period,
        pdf_data=data.pdf_data,
        pdf_filename=data.pdf_filename,
        created_by=current_user.id,
    )
    db.add(instr)
    db.commit()
    db.refresh(instr)
    return serialize(instr)


@router.delete("/{instruction_id}")
def delete_instruction(
    instruction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager")),
):
    instr = db.query(ApproachInstruction).filter(ApproachInstruction.id == instruction_id).first()
    if not instr:
        raise HTTPException(status_code=404, detail="指示が見つかりません")
    db.delete(instr)
    db.commit()
    return {"message": "削除しました"}
