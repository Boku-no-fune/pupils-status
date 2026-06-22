"""
生徒モデル
ステータス: enrolled(在籍) / trial(体験) / on_leave(休会) / withdrawn(退会)
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)

    # 学年: 1=小1, 6=小6, 7=中1, 9=中3, 10=高1, 12=高3
    grade = Column(Integer, nullable=False)
    school = Column(String(200), nullable=True)

    # 在籍学校区分: 公立 / 私立 / 国立
    school_type = Column(String(10), nullable=True)

    # 顔写真 (base64エンコード)
    photo_data = Column(Text, nullable=True)

    # 会員番号 (2から始まる10桁)
    member_number = Column(String(10), nullable=True, index=True)

    # 基本属性 (システム連携)
    gender = Column(String(4), nullable=True)            # 男 / 女
    parent_name = Column(String(100), nullable=True)     # 保護者氏名
    sibling_info = Column(Text, nullable=True)           # 兄弟姉妹情報

    # 在籍ステータス
    status = Column(String(20), nullable=False, default="enrolled")

    enrolled_at = Column(Date, nullable=True)   # 入会日
    trial_at = Column(Date, nullable=True)       # 体験日
    withdrawn_at = Column(Date, nullable=True)   # 退会日

    # 担当講師 (旧: 単一。複数担当は student_teachers 経由)
    assigned_teacher_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # 所属クラス (集団部門のみ。個別・自立はNull)
    class_group_id = Column(Integer, ForeignKey("class_groups.id"), nullable=True)

    # 所属教室
    classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # リレーション
    assigned_teacher = relationship("User", back_populates="assigned_students",
                                    foreign_keys=[assigned_teacher_id])
    classroom = relationship("Classroom", back_populates="students")
    class_group = relationship("ClassGroup", back_populates="students")
    teachers = relationship("User", secondary="student_teachers",
                            back_populates="responsible_students")
    enrollment_events = relationship("EnrollmentEvent", back_populates="student",
                                     order_by="EnrollmentEvent.occurred_at")
    enrollments = relationship("Enrollment", back_populates="student")
    attendances = relationship("Attendance", back_populates="student",
                               order_by="Attendance.class_date.desc()")
    room_logs = relationship("RoomLog", back_populates="student")
    homeworks = relationship("Homework", back_populates="student")
    test_scores = relationship("TestScore", back_populates="student")
    target_schools = relationship("TargetSchool", back_populates="student")
    school_grades = relationship("SchoolGrade", back_populates="student")
    payments = relationship("Payment", back_populates="student",
                            order_by="Payment.paid_at.desc()")
    parent_contacts = relationship("ParentContact", back_populates="student",
                                   order_by="ParentContact.occurred_at.desc()")
    sales_actions = relationship("SalesAction", back_populates="student",
                                 order_by="SalesAction.actioned_at.desc()")
    staff_notes = relationship("StaffNote", back_populates="student",
                               order_by="StaffNote.occurred_at.desc()")
    video_lesson_logs = relationship("VideoLessonLog", back_populates="student",
                                     order_by="VideoLessonLog.viewed_at.desc()")
    # 詳細ページ用の追加情報
    phones = relationship("StudentPhone", back_populates="student",
                          order_by="StudentPhone.position", cascade="all, delete-orphan")
    special_notes = relationship("SpecialNote", back_populates="student",
                                 order_by="SpecialNote.created_at.desc()",
                                 cascade="all, delete-orphan")
    profile_memos = relationship("ProfileMemo", back_populates="student",
                                 order_by="ProfileMemo.created_at.desc()",
                                 cascade="all, delete-orphan")
    parent_requests = relationship("ParentRequest", back_populates="student",
                                   order_by="ParentRequest.occurred_at.desc()",
                                   cascade="all, delete-orphan")
    exam_certifications = relationship("ExamCertification", back_populates="student",
                                       order_by="ExamCertification.exam_date.desc()",
                                       cascade="all, delete-orphan")
    referrals_made = relationship("Referral", foreign_keys="Referral.referrer_student_id",
                                  back_populates="referrer")
    referrals_received = relationship("Referral", foreign_keys="Referral.referred_student_id",
                                      back_populates="referred")
