"""Add a creator_id to streams

Revision ID: 1f8e3cf51fbc
Revises: 70c7d046881
Create Date: 2013-12-08 16:55:14.142000

"""

# revision identifiers, used by Alembic.
revision = '1f8e3cf51fbc'
down_revision = '70c7d046881'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('stream', sa.Column('creator_id', sa.Integer(), nullable=False))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('stream', 'creator_id')
    ### end Alembic commands ###