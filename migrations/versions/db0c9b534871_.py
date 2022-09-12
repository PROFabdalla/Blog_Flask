"""empty message

Revision ID: db0c9b534871
Revises: 1b0c98ea3f90
Create Date: 2022-09-12 15:59:42.916213

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'db0c9b534871'
down_revision = '1b0c98ea3f90'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('profile_pic', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'profile_pic')
    # ### end Alembic commands ###