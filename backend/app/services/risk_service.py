"""
リスク分析サービス
ルールベースのリスクスコア計算 (Claude API統合時はai_service.pyに委譲)

リスク判定ルール:
  HIGH: 出席率30日 < 60% または 3回連続成績下降
  MEDIUM: 出席率30日 60-75% または 2回連続成績下降
  LOW: それ以外
"""

from typing import List, Dict, Any, Optional
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.student import Student
from app.models.attendance import Attendance
from app.models.test_score import TestScore


def compute_attendance_rate(student_id: int, db: Session, days: int = 30) -> float:
    """指定期間の出席率を計算 (0-100)"""
    cutoff = date.today() - timedelta(days=days)
    records = db.query(Attendance).filter(
        Attendance.student_id == student_id,
        Attendance.class_date >= cutoff
    ).all()

    if not records:
        return 100.0  # データなし = デフォルト100%

    present = sum(1 for r in records if r.status == "present")
    return round(present / len(records) * 100, 1)


def get_score_trend(student_id: int, db: Session) -> Dict[str, Any]:
    """
    科目別の成績トレンドを分析
    3回連続下降があれば 'declining' を返す
    """
    # 最新4セッション分のスコアを取得
    scores = db.query(TestScore).filter(
        TestScore.student_id == student_id
    ).order_by(TestScore.test_date.desc(), TestScore.test_id.desc()).all()

    if not scores:
        return {"trend": "stable", "declining_subjects": []}

    # test_id別にグループ化
    sessions: Dict[str, Dict[str, float]] = {}
    for s in scores:
        if s.test_id not in sessions:
            sessions[s.test_id] = {}
        sessions[s.test_id][s.subject] = s.raw_score

    # test_idを時系列順にソート (文字列ソート = 日付順)
    sorted_sessions = sorted(sessions.keys())
    if len(sorted_sessions) < 3:
        return {"trend": "stable", "declining_subjects": []}

    # 各科目で3回連続下降を確認
    declining_subjects = []
    subjects = ["国語", "数学", "英語", "理科", "社会"]

    for subject in subjects:
        consecutive_decline = 0
        for i in range(1, len(sorted_sessions)):
            prev_session = sorted_sessions[i - 1]
            curr_session = sorted_sessions[i]
            prev_score = sessions[prev_session].get(subject)
            curr_score = sessions[curr_session].get(subject)
            if prev_score is not None and curr_score is not None:
                if curr_score < prev_score:
                    consecutive_decline += 1
                else:
                    consecutive_decline = 0
            if consecutive_decline >= 2:  # 3回分 = 2回の下降
                declining_subjects.append(subject)
                break

    if declining_subjects:
        return {"trend": "declining", "declining_subjects": declining_subjects}

    # 全体的な傾向を判定 (最新2セッション比較)
    if len(sorted_sessions) >= 2:
        last = sorted_sessions[-1]
        prev = sorted_sessions[-2]
        last_avg = sum(sessions[last].values()) / max(len(sessions[last]), 1)
        prev_avg = sum(sessions[prev].values()) / max(len(sessions[prev]), 1)
        if last_avg > prev_avg + 2:
            return {"trend": "improving", "declining_subjects": []}
        elif last_avg < prev_avg - 2:
            return {"trend": "declining", "declining_subjects": []}

    return {"trend": "stable", "declining_subjects": []}


def compute_risk_score(student_id: int, db: Session) -> Dict[str, Any]:
    """
    生徒のリスクスコアを計算
    戻り値: {risk_level, attendance_rate_30d, score_trend, factors, suggestions}
    """
    attendance_rate = compute_attendance_rate(student_id, db)
    score_info = get_score_trend(student_id, db)
    score_trend = score_info["trend"]
    declining_subjects = score_info.get("declining_subjects", [])

    factors = []
    suggestions = []

    # リスクレベル判定
    if attendance_rate < 60 or (score_trend == "declining" and len(declining_subjects) >= 2):
        risk_level = "high"
    elif attendance_rate < 75 or score_trend == "declining":
        risk_level = "medium"
    else:
        risk_level = "low"

    # 要因の説明
    if attendance_rate < 60:
        factors.append(f"出席率が低下しています ({attendance_rate:.0f}%)")
        suggestions.append("保護者に電話連絡し、欠席理由を確認してください")
        suggestions.append("次回授業前にリマインド連絡を入れてください")
    elif attendance_rate < 75:
        factors.append(f"出席率がやや低下しています ({attendance_rate:.0f}%)")
        suggestions.append("欠席が続く場合は保護者への連絡を検討してください")

    if declining_subjects:
        factors.append(f"{', '.join(declining_subjects)} の成績が3回連続で下降しています")
        suggestions.append(f"{declining_subjects[0]} の補習授業または追加サポートを提案してください")
        suggestions.append("学習計画の見直しを保護者と共有してください")
    elif score_trend == "declining":
        factors.append("全体的な成績が下降傾向にあります")
        suggestions.append("弱点科目の特定と個別対応を検討してください")

    if risk_level == "high" and not suggestions:
        suggestions.append("至急、担任講師からの面談を設定してください")
        suggestions.append("保護者への状況報告を行ってください")

    return {
        "risk_level": risk_level,
        "attendance_rate_30d": attendance_rate,
        "score_trend": score_trend,
        "factors": factors,
        "suggestions": suggestions,
    }


def get_all_risk_students(db: Session, classroom_id: Optional[int] = None) -> List[Dict]:
    """
    全在籍生徒のリスク評価を一括実行
    高リスク→中リスク→低リスクの順でソート
    """
    query = db.query(Student).filter(
        Student.status.in_(["enrolled", "trial"])
    )
    if classroom_id:
        query = query.filter(Student.classroom_id == classroom_id)

    students = query.all()
    results = []

    for student in students:
        risk = compute_risk_score(student.id, db)
        results.append({
            "student_id": student.id,
            "student_name": student.name,
            "grade": student.grade,
            "status": student.status,
            **risk,
        })

    # リスクレベル順にソート: high > medium > low
    level_order = {"high": 0, "medium": 1, "low": 2}
    results.sort(key=lambda x: (level_order.get(x["risk_level"], 3), -x["attendance_rate_30d"]))

    return results
