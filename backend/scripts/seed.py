"""
シードデータ生成スクリプト
Faker(ja_JP, seed=42) でリアルな日本語ダミーデータを生成する

使用方法:
  python scripts/seed.py          # 既存データがあればスキップ
  python scripts/seed.py --force  # 強制的に全データを削除して再生成
"""

import os
import sys
import argparse
import random
from datetime import date, datetime, timedelta
from pathlib import Path

# バックエンドディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from faker import Faker
from sqlalchemy.orm import Session

from app.database import SessionLocal, engine
from app.models import (
    Classroom, User, Course, Student,
    ClassGroup, class_teachers, student_teachers,
    StudentPhone, SpecialNote, ProfileMemo, ParentRequest, Referral, ExamCertification,
    EnrollmentEvent, Enrollment,
    Attendance, RoomLog,
    Homework,
    TestScore, TargetSchool, SchoolGrade,
    Payment, ParentContact,
    SalesAction, SalesGoal,
    StaffNote, VideoLessonLog,
)
from app.database import Base
from app.services.auth_service import hash_password

# 再現性のある乱数シード
fake = Faker('ja_JP')
Faker.seed(42)
random.seed(42)

# ====================
# 定数
# ====================
SUBJECTS = ["国語", "数学", "英語", "理科", "社会"]
TEST_SESSIONS = [
    {"test_id": "2024-09", "test_name": "2024年9月模試", "test_date": date(2024, 9, 15)},
    {"test_id": "2024-11", "test_name": "2024年11月模試", "test_date": date(2024, 11, 17)},
    {"test_id": "2025-01", "test_name": "2025年1月模試", "test_date": date(2025, 1, 19)},
    {"test_id": "2025-03", "test_name": "2025年3月模試", "test_date": date(2025, 3, 16)},
]

# 学校名プール (仮想)
SCHOOLS = [
    "桜木中学校", "緑ヶ丘中学校", "東光中学校", "北星中学校", "南岡中学校",
    "第一中学校", "第二中学校", "城南中学校", "港南中学校", "西丘中学校",
    "光陵高等学校", "翠嵐高等学校", "希望ヶ丘高等学校", "横浜翠陵高等学校", "湘南高等学校",
]

SCHOOL_TYPES = ["公立", "私立", "国立"]
SCHOOL_TYPE_WEIGHTS = [0.65, 0.30, 0.05]  # 公立65%・私立30%・国立5%

# 部門 × コース種別の定義
DIVISION_COURSE_TYPES = {
    "集団": ["低学年", "中学受験（国私立）", "中学受験（公立中高一貫）", "高校受験", "大学受験"],
    "個別": ["中学受験", "高校受験", "大学受験"],
    "自立": ["映像", "速読", "Lepton英語", "学研教室"],
}

VIDEO_LESSON_CATEGORIES = ["国語", "数学", "英語", "理科", "社会", "総合"]
NOTE_TYPES = ["電話報告", "保護者面談", "生徒ミーティング", "その他"]

# クラス定義 (集団部門。中1〜中3。レベル G/R=標準, L/D=応用, T=難関)
CLASS_DEFS = [
    ("1G-1", 7, "標準", 1), ("1G-2", 7, "標準", 2), ("1L-1", 7, "応用", 3), ("1L-2", 7, "応用", 4), ("1T-1", 7, "難関", 5),
    ("2G-1", 8, "標準", 11), ("2G-2", 8, "標準", 12), ("2L-1", 8, "応用", 13), ("2L-2", 8, "応用", 14), ("2T-1", 8, "難関", 15),
    ("3R-1", 9, "標準", 21), ("3R-2", 9, "標準", 22), ("3D-1", 9, "応用", 23), ("3D-2", 9, "応用", 24), ("3T-1", 9, "難関", 25),
]

GENDERS = ["男", "女"]

# 試験種別ごとのセッション定義 (test_id, test_name, 月日(year,month,day))
INTERNAL_TEST_A = [  # 塾内試験A
    ("juku-a-2024-10", "塾内試験A 第3回", (2024, 10, 5)),
    ("juku-a-2024-12", "塾内試験A 第4回", (2024, 12, 7)),
    ("juku-a-2025-02", "塾内試験A 第5回", (2025, 2, 8)),
]
INTERNAL_TEST_B = [  # 塾内試験B
    ("juku-b-2024-10", "塾内試験B 第3回", (2024, 10, 19)),
    ("juku-b-2024-12", "塾内試験B 第4回", (2024, 12, 21)),
    ("juku-b-2025-02", "塾内試験B 第5回", (2025, 2, 22)),
]
VENDOR_TEST_A = [  # 業者模試A (旧 TEST_SESSIONS 相当)
    ("gyosha-a-2024-09", "業者模試A 9月", (2024, 9, 15)),
    ("gyosha-a-2024-11", "業者模試A 11月", (2024, 11, 17)),
    ("gyosha-a-2025-01", "業者模試A 1月", (2025, 1, 19)),
]
VENDOR_TEST_B = [  # 業者模試B
    ("gyosha-b-2024-10", "業者模試B 10月", (2024, 10, 13)),
    ("gyosha-b-2025-01", "業者模試B 1月", (2025, 1, 26)),
]

