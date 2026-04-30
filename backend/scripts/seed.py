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
    EnrollmentEvent, Enrollment,
    Attendance, RoomLog,
    Homework,
    TestScore, TargetSchool, SchoolGrade,
    Payment, ParentContact,
    SalesAction, SalesGoal,
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
    """講座を4つ作成"""
    course_data = [
        ("中学英語", "英語", "中学生向け英語コース"),
        ("中学数学", "数学", "中学生向け数学コース"),
        ("高校英語", "英語", "高校生向け英語コース"),
        ("高校数学", "数学", "高校生向け数学コース"),
    ]
    courses = []
    for name, subject, desc in course_data:
        c = Course(name=name, subject=subject, description=desc)
        db.add(c)
        db.flush()
        courses.append(c)
    return courses


def seed_students(db: Session, classroom: Classroom, users: dict, courses: list) -> list:
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

        # 担当講師をランダムに割り当て
        teacher = random.choice(teachers)

        # 学校名
        school = random.choice(SCHOOLS)

        student = Student(
            name=fake.name(),
            grade=grade,
            school=school,
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

        # 受講講座 (在籍・休会生徒のみ)
        if status in ["enrolled", "on_leave"]:
            _seed_enrollments(db, student, courses)

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

    # 入会
    if student.enrolled_at:
        events.append(EnrollmentEvent(
            student_id=student.id,
            event_type="入会",
            occurred_at=datetime.combine(student.enrolled_at, datetime.min.time()),
            note="正式入会",
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
    """受講講座を設定"""
    # 学年に応じた講座選択
    if student.grade <= 9:
        available = [c for c in courses if "中学" in c.name]
    else:
        available = [c for c in courses if "高校" in c.name]

    if not available:
        available = courses[:2]

    # 1〜2講座受講
    selected = random.sample(available, min(random.randint(1, 2), len(available)))
    for course in selected:
        e = Enrollment(
            student_id=student.id,
            course_id=course.id,
            started_at=student.enrolled_at or date.today() - timedelta(days=180),
            ended_at=student.withdrawn_at,
            change_type="新規",
        )
        db.add(e)


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
            if rand < present_rate:
                status = "present"
            elif rand < present_rate + 0.05:
                status = "late"
            else:
                status = "absent"

            att = Attendance(
                student_id=student.id,
                class_date=current,
                status=status,
                note="無断欠席" if status == "absent" and random.random() < 0.3 else None,
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
    """4回分のテスト成績を生成"""
    # 基準スコア (生徒ごとにランダム)
    base_scores = {s: random.gauss(65, 15) for s in SUBJECTS}

    # クリッピング
    base_scores = {s: max(20, min(100, v)) for s, v in base_scores.items()}

    # 成績下降フラグがある生徒は特定科目で連続下降を設定
    declining_subjects = random.sample(SUBJECTS, 2) if profile.get("is_declining") else []

    for session_idx, session in enumerate(TEST_SESSIONS):
        # 退会前のデータのみ
        if student.withdrawn_at and session["test_date"] > student.withdrawn_at:
            continue

        for subject in SUBJECTS:
            score = base_scores[subject]

            if subject in declining_subjects:
                # 3回連続で5-10点下降
                decline = (session_idx + 1) * random.uniform(5, 10)
                score = max(10, score - decline)
            else:
                # 自然なばらつき
                score += random.gauss(0, 5)
                score = max(10, min(100, score))

            # 偏差値計算 (クラス平均65, 標準偏差12と仮定)
            deviation = 50 + (score - 65) / 12 * 10

            ts = TestScore(
                student_id=student.id,
                test_id=session["test_id"],
                test_name=session["test_name"],
                subject=subject,
                raw_score=round(score, 1),
                rank=random.randint(1, 80),
                deviation_value=round(max(20, min(80, deviation)), 1),
                test_date=session["test_date"],
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
        print(f"  講座作成: {len(courses)} 講座")

        # 生徒 + 関連データ
        print("  生徒データ生成中 (80名)...")
        students_data = seed_students(db, classroom, users, courses)
        print(f"  生徒作成: {len(students_data)} 名")

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
