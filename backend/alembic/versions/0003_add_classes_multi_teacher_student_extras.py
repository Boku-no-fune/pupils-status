"""add class_groups, multi-teacher links, student extras, exam certs, test_type, makeup, tags

Revision ID: 0003
Revises: 0002
Create Date: 2026-06-22
"""

from alembic import op
import sqlalchemy as sa

revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None


def upgrade():
    # ===== class_groups (クラス) =====
    op.create_table(
        'class_groups',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(20), nullable=False),
        sa.Column('grade', sa.Integer(), nullable=False),
        sa.Column('level', sa.String(10), nullable=False),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('classroom_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['classroom_id'], ['classrooms.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_class_groups_id', 'class_groups', ['id'])
    op.create_index('ix_class_groups_name', 'class_groups', ['name'])

    # ===== class_teachers / student_teachers (多対多) =====
    op.create_table(
        'class_teachers',
        sa.Column('class_group_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['class_group_id'], ['class_groups.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('class_group_id', 'user_id'),
    )
    op.create_table(
        'student_teachers',
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('student_id', 'user_id'),
    )

    # ===== students カラム追加 =====
    op.add_column('students', sa.Column('member_number', sa.String(10), nullable=True))
    op.add_column('students', sa.Column('gender', sa.String(4), nullable=True))
    op.add_column('students', sa.Column('parent_name', sa.String(100), nullable=True))
    op.add_column('students', sa.Column('sibling_info', sa.Text(), nullable=True))
    op.add_column('students', sa.Column('class_group_id', sa.Integer(), nullable=True))
    op.create_index('ix_students_member_number', 'students', ['member_number'])
    op.create_foreign_key('fk_students_class_group', 'students', 'class_groups',
                          ['class_group_id'], ['id'])

    # ===== test_scores.test_type =====
    op.add_column('test_scores', sa.Column('test_type', sa.String(30), nullable=True))
    op.create_index('ix_test_scores_test_type', 'test_scores', ['test_type'])

    # ===== attendances 振替・映像視聴 =====
    op.add_column('attendances', sa.Column('makeup_type', sa.String(20), nullable=True))
    op.add_column('attendances', sa.Column('makeup_note', sa.String(100), nullable=True))

    # ===== staff_notes.tags =====
    op.add_column('staff_notes', sa.Column('tags', sa.JSON(), nullable=True))

    # ===== student_phones =====
    op.create_table(
        'student_phones',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('phone_number', sa.String(20), nullable=False),
        sa.Column('memo', sa.String(50), nullable=True),
        sa.Column('position', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['student_id'], ['students.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_student_phones_id', 'student_phones', ['id'])
    op.create_index('ix_student_phones_student_id', 'student_phones', ['student_id'])

    # ===== special_notes =====
    op.create_table(
        'special_notes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('importance', sa.String(10), nullable=False, server_default='中'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['student_id'], ['students.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_special_notes_id', 'special_notes', ['id'])
    op.create_index('ix_special_notes_student_id', 'special_notes', ['student_id'])

    # ===== profile_memos =====
    op.create_table(
        'profile_memos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(30), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['student_id'], ['students.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_profile_memos_id', 'profile_memos', ['id'])
    op.create_index('ix_profile_memos_student_id', 'profile_memos', ['student_id'])

    # ===== parent_requests =====
    op.create_table(
        'parent_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('request_type', sa.String(10), nullable=False, server_default='要望'),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('status', sa.String(10), nullable=False, server_default='対応中'),
        sa.Column('occurred_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['student_id'], ['students.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_parent_requests_id', 'parent_requests', ['id'])
    op.create_index('ix_parent_requests_student_id', 'parent_requests', ['student_id'])

    # ===== referrals =====
    op.create_table(
        'referrals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('referrer_student_id', sa.Integer(), nullable=False),
        sa.Column('referred_student_id', sa.Integer(), nullable=True),
        sa.Column('referred_name', sa.String(100), nullable=True),
        sa.Column('occurred_at', sa.Date(), nullable=True),
        sa.Column('note', sa.String(200), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['referrer_student_id'], ['students.id']),
        sa.ForeignKeyConstraint(['referred_student_id'], ['students.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_referrals_id', 'referrals', ['id'])
    op.create_index('ix_referrals_referrer_student_id', 'referrals', ['referrer_student_id'])
    op.create_index('ix_referrals_referred_student_id', 'referrals', ['referred_student_id'])

    # ===== exam_certifications (英検・漢検) =====
    op.create_table(
        'exam_certifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('exam_type', sa.String(20), nullable=False),
        sa.Column('level', sa.String(20), nullable=False),
        sa.Column('score', sa.Integer(), nullable=True),
        sa.Column('result', sa.String(10), nullable=False, server_default='合格'),
        sa.Column('exam_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['student_id'], ['students.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_exam_certifications_id', 'exam_certifications', ['id'])
    op.create_index('ix_exam_certifications_student_id', 'exam_certifications', ['student_id'])


def downgrade():
    op.drop_table('exam_certifications')
    op.drop_table('referrals')
    op.drop_table('parent_requests')
    op.drop_table('profile_memos')
    op.drop_table('special_notes')
    op.drop_table('student_phones')

    op.drop_column('staff_notes', 'tags')
    op.drop_column('attendances', 'makeup_note')
    op.drop_column('attendances', 'makeup_type')
    op.drop_index('ix_test_scores_test_type', table_name='test_scores')
    op.drop_column('test_scores', 'test_type')

    op.drop_constraint('fk_students_class_group', 'students', type_='foreignkey')
    op.drop_index('ix_students_member_number', table_name='students')
    op.drop_column('students', 'class_group_id')
    op.drop_column('students', 'sibling_info')
    op.drop_column('students', 'parent_name')
    op.drop_column('students', 'gender')
    op.drop_column('students', 'member_number')

    op.drop_table('student_teachers')
    op.drop_table('class_teachers')
    op.drop_table('class_groups')
