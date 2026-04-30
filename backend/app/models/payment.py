"""
納入記録モデル
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Payment(Base):
    """
    授業料・講習費等の納入記録
    category: 授業料/講習費/教材費/その他
    status: paid(済) / pending(未)
    """
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)

    amount = Column(Float, nullable=False)
    paid_at = Column(Date, nullable=True)        # 実際の支払日 (Null = 未払い)
    due_at = Column(Date, nullable=True)         # 請求予定日
    category = Column(String(50), nullable=False, default="授業料")
    status = Column(String(20), nullable=False, default="paid")  # paid / pending

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # リレーション
    student = relationship("Student", back_populates="payments")
