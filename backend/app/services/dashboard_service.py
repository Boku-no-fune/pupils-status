"""
ダッシュボードサービス
各タブ用の集計データを生成する
"""

from typing import List, Dict, Optional
from datetime import date, timedelta
from collections import defaultdict
from sqlalchemy.orm import Session

from app.models.student import Student
from app.models.attendance import Attendance
from app.models.test_score import TestScore
from app.models.sales import SalesAction, SalesGoal
from app.services.risk_service import compute_attendance_rate


def get_dashboard_stats(db: Session, classroom_id: Optional[int] = None) -> Dict:
    """ダッシュボード上部サマリーカード用の集計"""
    query = db.query(Student)
    if classroom_id:
        query = query.filter(Student.classroom_id == classroom_id)

    all_students = query.all()

    enrolled = sum(1 for s in all_students if s.status == "enrolled")
    trial = sum(1 for s in all_students if s.status == "trial")
    on_leave = sum(1 for s in all_students if s.status == "on_leave")
    withdrawn = sum(1 for s in all_students if s.status == "withdrawn")

    # 高リスク生徒数: 出席率60%未満
    active_students = [s for s in all_students if s.status in ["enrolled", "trial"]]
    high_risk = sum(
        1 for s in active_students
        if compute_attendance_rate(s.id, db) < 60
    )

    # 平均出席率
    rates = [compute_attendance_rate(s.id, db) for s in active_students]
    avg_rate = sum(rates) / len(rates) if rates else 100.0

    return {
        "total_enrolled": enrolled,
        "total_trial": trial,
        "total_on_leave": on_leave,
        "total_withdrawn": withdrawn,
        "high_risk_count": high_risk,
        "avg_attendance_rate": round(avg_rate, 1),
    }


def get_attendance_trend(
    db: Session,
    classroom_id: Optional[int] = None,
    months: int = 6
) -> List[Dict]:
    """
    過去N ヶ月の月別出席率推移 (Tab2折れ線グラフ用)
    """
    today = date.today()
    results = []

    for m in range(months - 1, -1, -1):
        # 対象月の1日と末日を計算
        target_year = today.year
        target_month = today.month - m
        while target_month <= 0:
            target_month += 12
            target_year -= 1

        month_start = date(target_year, target_month, 1)
        if target_month == 12:
            month_end = date(target_year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = date(target_year, target_month + 1, 1) - timedelta(days=1)

        # 対象生徒の絞り込み
        student_ids_query = db.query(Student.id).filter(
            Student.status.in_(["enrolled", "trial"])
        )
        if classroom_id:
            student_ids_query = student_ids_query.filter(
                Student.classroom_id == classroom_id
            )
        student_ids = [r[0] for r in student_ids_query.all()]

        if not student_ids:
            results.append({
                "month": f"{target_year}-{target_month:02d}",
                "present_count": 0,
                "absent_count": 0,
                "late_count": 0,
                "rate": 100.0,
            })
            continue

        records = db.query(Attendance).filter(
            Attendance.student_id.in_(student_ids),
            Attendance.class_date >= month_start,
            Attendance.class_date <= month_end,
        ).all()

        present = sum(1 for r in records if r.status == "present")
        absent = sum(1 for r in records if r.status == "absent")
        late = sum(1 for r in records if r.status == "late")
        total = len(records)
        rate = round(present / total * 100, 1) if total > 0 else 100.0

        results.append({
            "month": f"{target_year}-{target_month:02d}",
            "present_count": present,
            "absent_count": absent,
            "late_count": late,
            "rate": rate,
        })

    return results


def get_score_trend(
    db: Session,
    classroom_id: Optional[int] = None,
    months: int = 6
) -> List[Dict]:
    """
    過去N ヶ月の科目別平均スコア推移 (Tab2棒グラフ用)
    """
    # 対象生徒
    student_ids_query = db.query(Student.id)
    if classroom_id:
        student_ids_query = student_ids_query.filter(
            Student.classroom_id == classroom_id
        )
    student_ids = [r[0] for r in student_ids_query.all()]

    if not student_ids:
        return []

    cutoff = date.today() - timedelta(days=months * 31)

    scores = db.query(TestScore).filter(
        TestScore.student_id.in_(student_ids),
        TestScore.test_date >= cutoff,
    ).order_by(TestScore.test_date).all()

    # test_idごとにグループ化
    sessions: Dict[str, Dict] = {}
    for s in scores:
        if s.test_id not in sessions:
            sessions[s.test_id] = {
                "test_id": s.test_id,
                "test_name": s.test_name or s.test_id,
                "test_date": str(s.test_date) if s.test_date else None,
                "subject_scores": defaultdict(list),
            }
        sessions[s.test_id]["subject_scores"][s.subject].append(s.raw_score)

    results = []
    for test_id, data in sorted(sessions.items()):
        avg_scores = {
            subject: round(sum(vals) / len(vals), 1)
            for subject, vals in data["subject_scores"].items()
            if vals
        }
        results.append({
            "test_id": data["test_id"],
            "test_name": data["test_name"],
            "test_date": data["test_date"],
            "scores": avg_scores,
        })

    return results


def get_sales_progress(db: Session, period: Optional[str] = None) -> List[Dict]:
    """
    営業目標進捗データ (Tab3用)
    """
    query = db.query(SalesGoal)
    if period:
        query = query.filter(SalesGoal.period == period)

    goals = query.all()
    results = []

    for goal in goals:
        # 対象商品の営業アクション集計
        actions_query = db.query(SalesAction)
        if goal.target_product:
            actions_query = actions_query.filter(
                SalesAction.target_product == goal.target_product
            )

        actions = actions_query.all()

        signed_up = sum(1 for a in actions if a.status == "signed_up")
        in_progress = sum(1 for a in actions if a.status == "in_progress")
        declined = sum(1 for a in actions if a.status == "declined")
        not_started = sum(1 for a in actions if a.status == "pending")

        progress_pct = round(signed_up / goal.target_count * 100, 1) if goal.target_count > 0 else 0

        results.append({
            "goal_id": goal.id,
            "goal_type": goal.goal_type,
            "target_product": goal.target_product,
            "target_count": goal.target_count,
            "period": goal.period,
            "signed_up": signed_up,
            "in_progress": in_progress,
            "declined": declined,
            "not_started": not_started,
            "progress_pct": progress_pct,
        })

    return results
