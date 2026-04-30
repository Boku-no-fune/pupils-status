"""
営業アクション・目標モデル
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class SalesAction(Base):
    """
    生徒への営業アクション記録
    action_type: trial_invitation(体験招待) / phone_follow(電話フォロー) / dm_campaign(DM) 等
    status: pending(未着手) / in_progress(アプローチ済) / signed_up(申込済) / declined(辞退)
    target_product: 夏期講習/冬期講習/春期講習 等
    """
    __tablename__ = "sales_actions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)

    action_type = Column(String(50), nullable=False)
    target_product = Column(String(100), nullable=True)  # 例: 夏期講習
    status = Column(String(30), nullable=False, default="pending")
    note = Column(Text, nullable=True)
    actioned_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # リレーション
    student = relationship("Student", back_populates="sales_actions")
    assigned_teacher = relationship("User", back_populates="sales_actions",
                                    foreign_keys=[assigned_to])


class SalesGoal(Base):
    """
    営業目標
    goal_type: trial_signup(体験申込) / enrollment(入会) 等
    period: "2024-summer" など
    """
    __tablename__ = "sales_goals"

    id = Column(Integer, primary_key=True, index=True)
    goal_type = Column(String(50), nullable=False)
    target_product = Column(String(100), nullable=True)  # 例: 夏期講習
    target_count = Column(Integer, nullable=False)
    period = Column(String(30), nullable=False)  # 例: "2024-summer"
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # リレーション
    creator = relationship("User", back_populates="created_sales_goals")
