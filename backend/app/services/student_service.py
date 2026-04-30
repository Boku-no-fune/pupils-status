"""
生徒サービス
生徒詳細データの集計・組み立てを担当
"""

from typing import Optional, List
from datetime import date, timedelta
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc

from app.models.student import Student
from app.models.attendance import Attendance, RoomLog
from app.models.test_score import TestScore
from app.services.risk_service import compute_risk_score, compute_attendance_rate


def get_last_visit(student_id: int, db: Session) -> Optional[date]:
    """最終来室日を取得"""
    last_log = db.query(RoomLog).filter(
        RoomLog.student_id == student_id
    ).order_by(RoomLog.entered_at.desc()).first()

    if last_log:
        return last_log.entered_at.date()

    # room_logがない場合は最後の出席日を参照
    last_att = db.query(Attendance).filter(
        Attendance.student_id == student_id,
        Attendance.status == "present"
    ).order_by(Attendance.class_date.desc()).first()

    return last_att.class_date if last_att else None


def get_recent_grade_change(student_id: int, db: Session) -> Optional[dict]:
    """
    最新2回のテスト結果から成績変化を計算
    最も変化が大きい科目を返す
    """
    scores = db.query(TestScore).filter(
        TestScore.student_id == student_id
    ).order_by(TestScore.test_date.desc(), TestScore.test_id.desc()).all()

    if not scores:
        return None

    # test_id別にグループ化
    sessions = {}
    for s in scores:
        if s.test_id not in sessions:
            sessions[s.test_id] = {}
        sessions[s.test_id][s.subject] = s.raw_score

    sorted_sessions = sorted(sessions.keys(), reverse=True)
    if len(sorted_sessions) < 2:
        return None

    latest = sessions[sorted_sessions[0]]
    previous = sessions[sorted_sessions[1]]

    # 最大変化科目を探す
    max_change = 0
    max_subject = None

    for subject in latest:
        if subject in previous:
            change = latest[subject] - previous[subject]
            if abs(change) > abs(max_change):
                max_change = change
                max_subject = subject

    if max_subject is None:
        return None

    direction = "up" if max_change > 0 else ("down" if max_change < 0 else "stable")
    return {
        "subject": max_subject,
        "change": round(max_change, 1),
        "direction": direction,
    }


def get_student_list(
    db: Session,
    status: Optional[str] = None,
    grade: Optional[int] = None,
    teacher_id: Optional[int] = None,
    classroom_id: Optional[int] = None,
    search: Optional[str] = None,
    page: int = 1,
    per_page: int = 20,
) -> dict:
    """
    生徒一覧を取得 (ダッシュボードTab1用)
    last_visit, attendance_rate, grade_change を付加する
    """
    query = db.query(Student)

    if status:
        query = query.filter(Student.status == status)
    if grade:
        query = query.filter(Student.grade == grade)
    if teacher_id:
        query = query.filter(Student.assigned_teacher_id == teacher_id)
    if classroom_id:
        query = query.filter(Student.classroom_id == classroom_id)
    if search:
        query = query.filter(Student.name.ilike(f"%{search}%"))

    total = query.count()
    students = query.order_by(Student.name).offset((page - 1) * per_page).limit(per_page).all()

    results = []
    for s in students:
        teacher_name = s.assigned_teacher.name if s.assigned_teacher else None
        last_visit = get_last_visit(s.id, db)
        attendance_rate = compute_attendance_rate(s.id, db)
        grade_change = get_recent_grade_change(s.id, db)

        results.append({
            "id": s.id,
            "name": s.name,
            "grade": s.grade,
            "school": s.school,
            "status": s.status,
            "enrolled_at": s.enrolled_at,
            "withdrawn_at": s.withdrawn_at,
            "assigned_teacher_id": s.assigned_teacher_id,
            "assigned_teacher_name": teacher_name,
            "classroom_id": s.classroom_id,
            "last_visit": last_visit,
            "attendance_rate_30d": attendance_rate,
            "recent_grade_change": grade_change,
        })

    return {"total": total, "page": page, "per_page": per_page, "students": results}


