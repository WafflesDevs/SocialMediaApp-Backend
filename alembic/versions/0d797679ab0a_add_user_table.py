"""Add user table

Revision ID: 0d797679ab0a
Revises: 467461623737
Create Date: 2026-06-22 22:27:17.536877

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0d797679ab0a'
down_revision: Union[str, Sequence[str], None] = '467461623737'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column("id",sa.Integer(), nullable=False),
        sa.Column("email",sa.String(), nullable=False),
        sa.Column("password",sa.String(), nullable=False),
        sa.Column("created_at",sa.TIMESTAMP(timezone=True)),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint("email")
    )
    pass


def downgrade() -> None:
    op.drop_table('users')
    pass
