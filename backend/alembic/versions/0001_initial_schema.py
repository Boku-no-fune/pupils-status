"""初期スキーマ作成 — 全テーブル

Revision ID: 0001
Revises:
Create Date: 2024-01-01 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # classrooms テーブル
    op.create_table(
        'classrooms',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('address', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_classrooms_id'), 'classrooms', ['id'], unique=False)

    # users テーブル
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('classroom_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['classroom_id'], ['classrooms.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # courses テーブル
    op.create_table(
        'courses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('subject', sa.String(length=50), nullable=True),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_courses_id'), 'courses', ['id'], unique=False)

    # students テーブル
    op.create_table(
        'students',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('grade', sa.Integer(), nullable=False),
        sa.Column('school', sa.String(length=200), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('enrolled_at', sa.Date(), nullable=True),
        sa.Column('trial_at', sa.Date(), nullable=True),
        sa.Column('withdrawn_at', sa.Date(), nullable=True),
        sa.Column('assigned_teacher_id', sa.Integer(), nullable=True),
        sa.Column('classroom_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['assigned_teacher_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['classroom_id'], ['classrooms.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_students_id'), 'students', ['id'], unique=False)

    # enrollment_events テーブル
    op.create_table(
        'enrollment_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('occurred_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_enrollment_events_id'), 'enrollment_events', ['id'], unique=False)
    op.create_index(op.f('ix_enrollment_events_student_id'), 'enrollment_events', ['student_id'], unique=False)

    # enrollments テーブル
    op.create_table(
        'enrollments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.Column('started_at', sa.Date(), nullable=False),
        sa.Column('ended_at', sa.Date(), nullable=True),
        sa.Column('change_type', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_enrollments_id'), 'enrollments', ['id'], unique=False)
    op.create_index(op.f('ix_enrollments_student_id'), 'enrollments', ['student_id'], unique=False)

    # attendances テーブル
    op.create_table(
        'attendances',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('class_date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_attendances_class_date'), 'attendances', ['class_date'], unique=False)
    op.create_index(op.f('ix_attendances_id'), 'attendances', ['id'], unique=False)
    op.create_index(op.f('ix_attendances_student_id'), 'attendances', ['student_id'], unique=False)

    # room_logs テーブル
    op.create_table(
        'room_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('entered_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('exited_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_room_logs_id'), 'room_logs', ['id'], unique=False)
    op.create_index(op.f('ix_room_logs_student_id'), 'room_logs', ['student_id'], unique=False)

    # homeworks テーブル
    op.create_table(
        'homeworks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('assigned_date', sa.Date(), nullable=False),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('checked_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['checked_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_homeworks_id'), 'homeworks', ['id'], unique=False)
    op.create_index(op.f('ix_homeworks_student_id'), 'homeworks', ['student_id'], unique=False)

    # test_scores テーブル
    op.create_table(
        'test_scores',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('test_id', sa.String(length=50), nullable=False),
        sa.Column('test_name', sa.String(length=100), nullable=True),
        sa.Column('subject', sa.String(length=20), nullable=False),
        sa.Column('raw_score', sa.Float(), nullable=False),
        sa.Column('rank', sa.Integer(), nullable=True),
        sa.Column('deviation_value', sa.Float(), nullable=True),
        sa.Column('item_results', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('test_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_test_scores_id'), 'test_scores', ['id'], unique=False)
    op.create_index(op.f('ix_test_scores_student_id'), 'test_scores', ['student_id'], unique=False)
    op.create_index(op.f('ix_test_scores_test_id'), 'test_scores', ['test_id'], unique=False)

    # target_schools テーブル
    op.create_table(
        'target_schools',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('school_name', sa.String(length=200), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=False),
        sa.Column('recorded_at', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_target_schools_id'), 'target_schools', ['id'], unique=False)
    op.create_index(op.f('ix_target_schools_student_id'), 'target_schools', ['student_id'], unique=False)

    # school_grades テーブル
    op.create_table(
        'school_grades',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('term', sa.String(length=50), nullable=False),
        sa.Column('subject', sa.String(length=20), nullable=False),
        sa.Column('score', sa.Float(), nullable=True),
        sa.Column('grade_notation', sa.String(length=10), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_school_grades_id'), 'school_grades', ['id'], unique=False)
    op.create_index(op.f('ix_school_grades_student_id'), 'school_grades', ['student_id'], unique=False)

    # payments テーブル
    op.create_table(
        'payments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('paid_at', sa.Date(), nullable=True),
        sa.Column('due_at', sa.Date(), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_payments_id'), 'payments', ['id'], unique=False)
    op.create_index(op.f('ix_payments_student_id'), 'payments', ['student_id'], unique=False)

    # parent_contacts テーブル
    op.create_table(
        'parent_contacts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('teacher_id', sa.Integer(), nullable=True),
        sa.Column('contact_type', sa.String(length=50), nullable=False),
        sa.Column('occurred_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ),
        sa.ForeignKeyConstraint(['teacher_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_parent_contacts_id'), 'parent_contacts', ['id'], unique=False)
    op.create_index(op.f('ix_parent_contacts_student_id'), 'parent_contacts', ['student_id'], unique=False)

    # sales_actions テーブル
    op.create_table(
        'sales_actions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('assigned_to', sa.Integer(), nullable=True),
        sa.Column('action_type', sa.String(length=50), nullable=False),
        sa.Column('target_product', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=30), nullable=False),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('actioned_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['assigned_to'], ['users.id'], ),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sales_actions_id'), 'sales_actions', ['id'], unique=False)
    op.create_index(op.f('ix_sales_actions_student_id'), 'sales_actions', ['student_id'], unique=False)

    # sales_goals テーブル
    op.create_table(
        'sales_goals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('goal_type', sa.String(length=50), nullable=False),
        sa.Column('target_product', sa.String(length=100), nullable=True),
        sa.Column('target_count', sa.Integer(), nullable=False),
        sa.Column('period', sa.String(length=30), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sales_goals_id'), 'sales_goals', ['id'], unique=False)


def downgrade() -> None:
    # 逆順で削除
    op.drop_table('sales_goals')
    op.drop_table('sales_actions')
    op.drop_table('parent_contacts')
    op.drop_table('payments')
    op.drop_table('school_grades')
    op.drop_table('target_schools')
    op.drop_table('test_scores')
    op.drop_table('homeworks')
    op.drop_table('room_logs')
    op.drop_table('attendances')
    op.drop_table('enrollment_events')
    op.drop_table('enrollments')
    op.drop_table('students')
    op.drop_table('courses')
    op.drop_table('users')
    op.drop_table('classrooms')