# 学校定期テスト (2期制 / 3期制)
TERM_TESTS_2 = [  # 2期制
    ("teiki-2024-zenki-chukan", "前期中間", (2024, 5, 23)),
    ("teiki-2024-zenki-kimatsu", "前期期末", (2024, 6, 27)),
    ("teiki-2024-koki-chukan", "後期中間", (2024, 11, 21)),
    ("teiki-2024-koki-kimatsu", "後期期末", (2025, 2, 20)),
]
TERM_TESTS_3 = [  # 3期制
    ("teiki-2024-1-chukan", "1学期中間", (2024, 5, 23)),
    ("teiki-2024-1-kimatsu", "1学期期末", (2024, 6, 27)),
    ("teiki-2024-2-chukan", "2学期中間", (2024, 10, 10)),
    ("teiki-2024-2-kimatsu", "2学期期末", (2024, 11, 28)),
    ("teiki-2024-3-kimatsu", "3学期期末", (2025, 2, 27)),
]

# 英検・漢検の級
EIKEN_LEVELS = ["5級", "4級", "3級", "準2級", "準2級プラス", "2級", "準1級", "1級"]
KANKEN_LEVELS = ["10級", "9級", "8級", "7級", "6級", "5級", "4級", "3級", "準2級", "2級", "準1級", "1級"]

# プロフィール定型メモのカテゴリ
PROFILE_CATEGORIES = ["部活動", "習い事", "家族構成", "家族の職業・学年", "通学校情報"]
PROFILE_SAMPLES = {
    "部活動": ["サッカー部（火・木・土）", "吹奏楽部（月・水・金・土）", "バスケ部（平日毎日）", "美術部（週2回）", "帰宅部"],
    "習い事": ["ピアノ（水曜）", "水泳（土曜）", "英会話（金曜）", "書道（月曜）", "なし"],
    "家族構成": ["父・母・本人・妹", "母・本人・弟", "父・母・兄・本人", "父・母・本人（一人っ子）"],
    "家族の職業・学年": ["父：会社員 / 母：パート", "父：自営業 / 母：看護師", "兄：高2 / 本人：中2", "姉：大学1年"],
    "通学校情報": ["駅から徒歩10分。給食あり。", "私服通学。土曜授業あり。", "2期制。定期テスト年4回。", "3期制。部活が盛ん。"],
}

# 特記事項
SPECIAL_NOTE_SAMPLES = [
    ("高", "アレルギーあり（そば）。教室での飲食に注意。"),
    ("高", "保護者が離婚協議中。連絡は母のみに。"),
    ("中", "人見知りが強い。少人数対応が望ましい。"),
    ("中", "兄が当塾OB。難関校志望で意識が高い。"),
    ("低", "送迎は基本的に祖母。"),
    ("低", "本人の希望で席は前方固定。"),
]

# 保護者要望・クレーム
PARENT_REQUEST_SAMPLES = {
    "要望": [
        "数学の補習を増やしてほしい。",
        "面談の頻度を上げてほしい。",
        "宿題の量を調整してほしい。",
        "志望校の最新情報を共有してほしい。",
    ],
    "クレーム": [
        "教室が騒がしいとのこと。改善要望。",
        "請求金額に誤りがあるとの指摘。",
        "担当講師の変更を希望。",
    ],
}

# スタッフ記録のハッシュタグ候補
STAFF_NOTE_TAGS = ["#成績", "#面談", "#欠席", "#志望校", "#宿題", "#モチベーション", "#保護者対応", "#進路", "#要フォロー"]

# 欠席時フォロー種別
MAKEUP_TYPES = ["映像視聴", "振替"]

CONTACT_TYPES = ["電話報告", "面談", "保護者会", "テキスト報告", "メール"]
ACTION_TYPES = ["trial_invitation", "phone_follow", "dm_campaign", "visit"]
ACTION_TYPE_LABELS = {
    "trial_invitation": "体験招待",
    "phone_follow": "電話フォロー",
    "dm_campaign": "DMキャンペーン",
    "visit": "来塾案内",
}


def clear_all_tables(db: Session):
    """全テーブルのデータを削除 (FK制約を考慮した逆順)"""
    print("全テーブルをクリア中...")
    # 多対多の関連テーブルを先に削除
    db.execute(student_teachers.delete())
    db.execute(class_teachers.delete())
    db.query(Referral).delete()
    db.query(ExamCertification).delete()
    db.query(ParentRequest).delete()
    db.query(ProfileMemo).delete()
    db.query(SpecialNote).delete()
    db.query(StudentPhone).delete()
    db.query(VideoLessonLog).delete()
    db.query(StaffNote).delete()
    db.query(SalesGoal).delete()
    db.query(SalesAction).delete()
    db.query(ParentContact).delete()
    db.query(Payment).delete()
    db.query(SchoolGrade).delete()
    db.query(TargetSchool).delete()
    db.query(TestScore).delete()
    db.query(Homework).delete()
    db.query(RoomLog).delete()
    db.query(Attendance).delete()
    db.query(Enrollment).delete()
    db.query(EnrollmentEvent).delete()
    db.query(Student).delete()
    db.query(ClassGroup).delete()
    db.query(Course).delete()
    db.query(User).delete()
    db.query(Classroom).delete()
    db.commit()
    print("クリア完了")


def seed_classroom(db: Session) -> Classroom:
    """教室を1つ作成"""
    classroom = Classroom(name="学習塾サンプル校", address="東京都渋谷区1-1-1")
    db.add(classroom)
    db.flush()
    return classroom


