"""Add rest of tables and cols! and auto-vote

Revision ID: b5de5ef341c0
Revises: e82aa8ccb061
Create Date: 2026-06-23 12:48:58.442370

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b5de5ef341c0'
down_revision: Union[str, Sequence[str], None] = 'e82aa8ccb061'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop FK constraint FIRST, before dropping the users table
    op.drop_constraint('post_users_fk', 'posts', type_='foreignkey')
    
    # Now safe to drop users
    op.drop_table('users')
    
    op.add_column('posts', sa.Column('content', sa.String(), nullable=False))
    op.alter_column('posts', 'published',
               existing_type=sa.BOOLEAN(),
               nullable=True,
               existing_server_default=sa.text('true'))
    op.create_foreign_key(None, 'posts', 'Users', ['owner_id'], ['id'], ondelete='CASCADE')
    op.drop_column('posts', 'Content')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('posts', sa.Column('Content', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'posts', type_='foreignkey')
    op.create_foreign_key('post_users_fk', 'posts', 'users', ['owner_id'], ['id'], ondelete='CASCADE')
    op.alter_column('posts', 'published',
               existing_type=sa.BOOLEAN(),
               nullable=False,
               existing_server_default=sa.text('true'))
    op.drop_column('posts', 'content')
    op.create_table('users',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('email', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('password', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='users_pkey'),
    sa.UniqueConstraint('email', name='users_email_key', postgresql_include=[], postgresql_nulls_not_distinct=False)
    )