"""Add database indices for performance

Revision ID: 0002_add_indices
Revises: 0001_initial_schema
Create Date: 2025-01-21

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0002_add_indices'
down_revision = '0001_initial_schema'
branch_labels = None
depends_on = None


def upgrade():
    # Events table indices (for filtering and date range queries)
    op.create_index('ix_events_timestamp', 'events', ['timestamp'], unique=False)
    op.create_index('ix_events_event_type', 'events', ['event_type'], unique=False)
    op.create_index('ix_events_processed_flag', 'events', ['processed_flag'], unique=False)
    
    # Logs table indices (for filtering and date range queries)
    op.create_index('ix_logs_log_type', 'logs', ['log_type'], unique=False)
    op.create_index('ix_logs_timestamp', 'logs', ['timestamp'], unique=False)
    
    # AI Rules table indices (for rule matching)
    op.create_index('ix_ai_rules_severity_level', 'ai_rules', ['severity_level'], unique=False)
    op.create_index('ix_ai_rules_adaptive_flag', 'ai_rules', ['adaptive_flag'], unique=False)
    
    # Composite indices for common query patterns
    op.create_index('ix_events_user_timestamp', 'events', ['triggered_by_user_id', 'timestamp'], unique=False)
    op.create_index('ix_events_type_processed', 'events', ['event_type', 'processed_flag'], unique=False)


def downgrade():
    # Drop indices in reverse order
    op.drop_index('ix_events_type_processed', table_name='events')
    op.drop_index('ix_events_user_timestamp', table_name='events')
    op.drop_index('ix_ai_rules_adaptive_flag', table_name='ai_rules')
    op.drop_index('ix_ai_rules_severity_level', table_name='ai_rules')
    op.drop_index('ix_logs_timestamp', table_name='logs')
    op.drop_index('ix_logs_log_type', table_name='logs')
    op.drop_index('ix_events_processed_flag', table_name='events')
    op.drop_index('ix_events_event_type', table_name='events')
    op.drop_index('ix_events_timestamp', table_name='events')
