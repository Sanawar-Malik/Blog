"""initial Migration

Revision ID: 5ab881d41776
Revises: a01f82039854
Create Date: 2022-01-17 09:42:02.336954

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5ab881d41776'
down_revision = 'a01f82039854'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('password_hash', sa.String(length=150), nullable=True))
    op.add_column('user', sa.Column('email_address', sa.String(length=20), nullable=False))
    op.drop_constraint('user_email_key', 'user', type_='unique')
    op.create_unique_constraint(None, 'user', ['email_address'])
    op.drop_column('user', 'password')
    op.drop_column('user', 'email')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('email', sa.VARCHAR(length=20), autoincrement=False, nullable=False))
    op.add_column('user', sa.Column('password', sa.VARCHAR(length=150), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'user', type_='unique')
    op.create_unique_constraint('user_email_key', 'user', ['email'])
    op.drop_column('user', 'email_address')
    op.drop_column('user', 'password_hash')
    # ### end Alembic commands ###