"""experiments + assignments — A/B-тестирование (P3.5)

Revision ID: 0021
Revises: 0020
Create Date: 2026-06-27
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0021"
down_revision = "0020"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "experiments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("key", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="draft"),
        sa.Column("variants", sa.JSON(), nullable=False),
        sa.Column("conversion_event", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("key", name="uq_experiment_key"),
    )
    op.create_index("ix_experiments_key", "experiments", ["key"])

    op.create_table(
        "experiment_assignments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("experiment_id", sa.Integer(), sa.ForeignKey("experiments.id"), nullable=False),
        sa.Column("subject_id", sa.String(length=64), nullable=False),
        sa.Column("variant", sa.String(length=64), nullable=False),
        sa.Column("assigned_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("experiment_id", "subject_id", name="uq_experiment_assignment"),
    )
    op.create_index(
        "ix_experiment_assignments_experiment_id", "experiment_assignments", ["experiment_id"]
    )
    op.create_index(
        "ix_experiment_assignments_subject_id", "experiment_assignments", ["subject_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_experiment_assignments_subject_id", table_name="experiment_assignments")
    op.drop_index("ix_experiment_assignments_experiment_id", table_name="experiment_assignments")
    op.drop_table("experiment_assignments")
    op.drop_index("ix_experiments_key", table_name="experiments")
    op.drop_table("experiments")
