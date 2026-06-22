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
    school_type: Optional[str] = None,
    division: Optional[str] = None,
    sort_by: str = "grade",
    sort_dir: str = "asc",
    page: int = 1,
    per_page: int = 20,
) -> dict:
    """
    生徒一覧を取得 (ダッシュボードTab1用)
    member_number, クラス, last_visit, attendance_rate, grade_change を付加する
    並び替えは派生列も含むため Python 側で実施 (デフォルト: 学年→クラス 昇順)
    """
    from app.models.enrollment import Enrollment
    from app.models.course import Course

    query = db.query(Student)

    if status:
        query = query.filter(Student.status == status)
    if grade:
        query = query.filter(Student.grade == grade)
    if teacher_id:
        # 複数担当 (student_teachers) または代表担当のいずれかに一致
        from app.models.class_group import student_teachers
        st_subq = db.query(student_teachers.c.student_id).filter(
            student_teachers.c.user_id == teacher_id
        ).subquery()
        query = query.filter(
            (Student.assigned_teacher_id == teacher_id) | (Student.id.in_(st_subq))
        )
    if classroom_id:
        query = query.filter(Student.classroom_id == classroom_id)
    if search:
        query = query.filter(Student.name.ilike(f"%{search}%"))
    if school_type:
        query = query.filter(Student.school_type == school_type)
    if division:
        subq = db.query(Enrollment.student_id).join(Course).filter(
            Course.division == division,
            Enrollment.ended_at.is_(None),
        ).subquery()
        query = query.filter(Student.id.in_(subq))

    students = query.all()

    results = []
    for s in students:
        teacher_name = s.assigned_teacher.name if s.assigned_teacher else None
        last_visit = get_last_visit(s.id, db)
        attendance_rate = compute_attendance_rate(s.id, db)
        grade_change = get_recent_grade_change(s.id, db)

        # クラス表示: 集団=クラス名 / それ以外=部門名
        active_divisions = sorted({
            e.course.division for e in s.enrollments
            if e.course and e.course.division and not e.ended_at
        })
        if s.class_group:
            class_label = s.class_group.name
            class_sort = s.class_group.sort_order
        elif active_divisions:
            class_label = " / ".join(active_divisions)
            class_sort = 100
        else:
            class_label = None
            class_sort = 999

        results.append({
            "id": s.id,
            "name": s.name,
            "member_number": s.member_number,
            "grade": s.grade,
            "school": s.school,
            "school_type": s.school_type,
            "status": s.status,
            "class_label": class_label,
            "class_sort": class_sort,
            "divisions": active_divisions,
            "enrolled_at": s.enrolled_at,
            "withdrawn_at": s.withdrawn_at,
            "assigned_teacher_id": s.assigned_teacher_id,
            "assigned_teacher_name": teacher_name,
            "teachers": [{"id": t.id, "name": t.name} for t in s.teachers],
            "classroom_id": s.classroom_id,
            "last_visit": last_visit,
            "attendance_rate_30d": attendance_rate,
            "recent_grade_change": grade_change,
        })

    # 並び替え (派生列対応)
    def sort_key(r):
        if sort_by == "name":
            return (r["name"] or "",)
        if sort_by == "member_number":
            return (r["member_number"] or "",)
        if sort_by == "status":
            return (r["status"] or "",)
        if sort_by == "class":
            return (r["class_sort"], r["grade"])
        if sort_by == "last_visit":
            return (r["last_visit"] or date.min,)
        if sort_by == "attendance_rate_30d":
            return (r["attendance_rate_30d"] if r["attendance_rate_30d"] is not None else -1,)
        # default: grade → class
        return (r["grade"], r["class_sort"])

    results.sort(key=sort_key, reverse=(sort_dir == "desc"))

    total = len(results)
    start = (page - 1) * per_page
    paged = results[start:start + per_page]

    return {"total": total, "page": page, "per_page": per_page, "students": paged}


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

    # スタッフ記録
    staff_notes = []
    for sn in student.staff_notes:
        teacher_n = sn.teacher.name if sn.teacher else None
        staff_notes.append({
            "id": sn.id,
            "note_type": sn.note_type,
            "content": sn.content,
            "tags": sn.tags or [],
            "occurred_at": sn.occurred_at,
            "teacher_id": sn.teacher_id,
            "teacher_name": teacher_n,
        })

    # 映像授業ログ (直近100件)
    video_logs = [
        {
            "id": vl.id,
            "lesson_name": vl.lesson_name,
            "lesson_category": vl.lesson_category,
            "viewed_at": vl.viewed_at,
            "duration_minutes": vl.duration_minutes,
            "completion_rate": vl.completion_rate,
            "source_system": vl.source_system,
        }
        for vl in student.video_lesson_logs[:100]
    ]

    # 受講部門 (重複排除・在籍中のみ)
    divisions = sorted({
        e.course.division for e in student.enrollments
        if e.course and e.course.division and not e.ended_at
    })

    # クラス情報
    class_group = None
    if student.class_group:
        class_group = {
            "id": student.class_group.id,
            "name": student.class_group.name,
            "level": student.class_group.level,
            "grade": student.class_group.grade,
        }

    # 紹介・被紹介
    referrals_made = [
        {
            "id": r.id,
            "referred_student_id": r.referred_student_id,
            "referred_name": r.referred_name,
            "occurred_at": r.occurred_at,
            "note": r.note,
        }
        for r in student.referrals_made
    ]
    referrals_received = [
        {
            "id": r.id,
            "referrer_student_id": r.referrer_student_id,
            "referrer_name": r.referrer.name if r.referrer else None,
            "occurred_at": r.occurred_at,
            "note": r.note,
        }
        for r in student.referrals_received
    ]

    return {
        "id": student.id,
        "name": student.name,
        "grade": student.grade,
        "school": student.school,
        "school_type": student.school_type,
        "photo_data": student.photo_data,
        "member_number": student.member_number,
        "gender": student.gender,
        "parent_name": student.parent_name,
        "sibling_info": student.sibling_info,
        "status": student.status,
        "enrolled_at": student.enrolled_at,
        "trial_at": student.trial_at,
        "withdrawn_at": student.withdrawn_at,
        "assigned_teacher_id": student.assigned_teacher_id,
        "assigned_teacher_name": teacher_name,
        "classroom_id": student.classroom_id,
        "class_group_id": student.class_group_id,
        "class_group": class_group,
        "divisions": divisions,
        "teachers": [{"id": t.id, "name": t.name, "role": t.role} for t in student.teachers],
        "last_visit": last_visit,
        "attendance_rate_30d": attendance_rate,
        "recent_grade_change": grade_change,
        "phones": [
            {"id": p.id, "phone_number": p.phone_number, "memo": p.memo, "position": p.position}
            for p in student.phones
        ],
        "special_notes": [
            {"id": sn.id, "content": sn.content, "importance": sn.importance, "created_at": sn.created_at}
            for sn in student.special_notes
        ],
        "profile_memos": [
            {"id": pm.id, "category": pm.category, "content": pm.content, "created_at": pm.created_at}
            for pm in student.profile_memos
        ],
        "parent_requests": [
            {"id": pr.id, "request_type": pr.request_type, "content": pr.content,
             "status": pr.status, "occurred_at": pr.occurred_at}
            for pr in student.parent_requests
        ],
        "exam_certifications": [
            {"id": ec.id, "exam_type": ec.exam_type, "level": ec.level, "score": ec.score,
             "result": ec.result, "exam_date": ec.exam_date}
            for ec in student.exam_certifications
        ],
        "referrals_made": referrals_made,
        "referrals_received": referrals_received,
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
            {"id": a.id, "class_date": a.class_date, "status": a.status, "note": a.note,
             "makeup_type": a.makeup_type, "makeup_note": a.makeup_note}
            for a in recent_attendances
        ],
        "test_scores": [
            {
                "id": ts.id,
                "test_id": ts.test_id,
                "test_name": ts.test_name,
                "test_type": ts.test_type,
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
        "staff_notes": staff_notes,
        "video_lesson_logs": video_logs,
    }
