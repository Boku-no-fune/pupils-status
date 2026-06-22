"""
生徒詳細ページ用の追加情報モデル群

- StudentPhone:       電話番号(最大3件)+メモ (番号はシステム連携 / メモは手入力)
- SpecialNote:        特記事項 (重要度タグ付き・手入力)
- ProfileMemo:        プロフィール定型メモ (部活動・習い事・家族構成等・手入力)
- ParentRequest:      保護者からの要望・クレーム履歴 (手入力)
- Referral:           紹介履歴・被紹介履歴 (システム連携)
- ExamCertification:  英検・漢検などの検定結果
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class StudentPhone(Base):
    __tablename__ = "student_phones"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)

    phone_number = Column(String(20), nullable=False)   # システム連携
    memo = Column(String(50), nullable=True)            # 「父の携帯」など (手入力)
    position = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student", back_populates="phones")


class SpecialNote(Base):
    """特記事項 — 最上段コンテナ直下に表示。重要度タグ付き。"""
    __tablename__ = "special_notes"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)

    content = Column(Text, nullable=False)
    importance = Column(String(10), nullable=False, default="中")  # 高 / 中 / 低
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student", back_populates="special_notes")


class ProfileMemo(Base):
    """プロフィール定型メモ — カテゴリ別に追記していく。"""
    __tablename__ = "profile_memos"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)

    # 部活動 / 習い事 / 家族構成 / 家族の職業・学年 / 通学校情報
    category = Column(String(30), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student", back_populates="profile_memos")


class ParentRequest(Base):
    """保護者からの要望・クレーム履歴。"""
    __tablename__ = "parent_requests"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)

    request_type = Column(String(10), nullable=False, default="要望")  # 要望 / クレーム
    content = Column(Text, nullable=False)
    status = Column(String(10), nullable=False, default="対応中")       # 対応中 / 対応済
    occurred_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student", back_populates="parent_requests")


class Referral(Base):
    """
    紹介履歴・被紹介履歴 (システム連携)
    referrer_student_id: 紹介した生徒
    referred_student_id: 紹介された生徒 (在籍生の場合)
    referred_name:       紹介された人 (未入会の場合の氏名)
    """
    __tablename__ = "referrals"

    id = Column(Integer, primary_key=True, index=True)
    referrer_student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    referred_student_id = Column(Integer, ForeignKey("students.id"), nullable=True, index=True)
    referred_name = Column(String(100), nullable=True)

    occurred_at = Column(Date, nullable=True)
    note = Column(String(200), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    referrer = relationship("Student", foreign_keys=[referrer_student_id],
                            back_populates="referrals_made")
    referred = relationship("Student", foreign_keys=[referred_student_id],
                            back_populates="referrals_received")


class ExamCertification(Base):
    """
    英検・漢検などの検定
    英検: 5級/4級/3級/準2級/準2級プラス/2級/準1級/1級 + スコア
    漢検: 10〜3級/準2級/2級/準1級/1級
    """
    __tablename__ = "exam_certifications"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)

    exam_type = Column(String(20), nullable=False)   # 英検 / 漢検
    level = Column(String(20), nullable=False)        # 級
    score = Column(Integer, nullable=True)            # スコア (英検CSEなど)
    result = Column(String(10), nullable=False, default="合格")  # 合格 / 不合格 / 受験予定
    exam_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student", back_populates="exam_certifications")
