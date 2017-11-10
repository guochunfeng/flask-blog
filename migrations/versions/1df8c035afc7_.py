"""empty message

Revision ID: 1df8c035afc7
Revises: 
Create Date: 2017-11-08 15:20:29.897000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1df8c035afc7'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('posts') as batch_op:
        batch_op.drop_column('boby_html')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('boby_html', sa.TEXT(), nullable=True))
    op.drop_column('posts', 'title')
    # ### end Alembic commands ###
