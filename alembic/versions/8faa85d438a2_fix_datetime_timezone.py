"""fix_datetime_timezone

Revision ID: 8faa85d438a2
Revises: 409416e0fc04
Create Date: 2026-01-01 17:17:30.405982

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8faa85d438a2'
down_revision: Union[str, Sequence[str], None] = '409416e0fc04'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - convert all datetime columns to TIMESTAMP WITH TIME ZONE."""
    # List of all tables that inherit from BaseModel (have created_at and updated_at)
    tables_with_timestamps = [
        'activity_logs',
        'agencies',
        'agency_metrics_daily',
        'agency_users',
        'agent_calendars',
        'agent_performance',
        'ai_agent_sessions',
        'api_keys',
        'auth_users',
        'calendar_events',
        'consent_logs',
        'conversation_state_snapshots',
        'conversations',
        'deals',
        'email_verification_tokens',
        'escalation_rules',
        'lead_preferences',
        'leads',
        'messages',
        'password_reset_tokens',
        'permissions',
        'properties',
        'property_availability',
        'refresh_tokens',
        'role_permissions',
        'roles',
        'user_roles',
        'viewing_feedback',
        'viewings',
    ]
    
    # Alter created_at and updated_at for all tables
    for table_name in tables_with_timestamps:
        # Check if columns exist before altering (in case table doesn't exist yet)
        op.execute(f"""
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = '{table_name}' AND column_name = 'created_at'
                ) THEN
                    ALTER TABLE {table_name} 
                    ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE;
                END IF;
                
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = '{table_name}' AND column_name = 'updated_at'
                ) THEN
                    ALTER TABLE {table_name} 
                    ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE;
                END IF;
            END $$;
        """)


def downgrade() -> None:
    """Downgrade schema - convert datetime columns back to TIMESTAMP WITHOUT TIME ZONE."""
    tables_with_timestamps = [
        'activity_logs',
        'agencies',
        'agency_metrics_daily',
        'agency_users',
        'agent_calendars',
        'agent_performance',
        'ai_agent_sessions',
        'api_keys',
        'auth_users',
        'calendar_events',
        'consent_logs',
        'conversation_state_snapshots',
        'conversations',
        'deals',
        'email_verification_tokens',
        'escalation_rules',
        'lead_preferences',
        'leads',
        'messages',
        'password_reset_tokens',
        'permissions',
        'properties',
        'property_availability',
        'refresh_tokens',
        'role_permissions',
        'roles',
        'user_roles',
        'viewing_feedback',
        'viewings',
    ]
    
    for table_name in tables_with_timestamps:
        op.execute(f"""
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = '{table_name}' AND column_name = 'created_at'
                ) THEN
                    ALTER TABLE {table_name} 
                    ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE;
                END IF;
                
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = '{table_name}' AND column_name = 'updated_at'
                ) THEN
                    ALTER TABLE {table_name} 
                    ALTER COLUMN updated_at TYPE TIMESTAMP WITHOUT TIME ZONE;
                END IF;
            END $$;
        """)
