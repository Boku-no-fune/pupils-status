"""add school_type, photo, division, staff_notes, video_lesson_logs

Revision ID: 0002
Revises: 0001
Create Date: 2026-05-01
"""

from alembic import op
import sqlalchemy as sa

revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade():
    # --- students テーブルにカラム追加 ---
    op.add_column('students', sa.Column('school_type', sa.String(10), nullable=True))
    op.add_column('students', sa.Column('photo_data', sa.Text(), nullable=True))

    # --- courses テーブルにカラム追加 ---
    op.add_column('courses', sa.Column('division', sa.String(10), nullable=True))
    op.add_column('courses', sa.Column('course_type', sa.String(30), nullable=True))

    # --- staff_notes テーブル新規作成 ---
    op.create_table(
        'staff_notes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('teacher_id', sa.Integer(), nullable=True),
        sa.Column('note_type', sa.String(30), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('occurred_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['student_id'], ['students.id']),
        sa.ForeignKeyConstraint(['teacher_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_staff_notes_id', 'staff_notes', ['id'], unique=False)
    op.create_index('ix_staff_notes_student_id', 'staff_notes', ['student_id'], unique=False)

    # --- video_lesson_logs テーブル新規作成 ---
    op.create_table(
        'video_lesson_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('lesson_name', sa.String(200), nullable=False),
        sa.Column('lesson_category', sa.String(50), nullable=True),
        sa.Column('viewed_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('duration_minutes', sa.Float(), nullable=False, server_default='0'),
        sa.Column('completion_rate', sa.Float(), nullable=True),
        sa.Column('source_system', sa.String(50), nullable=True),
        sa.Column('imported_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['student_id'], ['students.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_video_lesson_logs_id', 'video_lesson_logs', ['id'], unique=False)
    op.create_index('ix_video_lesson_logs_student_id', 'video_lesson_logs', ['student_id'], unique=False)


def downgrade():
    op.drop_index('ix_video_lesson_logs_student_id', table_name='video_lesson_logs')
    op.drop_index('ix_video_lesson_logs_id', table_name='video_lesson_logs')
    op.drop_table('video_lesson_logs')

    op.drop_index('ix_staff_notes_student_id', table_name='staff_notes')
    op.drop_index('ix_staff_notes_id', table_name='staff_notes')
    op.drop_table('staff_notes')

    op.drop_column('courses', 'course_type')
    op.drop_column('courses', 'division')
    op.drop_column('students', 'photo_data')
    op.drop_column('students', 'school_type')
