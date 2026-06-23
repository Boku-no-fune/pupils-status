"""
未入会(見込み)生徒ルーター
GET    /api/prospects                          — 一覧 (ステージ状況付き)
POST   /api/prospects/{id}/stages              — ステージの状況・メモを更新(upsert)
GET    /api/prospects/funnel                   — ファネル集計 (営業タブ連携用)
"""

from typing import Optional, List
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.prospect import Prospect, ProspectStage
from app.models.staff_note import StaffNote
from app.dependencies.auth import get_current_user, require_roles

router = APIRouter(prefix="/prospects", tags=["未入会生徒"])

STAGES = ["問い合わせ", "資料請求", "入会テスト", "体験授業", "イベント参加", "季節講習受講"]


def _serialize(p: Prospect) -> dict:
    stage_map = {s.stage: s for s in p.stages}
    return {
        "id": p.id,
        "name": p.name,
        "grade": p.grade,
        "school": p.school,
        "source": p.source,
        "status": p.status,
        "assigned_teacher_name": p.assigned_teacher.name if p.assigned_teacher else None,
        "first_contact_at": p.first_contact_at,
        "stages": [
            {
                "stage": stage,
                "id": stage_map[stage].id if stage in stage_map else None,
                "status": stage_map[stage].status if stage in stage_map else "未対応",
                "memo": stage_map[stage].memo if stage in stage_map else None,
                "occurred_at": stage_map[stage].occurred_at if stage in stage_map else None,
            }
            for stage in STAGES
        ],
    }


@router.get("/funnel")
def prospect_funnel(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager")),
):
    """ステージ別のファネル集計 (営業目標・アプローチタブ連携用)"""
    prospects = db.query(Prospect).filter(Prospect.status == "active").all()
    result = []
    for stage in STAGES:
        counts = {"未対応": 0, "対応中": 0, "完了": 0}
        for p in prospects:
            st = next((s for s in p.stages if s.stage == stage), None)
            status = st.status if st else "未対応"
            counts[status] = counts.get(status, 0) + 1
        result.append({"stage": stage, **counts, "total": len(prospects)})
    return {"total_prospects": len(prospects), "stages": result}


@router.get("")
def list_prospects(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager")),
):
    """未入会生徒の一覧 (各ステージの状況付き)"""
    prospects = db.query(Prospect).order_by(Prospect.first_contact_at.desc()).all()
    return [_serialize(p) for p in prospects]


@router.get("/{prospect_id}")
def get_prospect(
    prospect_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager", "teacher")),
):
    """未入会生徒の詳細 (ステージ + スタッフ記録)。入会時にこの記録が引き継がれる想定。"""
    p = db.query(Prospect).filter(Prospect.id == prospect_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="見込み客が見つかりません")
    data = _serialize(p)
    data["address"] = p.address
    data["note"] = p.note
    data["staff_notes"] = [
        {
            "id": n.id, "note_type": n.note_type, "content": n.content,
            "tags": n.tags or [], "occurred_at": n.occurred_at,
            "teacher_name": n.teacher.name if n.teacher else None,
        }
        for n in p.staff_notes
    ]
    return data


class ProspectNoteCreate(BaseModel):
    note_type: str = "その他"
    content: str
    occurred_at: Optional[datetime] = None


@router.post("/{prospect_id}/staff-notes", status_code=201)
def create_prospect_note(
    prospect_id: int,
    data: ProspectNoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager", "teacher")),
):
    import re
    p = db.query(Prospect).filter(Prospect.id == prospect_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="見込み客が見つかりません")
    tags = re.findall(r"#[^\s#　]+", data.content) or None
    note = StaffNote(
        prospect_id=prospect_id, teacher_id=current_user.id,
        note_type=data.note_type, content=data.content, tags=tags,
        occurred_at=data.occurred_at or datetime.now(),
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return {"id": note.id, "message": "記録しました"}


@router.delete("/{prospect_id}/staff-notes/{note_id}")
def delete_prospect_note(
    prospect_id: int, note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager", "teacher")),
):
    note = db.query(StaffNote).filter(
        StaffNote.id == note_id, StaffNote.prospect_id == prospect_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="記録が見つかりません")
    db.delete(note)
    db.commit()
    return {"message": "削除しました"}


class StageUpsert(BaseModel):
    stage: str
    status: str
    memo: Optional[str] = None


@router.post("/{prospect_id}/stages")
def upsert_stage(
    prospect_id: int,
    data: StageUpsert,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager", "teacher")),
):
    """ステージの状況・メモを更新 (なければ作成)"""
    if data.stage not in STAGES:
        raise HTTPException(status_code=400, detail="不正なステージです")
    prospect = db.query(Prospect).filter(Prospect.id == prospect_id).first()
    if not prospect:
        raise HTTPException(status_code=404, detail="見込み客が見つかりません")

    stage = db.query(ProspectStage).filter(
        ProspectStage.prospect_id == prospect_id,
        ProspectStage.stage == data.stage,
    ).first()
    if stage:
        stage.status = data.status
        stage.memo = data.memo
        if data.status != "未対応" and not stage.occurred_at:
            stage.occurred_at = date.today()
    else:
        stage = ProspectStage(
            prospect_id=prospect_id,
            stage=data.stage,
            status=data.status,
            memo=data.memo,
            sort_order=STAGES.index(data.stage),
            occurred_at=date.today() if data.status != "未対応" else None,
        )
        db.add(stage)
    db.commit()
    return {"message": "更新しました"}
