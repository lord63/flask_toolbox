"""Initial migration

Revision ID: 8bc8e4c1f48a
Revises: None
Create Date: 2016-01-23 19:37:49.371358

"""

# revision identifiers, used by Alembic.
revision = '8bc8e4c1f48a'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('category',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('package',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=40), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('website_url', sa.String(length=80), nullable=True),
    sa.Column('documentation_url', sa.String(length=80), nullable=True),
    sa.Column('source_code_url', sa.String(length=80), nullable=True),
    sa.Column('bug_tracker_url', sa.String(length=80), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['category.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('github',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('package_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['package_id'], ['package.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('pyPI',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('package_id', sa.Integer(), nullable=True),
    sa.Column('download_num', sa.Integer(), nullable=True),
    sa.Column('release_num', sa.Integer(), nullable=True),
    sa.Column('current_version', sa.String(length=20), nullable=True),
    sa.Column('released_date', sa.DateTime(), nullable=True),
    sa.Column('first_release', sa.DateTime(), nullable=True),
    sa.Column('python_version', sa.String(length=40), nullable=True),
    sa.ForeignKeyConstraint(['package_id'], ['package.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('pyPI')
    op.drop_table('github')
    op.drop_table('package')
    op.drop_table('category')
    ### end Alembic commands ###
