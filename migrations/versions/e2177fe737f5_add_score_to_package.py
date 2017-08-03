"""add_score_to_package

Revision ID: e2177fe737f5
Revises: 22d18de9decd
Create Date: 2017-08-01 22:14:36.684755

"""

# revision identifiers, used by Alembic.
revision = 'e2177fe737f5'
down_revision = '22d18de9decd'

from alembic import op
from sqlalchemy import text
import sqlalchemy as sa


def upgrade():
    op.add_column('package', sa.Column('score', sa.Float(), nullable=False, server_default=text('0.0')))


def downgrade():
    with op.batch_alter_table('package') as batch_op:
        batch_op.drop_column('score')
