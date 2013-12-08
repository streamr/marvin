"""Add number_of_streams to movies.

Revision ID: 19b7fe1331be
Revises: 2c76677d803f
Create Date: 2013-11-16 22:11:44.560000

"""

# revision identifiers, used by Alembic.
revision = '19b7fe1331be'
down_revision = '2c76677d803f'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('movie', sa.Column('number_of_streams', sa.Integer(), nullable=False, server_default='0'))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('movie', 'number_of_streams')
    ### end Alembic commands ###