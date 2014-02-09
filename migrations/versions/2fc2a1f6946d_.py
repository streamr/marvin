"""Initial commit.

Revision ID: 2fc2a1f6946d
Revises: None
Create Date: 2013-11-11 13:44:56.669000

"""

# revision identifiers, used by Alembic.
revision = '2fc2a1f6946d'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('movie',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('external_id', sa.String(length=200), nullable=False),
        sa.Column('title', sa.String(length=100), nullable=False),
        sa.Column('category', sa.String(length=20), nullable=False),
        sa.Column('datetime_added', sa.DateTime(), nullable=True),
        sa.Column('year', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('stream',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=30), nullable=False),
        sa.Column('movie_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['movie_id'], ['movie.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('entry',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('entry_point_in_ms', sa.Integer(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('stream_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['stream_id'], ['stream.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('entry')
    op.drop_table('stream')
    op.drop_table('movie')
    ### end Alembic commands ###