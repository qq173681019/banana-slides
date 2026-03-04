"""add Vertex AI fields to settings table

Revision ID: 016
Revises: 015
Create Date: 2026-03-04

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '016'
down_revision = '015'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('settings', sa.Column('vertex_project_id', sa.String(100), nullable=True))
    op.add_column('settings', sa.Column('vertex_location', sa.String(50), nullable=True))


def downgrade():
    op.drop_column('settings', 'vertex_location')
    op.drop_column('settings', 'vertex_project_id')
