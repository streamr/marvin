"""Add stream.description field

Revision ID: 3864b4713ef0
Revises: 872b6c03db1
Create Date: 2014-02-11 21:33:49.362000

"""

# revision identifiers, used by Alembic.
revision = '3864b4713ef0'
down_revision = '872b6c03db1'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('stream', sa.Column('description', sa.String(length=140), nullable=False, server_default=''))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('stream', 'description')
    ### end Alembic commands ###