def seed_users(db: Session, classroom: Classroom) -> dict:
    """
    ユーザーを作成:
    - admin: 1名
    - room_manager: 1名 (教室長)
    - teacher: 6名
    - parttime: 2名
    """
    users = {}

    # 管理者
    admin = User(
        name="山田 太郎",
        email="admin@example.com",
        password_hash=hash_password("password"),
        role="admin",
        classroom_id=classroom.id,
    )
    db.add(admin)
    db.flush()
    users["admin"] = admin

    # 教室長
    room_manager = User(
        name="鈴木 花子",
        email="manager@example.com",
        password_hash=hash_password("password"),
        role="room_manager",
        classroom_id=classroom.id,
    )
    db.add(room_manager)
    db.flush()
    users["room_manager"] = room_manager

    # 講師6名
    teachers = []
    teacher_names = [
        ("佐藤 誠", "teacher1@example.com"),
        ("田中 美咲", "teacher2@example.com"),
        ("伊藤 健太", "teacher3@example.com"),
        ("渡辺 由美", "teacher4@example.com"),
        ("小林 浩二", "teacher5@example.com"),
        ("加藤 愛子", "teacher6@example.com"),
    ]
    for name, email in teacher_names:
        t = User(
            name=name,
            email=email,
            password_hash=hash_password("password"),
            role="teacher",
            classroom_id=classroom.id,
        )
        db.add(t)
        db.flush()
        teachers.append(t)
    users["teachers"] = teachers

    # アルバイト2名
    parttimers = []
    for i, (name, email) in enumerate([("中村 翔", "part1@example.com"), ("木村 なな", "part2@example.com")]):
        p = User(
            name=name,
            email=email,
            password_hash=hash_password("password"),
            role="parttime",
            classroom_id=classroom.id,
        )
        db.add(p)
        db.flush()
        parttimers.append(p)
    users["parttimers"] = parttimers

    return users


def seed_courses(db: Session) -> list:
    """講座を部門×種別で作成"""
    course_data = [
        # 集団部門
        ("集団-高校受験コース",   "総合",   "集団", "高校受験"),
        ("集団-大学受験コース",   "総合",   "集団", "大学受験"),
        ("集団-中学受験（国私立）コース", "総合", "集団", "中学受験（国私立）"),
        ("集団-中学受験（公立中高一貫）コース", "総合", "集団", "中学受験（公立中高一貫）"),
        ("集団-低学年コース",     "総合",   "集団", "低学年"),
        # 個別部門
        ("個別-高校受験コース",   "総合",   "個別", "高校受験"),
        ("個別-大学受験コース",   "総合",   "個別", "大学受験"),
        ("個別-中学受験コース",   "総合",   "個別", "中学受験"),
        # 自立部門
        ("自立-映像授業",         "総合",   "自立", "映像"),
        ("自立-速読",             "国語",   "自立", "速読"),
        ("自立-Lepton英語",       "英語",   "自立", "Lepton英語"),
        ("自立-学研教室",         "総合",   "自立", "学研教室"),
    ]
    courses = []
    for name, subject, division, course_type in course_data:
        c = Course(
            name=name, subject=subject,
            division=division, course_type=course_type,
        )
        db.add(c)
        db.flush()
        courses.append(c)
    return courses


def seed_class_groups(db: Session, classroom: Classroom, users: dict) -> list:
    """クラス(集団部門の組分け)を作成し、各クラスに担当講師1〜2名を割り当てる"""
    teachers = users["teachers"]
    class_groups = []
    for idx, (name, grade, level, sort_order) in enumerate(CLASS_DEFS):
        cg = ClassGroup(
            name=name, grade=grade, level=level,
            sort_order=sort_order, classroom_id=classroom.id,
        )
        db.add(cg)
        db.flush()
        # 担当講師1〜2名 (難関クラスは2名)
        n_teachers = 2 if level == "難関" else random.randint(1, 2)
        assigned = random.sample(teachers, k=min(n_teachers, len(teachers)))
        cg.teachers = assigned
        class_groups.append(cg)
    db.flush()
    return class_groups


def _generate_member_number(idx: int) -> str:
    """2から始まる10桁の会員番号を生成 (連番ベースで一意)"""
    return f"2{(100000000 + idx):09d}"[:10]


