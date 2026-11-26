"""initial tables

Revision ID: 0001
Revises:
Create Date: 2026-11-26
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column(
            "role", sa.String(length=32), nullable=False, server_default="user"
        ),
        sa.Column("created_time", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "notes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("body", sa.Text(), nullable=False, server_default=""),
        sa.Column(
            "owner_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("created_time", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_notes_owner_id", "notes", ["owner_id"])

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column(
            "owner_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("note_id", sa.Integer(), nullable=True),
        sa.Column("created_time", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_notifications_owner_id", "notifications", ["owner_id"])


def downgrade() -> None:
    op.drop_index("ix_notifications_owner_id", table_name="notifications")
    op.drop_table("notifications")
    op.drop_index("ix_notes_owner_id", table_name="notes")
    op.drop_table("notes")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")