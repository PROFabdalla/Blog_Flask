"""empty message

Revision ID: 1b0c98ea3f90
Revises: c8eed6df369d
Create Date: 2022-09-12 14:56:06.109280

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1b0c98ea3f90'
down_revision = 'c8eed6df369d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('about_auther', sa.Text(length=500), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'about_auther')
    # ### end Alembic commands ###