def seed_students(db: Session, classroom: Classroom, users: dict, courses: list,
                  class_groups: list) -> list:
    """
    生徒80名を作成:
    - enrolled: 60名 (うち15名はat-risk設定)
    - on_leave: 10名
    - withdrawn: 10名
    """
    teachers = users["teachers"]
    students = []

    # 生徒プロファイルを定義
    profiles = []

    # 在籍60名
    for i in range(60):
        is_atrisk = i < 15  # 最初の15名はat-risk
        is_declining = i < 10  # 最初の10名は成績下降

        # 学年分布: 中学生45名、高校生15名
        if i < 45:
            grade = random.randint(7, 9)  # 中1-中3
        else:
            grade = random.randint(10, 12)  # 高1-高3

        profiles.append({
            "status": "enrolled",
            "grade": grade,
            "is_atrisk": is_atrisk,
            "is_declining": is_declining,
        })

    # 休会10名
    for i in range(10):
        profiles.append({
            "status": "on_leave",
            "grade": random.randint(7, 12),
            "is_atrisk": False,
            "is_declining": False,
        })

    # 退会10名
    for i in range(10):
        profiles.append({
            "status": "withdrawn",
            "grade": random.randint(7, 12),
            "is_atrisk": False,
            "is_declining": False,
        })

    today = date.today()
    base_enrolled_date = today - timedelta(days=365)

    for idx, profile in enumerate(profiles):
        grade = profile["grade"]
        status = profile["status"]

        # 入会日・体験日
        trial_at = base_enrolled_date - timedelta(days=random.randint(10, 30))
        enrolled_at = base_enrolled_date + timedelta(days=random.randint(0, 60))
        withdrawn_at = None

        if status == "withdrawn":
            withdrawn_at = today - timedelta(days=random.randint(30, 180))
            enrolled_at = withdrawn_at - timedelta(days=random.randint(90, 365))
            trial_at = enrolled_at - timedelta(days=random.randint(7, 21))
        elif status == "on_leave":
            enrolled_at = base_enrolled_date - timedelta(days=random.randint(30, 180))

        # 担当講師をランダムに割り当て (代表1名。複数担当は後で設定)
        teacher = random.choice(teachers)

        # 学校名・学校区分
        school = random.choice(SCHOOLS)
        school_type = random.choices(SCHOOL_TYPES, weights=SCHOOL_TYPE_WEIGHTS)[0]
        gender = random.choice(GENDERS)

        student = Student(
            name=fake.name(),
            grade=grade,
            school=school,
            school_type=school_type,
            gender=gender,
            parent_name=fake.last_name() + " " + fake.first_name(),
            sibling_info=random.choice([
                "弟（小4・当塾在籍）", "姉（高2・他塾）", "一人っ子", "兄（大学生）", "妹（小2）",
            ]),
            member_number=_generate_member_number(idx),
            status=status,
            enrolled_at=enrolled_at,
            trial_at=trial_at,
            withdrawn_at=withdrawn_at,
            assigned_teacher_id=teacher.id,
            classroom_id=classroom.id,
        )
        db.add(student)
        db.flush()

        # 入退会イベント
        _seed_enrollment_events(db, student)

        # 受講講座 (在籍・休会生徒のみ) → 受講部門を取得
        selected_divisions = []
        if status in ["enrolled", "on_leave"]:
            selected_divisions = _seed_enrollments(db, student, courses)

        # クラス所属 & 複数担当講師の割り当て
        _assign_class_and_teachers(db, student, selected_divisions, class_groups, teachers)

        # 詳細ページ用の追加情報
        _seed_phones(db, student)
        _seed_special_notes(db, student)
        _seed_profile_memos(db, student)
        _seed_parent_requests(db, student)
        _seed_exam_certs(db, student)

        # 出欠データ
        _seed_attendances(db, student, profile)

        # 入退室ログ
        _seed_room_logs(db, student, profile)

        # 宿題
        _seed_homeworks(db, student, teachers)

        # テスト成績
        _seed_test_scores(db, student, profile)

        # 志望校
        _seed_target_schools(db, student)

        # 学校成績
        _seed_school_grades(db, student)

        # 支払い
        _seed_payments(db, student)

        # 保護者コンタクト
        _seed_parent_contacts(db, student, teachers)

        # スタッフ記録 (在籍・休会のみ)
        if status in ["enrolled", "on_leave"]:
            _seed_staff_notes(db, student, teachers)

        # 映像授業ログ (自立部門受講生のみ)
        if status == "enrolled":
            _seed_video_logs(db, student)

        students.append({"student": student, "profile": profile})

    return students


def _seed_enrollment_events(db: Session, student: Student):
    """入退会イベントを生成"""
    events = []

    # 資料請求
    if random.random() < 0.7:
        events.append(EnrollmentEvent(
            student_id=student.id,
            event_type="資料請求",
            occurred_at=datetime.combine(student.trial_at - timedelta(days=14), datetime.min.time()),
            note="HPから資料請求",
        ))

    # 体験
    if student.trial_at:
        events.append(EnrollmentEvent(
            student_id=student.id,
            event_type="体験",
            occurred_at=datetime.combine(student.trial_at, datetime.min.time()),
            note="体験授業参加",
        ))

    # 入会テスト受験 (点数を記録)
    if student.trial_at:
        nyukai_score = random.randint(40, 95)
        events.append(EnrollmentEvent(
            student_id=student.id,
            event_type="入会テスト受験",
            occurred_at=datetime.combine(student.trial_at + timedelta(days=2), datetime.min.time()),
            note=f"入会テスト {nyukai_score}点",
        ))

    # 入会
    if student.enrolled_at:
        events.append(EnrollmentEvent(
            student_id=student.id,
            event_type="入会",
            occurred_at=datetime.combine(student.enrolled_at, datetime.min.time()),
            note="正式入会",
        ))

    # 季節講習受講 (在籍生のみランダム)
    if student.status in ["enrolled", "on_leave"] and student.enrolled_at:
        for season, ymd in [("夏期講習", (2024, 7, 25)), ("冬期講習", (2024, 12, 24))]:
            if random.random() < 0.7:
                events.append(EnrollmentEvent(
                    student_id=student.id,
                    event_type="季節講習受講",
                    occurred_at=datetime.combine(date(*ymd), datetime.min.time()),
                    note=f"{season}を受講",
                ))
        # イベント参加
        if random.random() < 0.5:
            events.append(EnrollmentEvent(
                student_id=student.id,
                event_type="イベント参加",
                occurred_at=datetime.combine(date.today() - timedelta(days=random.randint(20, 150)), datetime.min.time()),
                note=random.choice(["保護者会", "進路説明会", "勉強合宿", "定期面談会"]),
            ))

    # 休会・退会
    if student.status == "on_leave":
        events.append(EnrollmentEvent(
            student_id=student.id,
            event_type="休会",
            occurred_at=datetime.combine(date.today() - timedelta(days=30), datetime.min.time()),
            note="本人都合による休会",
        ))
    elif student.status == "withdrawn" and student.withdrawn_at:
        events.append(EnrollmentEvent(
            student_id=student.id,
            event_type="退会",
            occurred_at=datetime.combine(student.withdrawn_at, datetime.min.time()),
            note="退会申請による",
        ))

    for e in events:
        db.add(e)


