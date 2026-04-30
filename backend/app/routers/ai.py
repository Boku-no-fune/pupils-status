"""
AIルーター
GET  /api/ai/risk/{student_id}  — リスク分析 + AI提案
POST /api/ai/study-plan         — 学習改善プラン生成
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.services.student_service import get_student_detail
from app.services.risk_service import compute_risk_score
from app.services.ai_service import get_ai_service
from app.dependencies.auth import require_roles

router = APIRouter(prefix="/ai", tags=["AI分析"])


@router.get("/risk/{student_id}")
async def get_risk_analysis(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager")),
    ai_service=Depends(get_ai_service),
):
    """
    生徒のリスク分析とAI提案を返す
    ANTHROPIC_API_KEY 未設定時はダミーデータを返す
    """
    # ルールベースのリスクスコアを計算
    risk = compute_risk_score(student_id, db)

    # 生徒データを取得
    student = get_student_detail(student_id, db)
    if not student:
        raise HTTPException(status_code=404, detail="生徒が見つかりません")

    # AIサービスに詳細提案を依頼
    student_data = {
        "student_id": student_id,
        "grade": student.get("grade"),
        "status": student.get("status"),
        "attendance_rate_30d": risk["attendance_rate_30d"],
        "score_trend": risk["score_trend"],
        "risk_level": risk["risk_level"],
        "factors": risk["factors"],
        "suggestions": risk["suggestions"],
        "declining_subjects": [],  # risk_serviceから取得できる場合は付加
    }

    ai_result = await ai_service.get_risk_analysis(student_data)
    study_plan = await ai_service.get_study_plan(student_data)

    return {
        **risk,
        "suggestions": ai_result.get("suggestions", risk["suggestions"]),
        "study_plan": study_plan,
    }


@router.post("/study-plan")
async def get_study_plans(
    student_ids: list[int],
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "room_manager")),
    ai_service=Depends(get_ai_service),
):
    """複数生徒の学習改善プランを一括生成"""
    results = []
    for student_id in student_ids[:10]:  # 最大10名
        risk = compute_risk_score(student_id, db)
        plan = await ai_service.get_study_plan({
            "student_id": student_id,
            **risk,
        })
        results.append({"student_id": student_id, "study_plan": plan})
    return results
