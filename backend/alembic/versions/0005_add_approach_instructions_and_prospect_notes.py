"""add approach_instructions; staff_notes gain prospect_id (and student_id nullable)

Revision ID: 0005
Revises: 0004
Create Date: 2026-06-23
"""

from alembic import op
import sqlalchemy as sa

revision = '0005'
down_revision = '0004'
branch_labels = None
depends_on = None


def upgrade():
    # ===== approach_instructions =====
    op.create_table(
        'approach_instructions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('target_type', sa.String(10), nullable=False, server_default='全体'),
        sa.Column('target_value', sa.String(50), nullable=True),
        sa.Column('period', sa.String(50), nullable=True),
        sa.Column('pdf_data', sa.Text(), nullable=True),
        sa.Column('pdf_filename', sa.String(255), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_approach_instructions_id', 'approach_instructions', ['id'])

    # ===== staff_notes: prospect対応 =====
    op.add_column('staff_notes', sa.Column('prospect_id', sa.Integer(), nullable=True))
    op.alter_column('staff_notes', 'student_id', existing_type=sa.Integer(), nullable=True)
    op.create_index('ix_staff_notes_prospect_id', 'staff_notes', ['prospect_id'])
    op.create_foreign_key('fk_staff_notes_prospect', 'staff_notes', 'prospects',
                          ['prospect_id'], ['id'])


def downgrade():
    op.drop_constraint('fk_staff_notes_prospect', 'staff_notes', type_='foreignkey')
    op.drop_index('ix_staff_notes_prospect_id', table_name='staff_notes')
    op.alter_column('staff_notes', 'student_id', existing_type=sa.Integer(), nullable=False)
    op.drop_column('staff_notes', 'prospect_id')
    op.drop_table('approach_instructions')