def _seed_enrollments(db: Session, student: Student, courses: list):
    """受講講座を部門ごとに設定（1〜2部門を受講）"""
    # 学年に応じた利用可能コース
    def course_for_grade(division: str) -> list:
        pool = [c for c in courses if c.division == division]
        if student.grade <= 6:
            types = ["低学年"]
        elif student.grade <= 9:
            types = ["中学受験（国私立）", "中学受験（公立中高一貫）", "高校受験", "中学受験"]
        else:
            types = ["高校受験", "大学受験"]
        filtered = [c for c in pool if c.course_type in types]
        return filtered if filtered else pool

    # ランダムに1〜2部門選択。高校生は集団部門なし。
    if student.grade >= 10:
        all_divisions = ["個別", "自立"]
    else:
        all_divisions = ["集団", "個別", "自立"]
    selected_divisions = random.sample(all_divisions, k=random.randint(1, min(2, len(all_divisions))))

    started = student.enrolled_at or date.today() - timedelta(days=180)
    for division in selected_divisions:
        pool = course_for_grade(division)
        if not pool:
            continue
        course = random.choice(pool)
        e = Enrollment(
            student_id=student.id,
            course_id=course.id,
            started_at=started,
            ended_at=student.withdrawn_at,
            change_type="新規",
        )
        db.add(e)

    return selected_divisions


def _assign_class_and_teachers(db: Session, student: Student, selected_divisions: list,
                               class_groups: list, teachers: list):
    """
    集団部門 & 中学生ならクラスに所属させ、クラス担当講師を担当に設定。
    それ以外は個別に1〜2名の担当講師を設定。
    """
    assigned_teachers = []

    if "集団" in selected_divisions and 7 <= student.grade <= 9:
        candidates = [cg for cg in class_groups if cg.grade == student.grade]
        if candidates:
            cg = random.choice(candidates)
            student.class_group_id = cg.id
            assigned_teachers = list(cg.teachers)

    # 集団でない、またはクラス講師が空の場合は個別担当を設定
    if not assigned_teachers:
        n = random.randint(1, 2)
        assigned_teachers = random.sample(teachers, k=min(n, len(teachers)))

    # 代表担当 + 複数担当
    student.assigned_teacher_id = assigned_teachers[0].id if assigned_teachers else student.assigned_teacher_id
    student.teachers = assigned_teachers
    db.flush()


def _seed_phones(db: Session, student: Student):
    """電話番号を1〜3件生成 (番号は連携、メモは手入力イメージ)"""
    memos = ["父の携帯", "母の携帯", "自宅", "祖母の携帯", "本人の携帯"]
    n = random.randint(1, 3)
    selected_memos = random.sample(memos, k=n)
    for pos, memo in enumerate(selected_memos):
        db.add(StudentPhone(
            student_id=student.id,
            phone_number=fake.phone_number(),
            memo=memo,
            position=pos,
        ))


def _seed_special_notes(db: Session, student: Student):
    """特記事項を0〜2件生成"""
    n = random.randint(0, 2)
    for importance, content in random.sample(SPECIAL_NOTE_SAMPLES, k=min(n, len(SPECIAL_NOTE_SAMPLES))):
        db.add(SpecialNote(student_id=student.id, importance=importance, content=content))


def _seed_profile_memos(db: Session, student: Student):
    """プロフィール定型メモをカテゴリ別に生成"""
    for category in random.sample(PROFILE_CATEGORIES, k=random.randint(2, len(PROFILE_CATEGORIES))):
        db.add(ProfileMemo(
            student_id=student.id,
            category=category,
            content=random.choice(PROFILE_SAMPLES[category]),
        ))


def _seed_parent_requests(db: Session, student: Student):
    """保護者要望・クレームを0〜2件生成"""
    today = date.today()
    n = random.randint(0, 2)
    for _ in range(n):
        req_type = random.choices(["要望", "クレーム"], weights=[0.75, 0.25])[0]
        db.add(ParentRequest(
            student_id=student.id,
            request_type=req_type,
            content=random.choice(PARENT_REQUEST_SAMPLES[req_type]),
            status=random.choice(["対応中", "対応済"]),
            occurred_at=datetime.combine(today - timedelta(days=random.randint(5, 200)), datetime.min.time()),
        ))


def _seed_exam_certs(db: Session, student: Student):
    """英検・漢検の取得履歴を生成"""
    today = date.today()
    # 英検: 0〜3件 (受験予定含む)
    n_eiken = random.randint(0, 3)
    # 学年が上がるほど高い級を取りやすいよう開始位置を調整
    base = min(student.grade - 6, len(EIKEN_LEVELS) - 2)
    base = max(0, base)
    for i in range(n_eiken):
        lvl_idx = min(base + i, len(EIKEN_LEVELS) - 1)
        is_future = (i == n_eiken - 1) and random.random() < 0.3
        db.add(ExamCertification(
            student_id=student.id,
            exam_type="英検",
            level=EIKEN_LEVELS[lvl_idx],
            score=random.randint(1000, 2300) if not is_future else None,
            result="受験予定" if is_future else random.choices(["合格", "不合格"], weights=[0.8, 0.2])[0],
            exam_date=today - timedelta(days=random.randint(30, 600)) if not is_future else today + timedelta(days=random.randint(10, 60)),
        ))
    # 漢検: 0〜2件
    n_kanken = random.randint(0, 2)
    kbase = max(0, min(student.grade - 4, len(KANKEN_LEVELS) - 2))
    for i in range(n_kanken):
        lvl_idx = min(kbase + i, len(KANKEN_LEVELS) - 1)
        db.add(ExamCertification(
            student_id=student.id,
            exam_type="漢検",
            level=KANKEN_LEVELS[lvl_idx],
            score=random.randint(120, 200),
            result=random.choices(["合格", "不合格"], weights=[0.85, 0.15])[0],
            exam_date=today - timedelta(days=random.randint(30, 600)),
        ))


