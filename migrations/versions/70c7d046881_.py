"""Add user model

Revision ID: 70c7d046881
Revises: 19b7fe1331be
Create Date: 2013-12-07 15:30:26.169000

"""

# revision identifiers, used by Alembic.
revision = '70c7d046881'
down_revision = '19b7fe1331be'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=20), nullable=False),
        sa.Column('email', sa.EmailType(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=250), nullable=False),
        sa.Column('user_created_datetime', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user')
    ### end Alembic commands ###
