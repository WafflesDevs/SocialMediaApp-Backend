"""Add Content col to post

Revision ID: 467461623737
Revises: 8f3369cf7901
Create Date: 2026-06-22 22:21:24.420410

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '467461623737'
down_revision: Union[str, Sequence[str], None] = '8f3369cf7901'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'posts',
        sa.Column("Content", sa.String(),nullable = False)
    )
    pass


def downgrade() -> None:
    op.drop_column('posts','Content')
    pass