def _seed_attendances(db: Session, student: Student, profile: dict):
    """過去6ヶ月の出欠データを生成"""
    today = date.today()
    start = today - timedelta(days=180)

    # at-risk生徒は出席率45-60%、通常は85-95%
    if profile.get("is_atrisk"):
        present_rate = random.uniform(0.45, 0.60)
    elif student.status == "withdrawn":
        # 退会生徒は徐々に欠席が増える
        present_rate = random.uniform(0.60, 0.75)
    else:
        present_rate = random.uniform(0.85, 0.95)

    # 授業は週3回 (月水金) と仮定
    current = start
    while current <= today:
        if current.weekday() in [0, 2, 4]:  # 月水金
            # 退会済み生徒は退会日以降のデータなし
            if student.withdrawn_at and current > student.withdrawn_at:
                current += timedelta(days=1)
                continue

            rand = random.random()
            makeup_type = None
            makeup_note = None
            if rand < present_rate:
                status = "present"
            elif rand < present_rate + 0.05:
                status = "late"
            else:
                status = "absent"
                # 欠席の約6割は映像視聴または振替でフォロー
                r = random.random()
                if r < 0.35:
                    makeup_type = "映像視聴"
                    makeup_note = f"{random.choice(VIDEO_LESSON_CATEGORIES)}_{random.randint(1,50):02d}講 を視聴"
                elif r < 0.60:
                    makeup_type = "振替"
                    makeup_note = f"{random.choice(['翌週','別曜日','土曜'])}クラスへ振替"

            att = Attendance(
                student_id=student.id,
                class_date=current,
                status=status,
                note="無断欠席" if status == "absent" and makeup_type is None and random.random() < 0.3 else None,
                makeup_type=makeup_type,
                makeup_note=makeup_note,
            )
            db.add(att)

        current += timedelta(days=1)


def _seed_room_logs(db: Session, student: Student, profile: dict):
    """直近30日の入退室ログを生成"""
    today = date.today()
    for days_ago in range(30, 0, -1):
        log_date = today - timedelta(days=days_ago)
        if log_date.weekday() in [0, 2, 4] and random.random() < 0.8:
            entered = datetime.combine(log_date, datetime.strptime("15:30", "%H:%M").time())
            exited = entered + timedelta(hours=random.randint(1, 3))
            log = RoomLog(
                student_id=student.id,
                entered_at=entered,
                exited_at=exited,
            )
            db.add(log)


def _seed_homeworks(db: Session, student: Student, teachers: list):
    """過去3ヶ月の宿題データを生成"""
    today = date.today()
    start = today - timedelta(days=90)
    current = start
    while current <= today:
        if current.weekday() in [0, 2, 4]:
            if student.withdrawn_at and current > student.withdrawn_at:
                current += timedelta(days=1)
                continue
            submitted = None
            if random.random() < 0.75:  # 75%提出率
                submitted = datetime.combine(current + timedelta(days=random.randint(1, 3)), datetime.min.time())
            hw = Homework(
                student_id=student.id,
                assigned_date=current,
                submitted_at=submitted,
                checked_by=random.choice(teachers).id if submitted else None,
            )
            db.add(hw)
        current += timedelta(days=1)


def _seed_test_scores(db: Session, student: Student, profile: dict):
    """
    複数の試験種別ごとに成績を生成:
    塾内試験A/B, 業者模試A/B, 学校定期テスト(2期 or 3期)
    """
    # 基準スコア (生徒ごとにランダム)
    base_scores = {s: max(20, min(100, random.gauss(65, 15))) for s in SUBJECTS}
    # 成績下降フラグがある生徒は特定科目で連続下降を設定
    declining_subjects = random.sample(SUBJECTS, 2) if profile.get("is_declining") else []

    # 学校定期テストは2期制 or 3期制をランダムに割り当て
    term_sessions = random.choice([TERM_TESTS_2, TERM_TESTS_3])

    test_groups = [
        ("塾内試験A", INTERNAL_TEST_A, True),
        ("塾内試験B", INTERNAL_TEST_B, True),
        ("業者模試A", VENDOR_TEST_A, True),
        ("業者模試B", VENDOR_TEST_B, True),
        ("学校定期テスト", term_sessions, False),  # 定期テストは偏差値・順位なし
    ]

    for test_type, sessions, has_deviation in test_groups:
        # 試験種別ごとの平均オフセット (難易度差を表現)
        type_offset = {
            "塾内試験A": 0, "塾内試験B": -3, "業者模試A": -5, "業者模試B": -4, "学校定期テスト": 8,
        }.get(test_type, 0)

        for session_idx, (test_id, test_name, ymd) in enumerate(sessions):
            test_date = date(*ymd)
            if student.withdrawn_at and test_date > student.withdrawn_at:
                continue

            for subject in SUBJECTS:
                score = base_scores[subject] + type_offset
                if subject in declining_subjects:
                    score -= (session_idx + 1) * random.uniform(5, 10)
                else:
                    score += random.gauss(0, 5)
                score = max(10, min(100, score))

                deviation = None
                rank = None
                if has_deviation:
                    deviation = round(max(20, min(80, 50 + (score - 65) / 12 * 10)), 1)
                    rank = random.randint(1, 80)

                ts = TestScore(
                    student_id=student.id,
                    test_id=test_id,
                    test_name=test_name,
                    test_type=test_type,
                    subject=subject,
                    raw_score=round(score, 1),
                    rank=rank,
                    deviation_value=deviation,
                    test_date=test_date,
                    item_results={"correct": random.randint(5, 20), "total": 20},
                )
                db.add(ts)


