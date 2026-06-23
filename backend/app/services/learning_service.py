"""
学習進捗サービス
映像授業視聴ログと宿題提出状況の集計
"""

from typing import Optional, List
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.student import Student
from app.models.video_lesson_log import VideoLessonLog
from app.models.homework import Homework


def get_learning_progress(db: Session, classroom_id: Optional[int] = None,
                          student_ids_filter: Optional[List[int]] = None) -> dict:
    """
    ダッシュボードTab5用 学習進捗集計
    - 映像授業: 月別視聴時間推移 / 科目別視聴時間
    - 宿題: 直近30日の提出率 (生徒別)
    student_ids_filter を指定すると、その生徒だけに絞り込む (講師の担当生徒フィルタ用)。
    """

    # 対象生徒を絞り込む
    student_query = db.query(Student).filter(
        Student.status.in_(["enrolled", "trial"])
    )
    if classroom_id:
        student_query = student_query.filter(Student.classroom_id == classroom_id)
    if student_ids_filter is not None:
        student_query = student_query.filter(Student.id.in_(student_ids_filter))
    students = student_query.all()
    student_ids = [s.id for s in students]

    if not student_ids:
        return {
            "video_monthly": [],
            "video_by_category": [],
            "homework_summary": [],
        }

    # ===== 映像授業: 月別視聴時間 (過去6ヶ月) =====
    six_months_ago = date.today() - timedelta(days=180)

    monthly_rows = db.query(
        func.to_char(VideoLessonLog.viewed_at, 'YYYY-MM').label('month'),
        func.sum(VideoLessonLog.duration_minutes).label('total_minutes'),
        func.count(VideoLessonLog.id).label('view_count'),
    ).filter(
        VideoLessonLog.student_id.in_(student_ids),
        VideoLessonLog.viewed_at >= six_months_ago,
    ).group_by('month').order_by('month').all()

    video_monthly = [
        {
            "month": row.month,
            "total_minutes": round(float(row.total_minutes or 0), 1),
            "view_count": row.view_count,
        }
        for row in monthly_rows
    ]

    # ===== 映像授業: 科目・カテゴリ別視聴時間 =====
    category_rows = db.query(
        VideoLessonLog.lesson_category,
        func.sum(VideoLessonLog.duration_minutes).label('total_minutes'),
        func.count(VideoLessonLog.id).label('view_count'),
    ).filter(
        VideoLessonLog.student_id.in_(student_ids),
        VideoLessonLog.viewed_at >= six_months_ago,
    ).group_by(VideoLessonLog.lesson_category).order_by(
        func.sum(VideoLessonLog.duration_minutes).desc()
    ).all()

    video_by_category = [
        {
            "category": row.lesson_category or "未分類",
            "total_minutes": round(float(row.total_minutes or 0), 1),
            "view_count": row.view_count,
        }
        for row in category_rows
    ]

    # ===== 宿題提出状況: 直近30日・生徒別 =====
    thirty_days_ago = date.today() - timedelta(days=30)

    hw_rows = db.query(
        Homework.student_id,
        func.count(Homework.id).label('total'),
        func.count(Homework.submitted_at).label('submitted'),
    ).filter(
        Homework.student_id.in_(student_ids),
        Homework.assigned_date >= thirty_days_ago,
    ).group_by(Homework.student_id).all()

    # student_idをname等にマッピング
    student_map = {s.id: s for s in students}

    homework_summary = []
    for row in hw_rows:
        s = student_map.get(row.student_id)
        if not s:
            continue
        rate = round((row.submitted / row.total * 100) if row.total > 0 else 0, 1)
        homework_summary.append({
            "student_id": row.student_id,
            "student_name": s.name,
            "grade": s.grade,
            "total": row.total,
            "submitted": row.submitted,
            "submission_rate": rate,
        })

    # 提出率の低い順にソート
    homework_summary.sort(key=lambda x: x["submission_rate"])

    return {
        "video_monthly": video_monthly,
        "video_by_category": video_by_category,
        "homework_summary": homework_summary,
    }
