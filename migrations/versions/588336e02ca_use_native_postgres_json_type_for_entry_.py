"""Use native postgres JSON type for Entry.content

Revision ID: 588336e02ca
Revises: 2b7f5e38dd73
Create Date: 2014-01-09 22:40:07.690000

"""

# revision identifiers, used by Alembic.
revision = '588336e02ca'
down_revision = '2b7f5e38dd73'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    # Couldn't find a way to specify a USING clause with alembic's alter_table
    op.execute('ALTER TABLE entry ALTER COLUMN content TYPE json USING content::json')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('entry', 'content',
               type_=sa.TEXT(),
               nullable=False)
    ### end Alembic commands ###
