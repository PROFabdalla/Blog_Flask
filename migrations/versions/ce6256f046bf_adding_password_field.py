"""adding password field

Revision ID: ce6256f046bf
Revises: 7ce669673adb
Create Date: 2022-09-10 12:08:22.233301

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ce6256f046bf'
down_revision = '7ce669673adb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('password_hashed', sa.String(length=150), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'password_hashed')
    # ### end Alembic commands ###
