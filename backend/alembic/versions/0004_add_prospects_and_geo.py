"""add prospects, prospect_stages, and geo columns on students

Revision ID: 0004
Revises: 0003
Create Date: 2026-06-22
"""

from alembic import op
import sqlalchemy as sa

revision = '0004'
down_revision = '0003'
branch_labels = None
depends_on = None


def upgrade():
    # ===== students 住所・座標 =====
    op.add_column('students', sa.Column('address', sa.String(255), nullable=True))
    op.add_column('students', sa.Column('home_lat', sa.Float(), nullable=True))
    op.add_column('students', sa.Column('home_lng', sa.Float(), nullable=True))
    op.add_column('students', sa.Column('school_lat', sa.Float(), nullable=True))
    op.add_column('students', sa.Column('school_lng', sa.Float(), nullable=True))

    # ===== prospects (未入会見込み客) =====
    op.create_table(
        'prospects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('grade', sa.Integer(), nullable=True),
        sa.Column('school', sa.String(200), nullable=True),
        sa.Column('source', sa.String(50), nullable=True),
        sa.Column('address', sa.String(255), nullable=True),
        sa.Column('home_lat', sa.Float(), nullable=True),
        sa.Column('home_lng', sa.Float(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='active'),
        sa.Column('assigned_to', sa.Integer(), nullable=True),
        sa.Column('first_contact_at', sa.Date(), nullable=True),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['assigned_to'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_prospects_id', 'prospects', ['id'])

    # ===== prospect_stages =====
    op.create_table(
        'prospect_stages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('prospect_id', sa.Integer(), nullable=False),
        sa.Column('stage', sa.String(30), nullable=False),
        sa.Column('status', sa.String(10), nullable=False, server_default='未対応'),
        sa.Column('memo', sa.Text(), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('occurred_at', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['prospect_id'], ['prospects.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_prospect_stages_id', 'prospect_stages', ['id'])
    op.create_index('ix_prospect_stages_prospect_id', 'prospect_stages', ['prospect_id'])


def downgrade():
    op.drop_table('prospect_stages')
    op.drop_table('prospects')
    op.drop_column('students', 'school_lng')
    op.drop_column('students', 'school_lat')
    op.drop_column('students', 'home_lng')
    op.drop_column('students', 'home_lat')
    op.drop_column('students', 'address')
