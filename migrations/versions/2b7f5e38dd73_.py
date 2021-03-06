"""Add content_type to entry

Revision ID: 2b7f5e38dd73
Revises: 1f8e3cf51fbc
Create Date: 2013-12-14 20:44:38.076000

"""

# revision identifiers, used by Alembic.
revision = '2b7f5e38dd73'
down_revision = '1f8e3cf51fbc'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('entry', sa.Column('content_type', sa.String(length=20), nullable=False))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('entry', 'content_type')
    ### end Alembic commands ###
