"""
スタッフ記録・保護者アプローチの月別実施状況サービス
StaffNote(スタッフ記録) と ParentContact(保護者コンタクト/アプローチ) を月別に集計する。
"""

from typing import Optional, List, Dict
from datetime import date, datetime
from collections import defaultdict
from sqlalchemy.orm import Session

from app.models.student import Student
from app.models.staff_note import StaffNote
from app.models.contact import ParentContact


def _month_keys(months: int) -> List[str]:
    today = date.today()
    keys = []
    for m in range(months - 1, -1, -1):
        y, mo = today.year, today.month - m
        while mo <= 0:
            mo += 12
            y -= 1
        keys.append(f"{y}-{mo:02d}")
    return keys


def get_activity_matrix(db: Session, months: int = 6, classroom_id: Optional[int] = None,
                        student_ids: Optional[list] = None) -> Dict:
    """
    生徒 × 月 の実施回数マトリクス。
    各セルは スタッフ記録 + 保護者アプローチ の合計回数。
    student_ids を指定すると、その生徒だけに絞り込む (講師の担当生徒フィルタ用)。
    """
    month_keys = _month_keys(months)
    month_set = set(month_keys)

    q = db.query(Student).filter(Student.status.in_(["enrolled", "trial", "on_leave"]))
    if classroom_id:
        q = q.filter(Student.classroom_id == classroom_id)
    if student_ids is not None:
        q = q.filter(Student.id.in_(student_ids))
    students = q.all()
    student_ids = [s.id for s in students]
    if not student_ids:
        return {"months": month_keys, "rows": []}

    # 月別カウント (種別ごと)
    staff_counts: Dict[int, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    contact_counts: Dict[int, Dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for n in db.query(StaffNote).filter(StaffNote.student_id.in_(student_ids)).all():
        mk = n.occurred_at.strftime("%Y-%m")
        if mk in month_set:
            staff_counts[n.student_id][mk] += 1
    for c in db.query(ParentContact).filter(ParentContact.student_id.in_(student_ids)).all():
        mk = c.occurred_at.strftime("%Y-%m")
        if mk in month_set:
            contact_counts[c.student_id][mk] += 1

    current_month = month_keys[-1] if month_keys else None

    rows = []
    for s in students:
        enrolled_month = s.enrolled_at.strftime("%Y-%m") if s.enrolled_at else None
        cells = []
        total = 0
        for mk in month_keys:
            # 入会前の月は enrolled=False (画面では「-」表示)
            enrolled = (enrolled_month is None) or (mk >= enrolled_month)
            sc = staff_counts[s.id].get(mk, 0)
            cc = contact_counts[s.id].get(mk, 0)
            cells.append({"month": mk, "staff": sc, "contact": cc, "total": sc + cc, "enrolled": enrolled})
            total += sc + cc
        # 当月に在籍しているのにアプローチが0件 → 強調対象
        current_cell = next((c for c in cells if c["month"] == current_month), None)
        needs_attention = bool(current_cell and current_cell["enrolled"] and current_cell["total"] == 0)
        rows.append({
            "student_id": s.id,
            "student_name": s.name,
            "grade": s.grade,
            "class_label": s.class_group.name if s.class_group else None,
            "cells": cells,
            "total": total,
            "needs_attention": needs_attention,
        })

    # 当月未アプローチを上に、その後は実施が多い順
    rows.sort(key=lambda r: (not r["needs_attention"], -r["total"]))
    return {"months": month_keys, "rows": rows}


def get_student_activities(db: Session, student_id: int, month: str) -> List[Dict]:
    """指定生徒・指定月(YYYY-MM)のスタッフ記録+保護者アプローチ明細 (ポップアップ用)"""
    try:
        y, mo = map(int, month.split("-"))
        start = date(y, mo, 1)
        end = date(y + 1, 1, 1) if mo == 12 else date(y, mo + 1, 1)
    except (ValueError, IndexError):
        return []

    items = []
    notes = db.query(StaffNote).filter(StaffNote.student_id == student_id).all()
    for n in notes:
        d = n.occurred_at.date() if isinstance(n.occurred_at, datetime) else n.occurred_at
        if start <= d < end:
            items.append({
                "kind": "スタッフ記録",
                "type": n.note_type,
                "content": n.content,
                "occurred_at": n.occurred_at,
                "teacher_name": n.teacher.name if n.teacher else None,
            })
    contacts = db.query(ParentContact).filter(ParentContact.student_id == student_id).all()
    for c in contacts:
        d = c.occurred_at.date() if isinstance(c.occurred_at, datetime) else c.occurred_at
        if start <= d < end:
            items.append({
                "kind": "保護者アプローチ",
                "type": c.contact_type,
                "content": c.summary,
                "occurred_at": c.occurred_at,
                "teacher_name": c.teacher.name if c.teacher else None,
            })

    items.sort(key=lambda x: x["occurred_at"], reverse=True)
    return items
