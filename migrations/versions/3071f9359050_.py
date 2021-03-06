"""empty message

Revision ID: 3071f9359050
Revises: 3ee3dd188ee5
Create Date: 2015-05-05 14:04:14.963033

"""

# revision identifiers, used by Alembic.
revision = '3071f9359050'
down_revision = '3ee3dd188ee5'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('problemsetscore', sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now()))
    op.add_column('user', sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now()))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'updated_at')
    op.drop_column('problemsetscore', 'updated_at')
    ### end Alembic commands ###
