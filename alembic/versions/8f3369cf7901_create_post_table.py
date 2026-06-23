"""Create post table

Revision ID: 8f3369cf7901
Revises: 
Create Date: 2026-06-22 22:07:44.796890

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8f3369cf7901'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None: #handles changes
     op.create_table(
        'posts',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('title', sa.String(), nullable=False)
    )
     pass


def downgrade() -> None: #rolls it back!
    op.drop_table('posts') #deletes table!
    pass
