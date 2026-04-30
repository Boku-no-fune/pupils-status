"""
AIサービス — Claude API統合ポイント

現在はダミー実装。ANTHROPIC_API_KEY を設定すると ClaudeAIService が使用される。
コード変更不要で本番AIに切り替え可能な設計。
"""

from typing import Protocol, List, Dict, Any, runtime_checkable


@runtime_checkable
class AIServiceProtocol(Protocol):
    """AIサービスのインターフェース定義"""
    async def get_risk_analysis(self, student_data: Dict[str, Any]) -> Dict[str, Any]: ...
    async def get_sales_suggestions(self, student_data: Dict[str, Any]) -> List[str]: ...
    async def get_study_plan(self, student_data: Dict[str, Any]) -> str: ...


class DummyAIService:
    """
    ANTHROPIC_API_KEY 未設定時に使用するダミー実装
    ルールベースのリスクスコアに基づいてリアルなテキストを返す
    """

    async def get_risk_analysis(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """ダミーリスク分析 (risk_serviceの結果をそのまま返す)"""
        return {
            "risk_level": student_data.get("risk_level", "low"),
            "factors": student_data.get("factors", []),
            "suggestions": student_data.get("suggestions", ["特に問題ありません。現状維持を継続してください。"]),
        }

    async def get_sales_suggestions(self, student_data: Dict[str, Any]) -> List[str]:
        """夏期講習等の営業アプローチのダミー提案"""
        grade = student_data.get("grade", 7)
        status = student_data.get("status", "enrolled")

        if grade <= 9:  # 中学生
            return [
                "夏期講習の体験授業への招待メールを送付してください。特に英数の集中コースをご案内ください。",
                "保護者への電話フォローアップで学習状況の確認と夏期講習のご案内をしてください。",
                "2学期の定期テスト対策として早期申込特典を強調してください。",
            ]
        else:  # 高校生
            return [
                "大学受験を見据えた夏期集中講座をご案内してください。",
                "模試の結果をもとに志望校別の対策コースをご提案ください。",
                "夏休みの学習計画を保護者と一緒に立てる面談を設定してください。",
            ]

    async def get_study_plan(self, student_data: Dict[str, Any]) -> str:
        """成績向上プランのダミーテキスト生成"""
        grade = student_data.get("grade", 7)
        declining_subjects = student_data.get("declining_subjects", [])
        score_trend = student_data.get("score_trend", "stable")

        grade_label = _grade_label(grade)

        if declining_subjects:
            subjects_str = "・".join(declining_subjects)
            return (
                f"【{grade_label}向け学習改善プラン】\n\n"
                f"現在 {subjects_str} の成績が下降傾向にあります。\n\n"
                f"推奨アクション:\n"
                f"1. 毎週の授業後に {declining_subjects[0]} の復習テスト (15分) を実施\n"
                f"2. 苦手単元の特定 → 個別補習授業の設定 (月2回)\n"
                f"3. 宿題の提出状況を毎週確認し、未提出の場合は即フォロー\n"
                f"4. 月1回の保護者報告で進捗を共有\n\n"
                f"目標: 次回模試で平均+5点以上の改善"
            )
        elif score_trend == "improving":
            return (
                f"【{grade_label}向け学習維持プラン】\n\n"
                f"成績が向上中です。この勢いを維持しましょう！\n\n"
                f"推奨アクション:\n"
                f"1. 現在の学習ペースを継続\n"
                f"2. 得意科目をさらに伸ばす発展問題に挑戦\n"
                f"3. 弱点科目の補強で総合力アップ\n\n"
                f"目標: 上位20%以内の成績を維持"
            )
        else:
            return (
                f"【{grade_label}向け標準学習プラン】\n\n"
                f"現在の成績は安定しています。\n\n"
                f"推奨アクション:\n"
                f"1. 定期的な模試受験で学習到達度を確認\n"
                f"2. 各科目バランスよく学習時間を確保\n"
                f"3. 次学期の目標設定を保護者と共有\n\n"
                f"目標: 現状維持しながら着実な成績アップ"
            )


class ClaudeAIService:
    """
    ANTHROPIC_API_KEY 設定時に使用する本番Claude実装
    将来統合用 — 現在は DummyAIService にフォールバック
    """

    def __init__(self):
        try:
            import anthropic
            self.client = anthropic.Anthropic()
        except ImportError:
            self.client = None

    async def get_risk_analysis(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """Claude APIを使ったリスク分析"""
        if self.client is None:
            return await DummyAIService().get_risk_analysis(student_data)

        prompt = self._build_risk_prompt(student_data)
        try:
            message = self.client.messages.create(
                model="claude-opus-4-5",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            return self._parse_response(message.content[0].text, student_data)
        except Exception:
            # API呼び出し失敗時はダミーにフォールバック
            return await DummyAIService().get_risk_analysis(student_data)

    def _build_risk_prompt(self, student_data: Dict[str, Any]) -> str:
        return f"""あなたは学習塾のCRMシステムのAIアシスタントです。
以下の生徒データを分析し、退会リスクと改善提案をJSON形式で返してください。

生徒データ:
{student_data}

以下のJSON形式で回答してください:
{{
  "risk_level": "high|medium|low",
  "factors": ["リスク要因1", "リスク要因2"],
  "suggestions": ["改善提案1", "改善提案2", "改善提案3"]
}}

日本語で回答してください。"""

    def _parse_response(self, text: str, fallback_data: Dict) -> Dict[str, Any]:
        """Claude APIレスポンスをパース (失敗時はフォールバック)"""
        import json
        try:
            # JSON部分を抽出
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
        except Exception:
            pass
        return {
            "risk_level": fallback_data.get("risk_level", "low"),
            "factors": fallback_data.get("factors", []),
            "suggestions": fallback_data.get("suggestions", []),
        }

    async def get_sales_suggestions(self, student_data: Dict[str, Any]) -> List[str]:
        return await DummyAIService().get_sales_suggestions(student_data)

    async def get_study_plan(self, student_data: Dict[str, Any]) -> str:
        return await DummyAIService().get_study_plan(student_data)


def get_ai_service() -> "DummyAIService | ClaudeAIService":
    """
    FastAPI依存関係: ENV設定に応じてAIサービス実装を返す
    ANTHROPIC_API_KEY が設定されている場合は ClaudeAIService を使用
    """
    from app.config import settings
    if settings.ANTHROPIC_API_KEY:
        return ClaudeAIService()
    return DummyAIService()


def _grade_label(grade: int) -> str:
    """学年番号を日本語ラベルに変換"""
    if grade <= 6:
        return f"小学{grade}年生"
    elif grade <= 9:
        return f"中学{grade - 6}年生"
    else:
        return f"高校{grade - 9}年生"
