"""add archived to github

Revision ID: 4c7e9f9d2a1b
Revises: 22d18de9decd
Create Date: 2026-04-05 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = '4c7e9f9d2a1b'
down_revision = 'e2177fe737f5'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('github') as batch_op:
        batch_op.add_column(sa.Column('archived', sa.Boolean(), nullable=True))


def downgrade():
    with op.batch_alter_table('github') as batch_op:
        batch_op.drop_column('archived')
