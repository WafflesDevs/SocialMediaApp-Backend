"""Foregin Key addon to posttable

Revision ID: 0f3c1df7a4d2
Revises: 0d797679ab0a
Create Date: 2026-06-22 22:34:37.804532

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0f3c1df7a4d2'
down_revision: Union[str, Sequence[str], None] = '0d797679ab0a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    op.add_column(
        'posts', 
        sa.Column("owner_id", sa.Integer, nullable=False)
    )
    op.create_foreign_key(
        'post_users_fk',
        source_table="posts",  
        referent_table="users",
        local_cols=["owner_id"],
        remote_cols=["id"],
        ondelete="CASCADE"
    )

def downgrade():
    op.drop_constraint('post_users_fk', 'posts', type_='foreignkey')
    op.drop_column('posts', 'owner_id')