def _seed_target_schools(db: Session, student: Student):
    """志望校を1〜3校設定"""
    # 高校生のみ有意義なデータ
    if student.grade >= 10:
        target_schools = [
            "東京大学", "京都大学", "早稲田大学", "慶應義塾大学", "上智大学",
            "明治大学", "青山学院大学", "立教大学", "中央大学", "法政大学",
        ]
    else:
        target_schools = [
            "桜丘高等学校", "緑丘高等学校", "東光高等学校", "北星高等学校", "南丘高等学校",
        ]

    count = random.randint(1, 3)
    selected = random.sample(target_schools, min(count, len(target_schools)))
    for priority, school_name in enumerate(selected, 1):
        ts = TargetSchool(
            student_id=student.id,
            school_name=school_name,
            priority=priority,
            recorded_at=date.today() - timedelta(days=random.randint(30, 180)),
        )
        db.add(ts)


def _seed_school_grades(db: Session, student: Student):
    """学校の成績を2学期分設定"""
    terms = ["2024-前期", "2024-後期"]
    for term in terms:
        for subject in SUBJECTS:
            score = round(random.gauss(3.5, 0.8), 0)
            score = max(1, min(5, score))
            sg = SchoolGrade(
                student_id=student.id,
                term=term,
                subject=subject,
                score=score,
                grade_notation=str(int(score)),
            )
            db.add(sg)


def _seed_payments(db: Session, student: Student):
    """過去6ヶ月の支払い記録を生成"""
    today = date.today()
    for months_ago in range(6, 0, -1):
        payment_date = date(
            today.year if today.month > months_ago else today.year - 1,
            (today.month - months_ago) % 12 or 12,
            25,
        )

        # 退会後は支払いなし
        if student.withdrawn_at and payment_date > student.withdrawn_at:
            continue

        status = "paid" if random.random() < 0.95 else "pending"
        payment = Payment(
            student_id=student.id,
            amount=22000 + random.choice([0, 5500, 11000]),  # 授業料 + オプション
            paid_at=payment_date if status == "paid" else None,
            due_at=payment_date,
            category="授業料",
            status=status,
        )
        db.add(payment)


def _seed_parent_contacts(db: Session, student: Student, teachers: list):
    """2〜5件の保護者コンタクト記録を生成"""
    contact_count = random.randint(2, 5)
    today = date.today()

    summaries = {
        "電話報告": ["学習状況を報告。理解度は概ね良好。", "最近の欠席について確認。体調不良との回答。", "成績向上の報告。保護者も喜んでいた。"],
        "面談": ["学習目標について話し合い。志望校を確認。", "成績下降の対策を議論。追加授業を提案。", "次学期の受講講座について相談。"],
        "保護者会": ["定期保護者会にて学習状況を共有。", "春期講習の案内を実施。"],
        "テキスト報告": ["本日の授業内容と宿題を報告。", "テスト結果の報告を送付。"],
        "メール": ["夏期講習の案内メールを送付。", "模試結果の詳細を送付。"],
    }

    for _ in range(contact_count):
        contact_type = random.choice(CONTACT_TYPES)
        days_ago = random.randint(10, 150)
        occurred_at = datetime.combine(today - timedelta(days=days_ago), datetime.min.time())

        contact = ParentContact(
            student_id=student.id,
            contact_type=contact_type,
            occurred_at=occurred_at,
            summary=random.choice(summaries.get(contact_type, ["対応完了。"])),
            teacher_id=random.choice(teachers).id,
        )
        db.add(contact)


def _seed_staff_notes(db: Session, student: Student, teachers: list):
    """スタッフ記録を2〜4件生成"""
    today = date.today()
    note_contents = {
        "電話報告": [
            "保護者より電話。学習状況について確認。特に問題なし。",
            "保護者に成績向上を報告。次回模試への意欲も確認。",
            "欠席理由を確認。体調不良とのこと。補講を提案。",
        ],
        "保護者面談": [
            "志望校について保護者と面談。方針を共有した。",
            "成績下降について対策を話し合い。週1回補習を実施することになった。",
            "次学期の受講コースについて相談。追加受講を検討中。",
        ],
        "生徒ミーティング": [
            "学習目標の確認。本人もやる気を見せている。",
            "宿題の取り組み方について指導。改善の余地あり。",
            "模試結果を一緒に確認。苦手分野の特定ができた。",
        ],
        "その他": [
            "連絡帳にて学習状況を保護者に共有。",
            "スケジュール調整の連絡を受けた。",
        ],
    }

    count = random.randint(2, 4)
    for _ in range(count):
        note_type = random.choice(NOTE_TYPES)
        days_ago = random.randint(5, 120)
        occurred_at = datetime.combine(
            today - timedelta(days=days_ago),
            datetime.strptime(f"{random.randint(9,18)}:00", "%H:%M").time(),
        )
        note = StaffNote(
            student_id=student.id,
            teacher_id=random.choice(teachers).id,
            note_type=note_type,
            content=random.choice(note_contents[note_type]),
            tags=random.sample(STAFF_NOTE_TAGS, k=random.randint(1, 3)),
            occurred_at=occurred_at,
        )
        db.add(note)


def _seed_video_logs(db: Session, student: Student):
    """過去3ヶ月の映像授業視聴ログを生成（自立部門受講生のみ）"""
    # 自立部門受講かチェック
    has_jiritu = any(
        e.course and e.course.division == "自立"
        for e in student.enrollments
        if not e.ended_at
    )
    if not has_jiritu:
        return

    today = date.today()
    # 月2〜8回視聴
    view_count = random.randint(6, 24)
    for _ in range(view_count):
        days_ago = random.randint(1, 90)
        viewed_at = datetime.combine(
            today - timedelta(days=days_ago),
            datetime.strptime(f"{random.randint(14,20)}:{random.choice(['00','15','30','45'])}", "%H:%M").time(),
        )
        duration = round(random.uniform(20, 90), 1)
        completion = round(random.uniform(60, 100), 1)

        vl = VideoLessonLog(
            student_id=student.id,
            lesson_name=f"{random.choice(VIDEO_LESSON_CATEGORIES)}_{random.randint(1,50):02d}講",
            lesson_category=random.choice(VIDEO_LESSON_CATEGORIES),
            viewed_at=viewed_at,
            duration_minutes=duration,
            completion_rate=completion,
            source_system="映像授業システム",
        )
        db.add(vl)


