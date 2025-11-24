"""
Initial PostgreSQL schema for Secure AI Monitoring Sandbox

Maps to:
- docs/07_database_design.txt (sections 2, 3, 4, 5)
- docs/08_database_design.txt (normalized mirror)
- docs/08_ai_behavior_rules.txt (severity/action categories reference)
- docs/11_database_design_extended.txt (placeholders noted in comments)
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Requirement: see 07_database_design.txt, section 2(a): Users
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger, primary_key=True),
        sa.Column("username", sa.String(length=150), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column(
            "role",
            sa.String(length=20),
            nullable=False,
            # 07: role (admin/user)
            # CHECK constraint purely from documentation; do not extend beyond admin/user
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
    )

    # Requirement: see 07_database_design.txt, section 2(b): Folders
    op.create_table(
        "folders",
        sa.Column("id", sa.BigInteger, primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("path", sa.Text, nullable=False),
        sa.Column("owner_id", sa.BigInteger, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("modified_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_index("ix_folders_owner_id", "folders", ["owner_id"])  # 11: indices placeholder

    # Requirement: see 07_database_design.txt, section 2(c): Files
    op.create_table(
        "files",
        sa.Column("id", sa.BigInteger, primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("path", sa.Text, nullable=False),
        sa.Column("folder_id", sa.BigInteger, sa.ForeignKey("folders.id", ondelete="CASCADE"), nullable=False),
        sa.Column("owner_id", sa.BigInteger, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("modified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("hash", sa.String(length=128), nullable=True),  # optional checksum for integrity
    )

    op.create_index("ix_files_folder_id", "files", ["folder_id"])  # 11: indices placeholder
    op.create_index("ix_files_owner_id", "files", ["owner_id"])    # 11: indices placeholder

    # Requirement: see 07_database_design.txt, section 2(d): AI_Rules
    # Severity/action semantics reference 08_ai_behavior_rules.txt
    op.create_table(
        "ai_rules",
        sa.Column("id", sa.BigInteger, primary_key=True),
        sa.Column("rule_name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("severity_level", sa.String(length=20), nullable=True),
        sa.Column("action_type", sa.String(length=50), nullable=True),
        sa.Column("adaptive_flag", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column(
            "last_updated",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("stored_in_engine", sa.Boolean, nullable=False, server_default=sa.text("false")),
    )

    # Requirement: see 07_database_design.txt, section 2(e): Events
    op.create_table(
        "events",
        sa.Column("id", sa.BigInteger, primary_key=True),
        sa.Column("event_type", sa.String(length=20), nullable=False),  # create/delete/modify
        sa.Column("target_file_id", sa.BigInteger, sa.ForeignKey("files.id", ondelete="SET NULL"), nullable=True),
        sa.Column("target_folder_id", sa.BigInteger, sa.ForeignKey("folders.id", ondelete="SET NULL"), nullable=True),
        sa.Column("triggered_by_user_id", sa.BigInteger, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("processed_flag", sa.Boolean, nullable=False, server_default=sa.text("false")),
        # docs/11_database_design_extended.txt: Constraints for file vs folder targets are not fully documented.
        # Not enforcing XOR here. Placeholder for future migration when details are provided.
    )

    op.create_index("ix_events_target_file_id", "events", ["target_file_id"])   # 11: indices placeholder
    op.create_index("ix_events_target_folder_id", "events", ["target_folder_id"])  # 11: indices placeholder
    op.create_index("ix_events_triggered_by_user_id", "events", ["triggered_by_user_id"])  # 11: indices placeholder

    # Requirement: see 07_database_design.txt, section 2(f): AI_Feedback
    op.create_table(
        "ai_feedback",
        sa.Column("id", sa.BigInteger, primary_key=True),
        sa.Column("event_id", sa.BigInteger, sa.ForeignKey("events.id", ondelete="CASCADE"), nullable=False),
        sa.Column("admin_id", sa.BigInteger, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("feedback_type", sa.String(length=20), nullable=False),  # approve/reject/modify
        sa.Column("comment", sa.Text, nullable=True),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.UniqueConstraint("event_id", name="uq_ai_feedback_event_id"),  # 1:1 feedback per event
    )

    op.create_index("ix_ai_feedback_event_id", "ai_feedback", ["event_id"])  # 11: indices placeholder

    # Requirement: see 07_database_design.txt, section 2(g): Logs
    op.create_table(
        "logs",
        sa.Column("id", sa.BigInteger, primary_key=True),
        sa.Column("log_type", sa.String(length=50), nullable=False),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("related_event_id", sa.BigInteger, sa.ForeignKey("events.id", ondelete="SET NULL"), nullable=True),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )

    op.create_index("ix_logs_related_event_id", "logs", ["related_event_id"])  # 11: indices placeholder

    # Security Measures note (07: section 3): encryption/roles/audit logs are application/DB config level,
    # not enforced directly in this initial migration. Future migrations may add RLS/roles.


def downgrade() -> None:
    op.drop_index("ix_logs_related_event_id", table_name="logs")
    op.drop_table("logs")

    op.drop_index("ix_ai_feedback_event_id", table_name="ai_feedback")
    op.drop_table("ai_feedback")

    op.drop_index("ix_events_triggered_by_user_id", table_name="events")
    op.drop_index("ix_events_target_folder_id", table_name="events")
    op.drop_index("ix_events_target_file_id", table_name="events")
    op.drop_table("events")

    op.drop_table("ai_rules")

    op.drop_index("ix_files_owner_id", table_name="files")
    op.drop_index("ix_files_folder_id", table_name="files")
    op.drop_table("files")

    op.drop_index("ix_folders_owner_id", table_name="folders")
    op.drop_table("folders")

    op.drop_table("users")