def get_student_detail(student_id: int, db: Session) -> Optional[dict]:
    """
    生徒詳細を全関連データと共に取得
    """
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        return None

    teacher_name = student.assigned_teacher.name if student.assigned_teacher else None
    last_visit = get_last_visit(student_id, db)
    attendance_rate = compute_attendance_rate(student_id, db)
    grade_change = get_recent_grade_change(student_id, db)
    risk = compute_risk_score(student_id, db)

    # 最近90日の出欠
    cutoff = date.today() - timedelta(days=90)
    recent_attendances = db.query(Attendance).filter(
        Attendance.student_id == student_id,
        Attendance.class_date >= cutoff,
    ).order_by(Attendance.class_date.desc()).all()

    # 保護者コンタクトに担当者名を付加
    contacts = []
    for c in student.parent_contacts:
        teacher_n = c.teacher.name if c.teacher else None
        contacts.append({
            "id": c.id,
            "contact_type": c.contact_type,
            "occurred_at": c.occurred_at,
            "summary": c.summary,
            "teacher_id": c.teacher_id,
            "teacher_name": teacher_n,
        })

    # 営業アクションに担当者名を付加
    sales = []
    for sa in student.sales_actions:
        teacher_n = sa.assigned_teacher.name if sa.assigned_teacher else None
        sales.append({
            "id": sa.id,
            "action_type": sa.action_type,
            "target_product": sa.target_product,
            "status": sa.status,
            "note": sa.note,
            "actioned_at": sa.actioned_at,
            "assigned_to": sa.assigned_to,
            "assigned_teacher_name": teacher_n,
        })

    return {
        "id": student.id,
        "name": student.name,
        "grade": student.grade,
        "school": student.school,
        "status": student.status,
        "enrolled_at": student.enrolled_at,
        "trial_at": student.trial_at,
        "withdrawn_at": student.withdrawn_at,
        "assigned_teacher_id": student.assigned_teacher_id,
        "assigned_teacher_name": teacher_name,
        "classroom_id": student.classroom_id,
        "last_visit": last_visit,
        "attendance_rate_30d": attendance_rate,
        "recent_grade_change": grade_change,
        "enrollment_events": [
            {"id": e.id, "event_type": e.event_type, "occurred_at": e.occurred_at, "note": e.note}
            for e in student.enrollment_events
        ],
        "enrollments": [
            {
                "id": e.id,
                "course_id": e.course_id,
                "course": {"id": e.course.id, "name": e.course.name, "subject": e.course.subject} if e.course else None,
                "started_at": e.started_at,
                "ended_at": e.ended_at,
                "change_type": e.change_type,
            }
            for e in student.enrollments
        ],
        "recent_attendances": [
            {"id": a.id, "class_date": a.class_date, "status": a.status, "note": a.note}
            for a in recent_attendances
        ],
        "test_scores": [
            {
                "id": ts.id,
                "test_id": ts.test_id,
                "test_name": ts.test_name,
                "subject": ts.subject,
                "raw_score": ts.raw_score,
                "rank": ts.rank,
                "deviation_value": ts.deviation_value,
                "test_date": ts.test_date,
            }
            for ts in student.test_scores
        ],
        "target_schools": [
            {"id": ts.id, "school_name": ts.school_name, "priority": ts.priority, "recorded_at": ts.recorded_at}
            for ts in student.target_schools
        ],
        "school_grades": [
            {"id": sg.id, "term": sg.term, "subject": sg.subject, "score": sg.score, "grade_notation": sg.grade_notation}
            for sg in student.school_grades
        ],
        "parent_contacts": contacts,
        "payments": [
            {"id": p.id, "amount": p.amount, "paid_at": p.paid_at, "due_at": p.due_at, "category": p.category, "status": p.status}
            for p in student.payments
        ],
        "sales_actions": sales,
        "risk_score": risk,
    }
