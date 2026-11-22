"""add verification and provenance columns

Revision ID: c8294a90f123
Revises: bd80029054f8
Create Date: 2026-08-01 18:10:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'c8294a90f123'
down_revision = 'bd80029054f8'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('papers', sa.Column('source_url', sa.String(length=500), nullable=True))
    op.add_column('papers', sa.Column('source_type', sa.String(length=50), nullable=True))
    op.add_column('papers', sa.Column('scraped_at', sa.DateTime(), nullable=True))
    op.add_column('papers', sa.Column('verification_status', sa.String(length=20), server_default='unverified', nullable=False))
    op.add_column('papers', sa.Column('verified_by', sa.Integer(), nullable=True))
    op.add_column('papers', sa.Column('rejection_note', sa.Text(), nullable=True))
    op.create_foreign_key('fk_papers_verified_by_users', 'papers', 'users', ['verified_by'], ['id'], ondelete='SET NULL')
    op.create_index(op.f('ix_papers_verification_status'), 'papers', ['verification_status'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_papers_verification_status'), table_name='papers')
    op.drop_constraint('fk_papers_verified_by_users', 'papers', type_='foreignkey')
    op.drop_column('papers', 'rejection_note')
    op.drop_column('papers', 'verified_by')
    op.drop_column('papers', 'verification_status')
    op.drop_column('papers', 'scraped_at')
    op.drop_column('papers', 'source_type')
    op.drop_column('papers', 'source_url')
