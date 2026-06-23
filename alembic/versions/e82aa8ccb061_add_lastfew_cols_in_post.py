"""Add lastfew cols in post

Revision ID: e82aa8ccb061
Revises: 0f3c1df7a4d2
Create Date: 2026-06-22 22:41:57.314341

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e82aa8ccb061'
down_revision: Union[str, Sequence[str], None] = '0f3c1df7a4d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        'posts',
        sa.Column('published', sa.Boolean, nullable=False, server_default='true')
    )
    op.add_column(
        'posts',
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()'))
    )

def downgrade():
    op.drop_column('posts', 'published')
    op.drop_column('posts', 'created_at')
