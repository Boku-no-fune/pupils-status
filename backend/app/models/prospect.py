"""
未入会(見込み)生徒モデルと、入会前ファネルの各ステージ状況

ステージ: 問い合わせ / 資料請求 / 入会テスト / 体験授業 / イベント参加 / 季節講習受講
各ステージの状況: 未対応 / 対応中 / 完了 (+ 対応メモ)
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Prospect(Base):
    __tablename__ = "prospects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    grade = Column(Integer, nullable=True)
    school = Column(String(200), nullable=True)
    source = Column(String(50), nullable=True)        # 問い合わせ経路 (HP/チラシ/紹介 等)

    # 住所・座標 (地図用ダミー)
    address = Column(String(255), nullable=True)
    home_lat = Column(Float, nullable=True)
    home_lng = Column(Float, nullable=True)

    status = Column(String(20), nullable=False, default="active")  # active / converted / lost
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    first_contact_at = Column(Date, nullable=True)
    note = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    stages = relationship("ProspectStage", back_populates="prospect",
                          order_by="ProspectStage.sort_order",
                          cascade="all, delete-orphan")
    staff_notes = relationship("StaffNote", back_populates="prospect",
                               order_by="StaffNote.occurred_at.desc()")
    assigned_teacher = relationship("User", foreign_keys=[assigned_to])


class ProspectStage(Base):
    __tablename__ = "prospect_stages"

    id = Column(Integer, primary_key=True, index=True)
    prospect_id = Column(Integer, ForeignKey("prospects.id"), nullable=False, index=True)

    stage = Column(String(30), nullable=False)        # 問い合わせ/資料請求/入会テスト/体験授業/イベント参加/季節講習受講
    status = Column(String(10), nullable=False, default="未対応")  # 未対応/対応中/完了
    memo = Column(Text, nullable=True)
    sort_order = Column(Integer, nullable=False, default=0)
    occurred_at = Column(Date, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    prospect = relationship("Prospect", back_populates="stages")