def seed_sales(db: Session, students_data: list, users: dict):
    """
    夏期講習の営業目標と営業アクションを生成:
    - 目標: 45名
    - signed_up: 28名
    - in_progress: 10名
    - declined: 7名
    """
    admin = users["admin"]
    teachers = users["teachers"]

    # 営業目標を作成
    goal = SalesGoal(
        goal_type="trial_signup",
        target_product="夏期講習",
        target_count=45,
        period="2024-summer",
        created_by=admin.id,
    )
    db.add(goal)
    db.flush()

    # 在籍・体験中の生徒にアクション設定
    enrolled_students = [
        sd["student"] for sd in students_data
        if sd["student"].status in ["enrolled", "trial"]
    ]

    random.shuffle(enrolled_students)

    signed_up_count = 0
    in_progress_count = 0
    declined_count = 0

    for idx, student in enumerate(enrolled_students):
        if signed_up_count < 28:
            status = "signed_up"
            signed_up_count += 1
        elif in_progress_count < 10:
            status = "in_progress"
            in_progress_count += 1
        elif declined_count < 7:
            status = "declined"
            declined_count += 1
        else:
            status = "pending"

        days_ago = random.randint(5, 60)
        action = SalesAction(
            student_id=student.id,
            assigned_to=random.choice(teachers).id,
            action_type=random.choice(ACTION_TYPES),
            target_product="夏期講習",
            status=status,
            note=_make_action_note(status),
            actioned_at=datetime.combine(
                date.today() - timedelta(days=days_ago),
                datetime.min.time(),
            ),
        )
        db.add(action)


def _make_action_note(status: str) -> str:
    """アクション状況に応じたメモを生成"""
    notes = {
        "signed_up": ["夏期講習申込完了。入金確認済み。", "申込書受領。開講日を案内済み。"],
        "in_progress": ["電話にて案内済み。検討中とのこと。", "資料を郵送。折り返し待ち。"],
        "declined": ["家族の予定と重複するとのことで辞退。", "費用面での懸念により辞退。"],
        "pending": ["未着手。", "担当者からの連絡待ち。"],
    }
    return random.choice(notes.get(status, ["対応中。"]))


def _seed_referrals(db: Session, students_data: list):
    """生徒間の紹介・被紹介履歴を生成 (在籍生の一部が他の在籍生を紹介)"""
    students = [sd["student"] for sd in students_data if sd["student"].status in ["enrolled", "on_leave"]]
    if len(students) < 4:
        return

    today = date.today()
    # 全体の約25%が紹介者になる
    referrers = random.sample(students, k=max(1, len(students) // 4))
    for referrer in referrers:
        # 在籍生を紹介 (60%) または 未入会の人物名 (40%)
        if random.random() < 0.6:
            candidate = random.choice([s for s in students if s.id != referrer.id])
            db.add(Referral(
                referrer_student_id=referrer.id,
                referred_student_id=candidate.id,
                referred_name=candidate.name,
                occurred_at=today - timedelta(days=random.randint(30, 300)),
                note="入会済み",
            ))
        else:
            db.add(Referral(
                referrer_student_id=referrer.id,
                referred_student_id=None,
                referred_name=fake.name(),
                occurred_at=today - timedelta(days=random.randint(30, 300)),
                note=random.choice(["体験申込", "資料請求のみ", "検討中"]),
            ))


def main():
    parser = argparse.ArgumentParser(description="シードデータを生成する")
    parser.add_argument("--force", action="store_true", help="既存データを削除して再生成")
    args = parser.parse_args()

    db: Session = SessionLocal()
    try:
        # 既存データ確認
        existing = db.query(User).count()
        if existing > 0 and not args.force:
            print(f"シードデータが既に存在します ({existing} ユーザー)。スキップします。")
            print("再生成する場合は --force オプションを使用してください。")
            return

        if args.force:
            clear_all_tables(db)

        print("シードデータを生成中...")

        # 教室
        classroom = seed_classroom(db)
        print(f"  教室作成: {classroom.name}")

        # ユーザー
        users = seed_users(db, classroom)
        print(f"  ユーザー作成: {1 + 1 + 6 + 2} 名")

        # 講座
        courses = seed_courses(db)
        print(f"  講座作成: {len(courses)} 講座 (集団5・個別3・自立4)")

        # クラス (集団部門)
        class_groups = seed_class_groups(db, classroom, users)
        print(f"  クラス作成: {len(class_groups)} クラス (中1〜中3)")

        # 生徒 + 関連データ
        print("  生徒データ生成中 (80名)...")
        students_data = seed_students(db, classroom, users, courses, class_groups)
        print(f"  生徒作成: {len(students_data)} 名")

        # 紹介・被紹介履歴
        _seed_referrals(db, students_data)
        print("  紹介履歴作成完了")

        # 営業データ
        seed_sales(db, students_data, users)
        print("  営業データ作成完了")

        db.commit()
        print("\nシードデータ生成完了!")
        print(f"  ログインURL: http://localhost:5173")
        print(f"  管理者: admin@example.com / password")
        print(f"  教室長: manager@example.com / password")
        print(f"  講師:   teacher1@example.com / password")

    except Exception as e:
        db.rollback()
        print(f"エラー: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
