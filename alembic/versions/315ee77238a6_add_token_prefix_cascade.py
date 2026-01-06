"""add_token_prefix_cascade

Revision ID: 315ee77238a6
Revises: 8faa85d438a2
Create Date: 2026-01-01 20:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '315ee77238a6'
down_revision: Union[str, Sequence[str], None] = '8faa85d438a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add token_prefix columns and CASCADE deletes to token tables."""
    
    # ============================================================
    # 1. Add token_prefix column to refresh_tokens
    # ============================================================
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'refresh_tokens' AND column_name = 'token_prefix'
            ) THEN
                ALTER TABLE refresh_tokens 
                ADD COLUMN token_prefix VARCHAR(8);
                
                -- Create index for O(1) lookup
                CREATE INDEX IF NOT EXISTS ix_refresh_tokens_token_prefix 
                ON refresh_tokens(token_prefix);
            END IF;
        END $$;
    """)
    
    # ============================================================
    # 2. Add token_prefix column to password_reset_tokens
    # ============================================================
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'password_reset_tokens' AND column_name = 'token_prefix'
            ) THEN
                ALTER TABLE password_reset_tokens 
                ADD COLUMN token_prefix VARCHAR(8);
                
                -- Create index for O(1) lookup
                CREATE INDEX IF NOT EXISTS ix_password_reset_tokens_token_prefix 
                ON password_reset_tokens(token_prefix);
            END IF;
        END $$;
    """)
    
    # ============================================================
    # 3. Add token_prefix column to email_verification_tokens
    # ============================================================
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'email_verification_tokens' AND column_name = 'token_prefix'
            ) THEN
                ALTER TABLE email_verification_tokens 
                ADD COLUMN token_prefix VARCHAR(8);
                
                -- Create index for O(1) lookup
                CREATE INDEX IF NOT EXISTS ix_email_verification_tokens_token_prefix 
                ON email_verification_tokens(token_prefix);
            END IF;
        END $$;
    """)
    
    # ============================================================
    # 4. Add CASCADE delete to refresh_tokens.user_id
    # ============================================================
    op.execute("""
        DO $$
        BEGIN
            -- Drop existing foreign key constraint if it exists
            IF EXISTS (
                SELECT 1 FROM information_schema.table_constraints 
                WHERE table_name = 'refresh_tokens' 
                AND constraint_name LIKE '%user_id%'
                AND constraint_type = 'FOREIGN KEY'
            ) THEN
                ALTER TABLE refresh_tokens 
                DROP CONSTRAINT refresh_tokens_user_id_fkey;
            END IF;
            
            -- Add new foreign key with CASCADE
            ALTER TABLE refresh_tokens 
            ADD CONSTRAINT refresh_tokens_user_id_fkey 
            FOREIGN KEY (user_id) 
            REFERENCES auth_users(id) 
            ON DELETE CASCADE;
        END $$;
    """)
    
    # ============================================================
    # 5. Add CASCADE delete to password_reset_tokens.user_id
    # ============================================================
    op.execute("""
        DO $$
        BEGIN
            -- Drop existing foreign key constraint if it exists
            IF EXISTS (
                SELECT 1 FROM information_schema.table_constraints 
                WHERE table_name = 'password_reset_tokens' 
                AND constraint_name LIKE '%user_id%'
                AND constraint_type = 'FOREIGN KEY'
            ) THEN
                ALTER TABLE password_reset_tokens 
                DROP CONSTRAINT password_reset_tokens_user_id_fkey;
            END IF;
            
            -- Add new foreign key with CASCADE
            ALTER TABLE password_reset_tokens 
            ADD CONSTRAINT password_reset_tokens_user_id_fkey 
            FOREIGN KEY (user_id) 
            REFERENCES auth_users(id) 
            ON DELETE CASCADE;
        END $$;
    """)
    
    # ============================================================
    # 6. Add CASCADE delete to email_verification_tokens.user_id
    # ============================================================
    op.execute("""
        DO $$
        BEGIN
            -- Drop existing foreign key constraint if it exists
            IF EXISTS (
                SELECT 1 FROM information_schema.table_constraints 
                WHERE table_name = 'email_verification_tokens' 
                AND constraint_name LIKE '%user_id%'
                AND constraint_type = 'FOREIGN KEY'
            ) THEN
                ALTER TABLE email_verification_tokens 
                DROP CONSTRAINT email_verification_tokens_user_id_fkey;
            END IF;
            
            -- Add new foreign key with CASCADE
            ALTER TABLE email_verification_tokens 
            ADD CONSTRAINT email_verification_tokens_user_id_fkey 
            FOREIGN KEY (user_id) 
            REFERENCES auth_users(id) 
            ON DELETE CASCADE;
        END $$;
    """)
    
    # ============================================================
    # 7. Make token_prefix nullable (existing tokens won't have prefix)
    # New tokens will always have prefix, old ones will be NULL
    # This allows graceful migration - old tokens still work but slower
    # ============================================================
    op.execute("""
        ALTER TABLE refresh_tokens 
        ALTER COLUMN token_prefix DROP NOT NULL;
        
        ALTER TABLE password_reset_tokens 
        ALTER COLUMN token_prefix DROP NOT NULL;
        
        ALTER TABLE email_verification_tokens 
        ALTER COLUMN token_prefix DROP NOT NULL;
    """)


def downgrade() -> None:
    """Remove token_prefix columns and revert CASCADE deletes."""
    
    # Drop indexes
    op.execute("DROP INDEX IF EXISTS ix_refresh_tokens_token_prefix;")
    op.execute("DROP INDEX IF EXISTS ix_password_reset_tokens_token_prefix;")
    op.execute("DROP INDEX IF EXISTS ix_email_verification_tokens_token_prefix;")
    
    # Drop columns
    op.execute("ALTER TABLE refresh_tokens DROP COLUMN IF EXISTS token_prefix;")
    op.execute("ALTER TABLE password_reset_tokens DROP COLUMN IF EXISTS token_prefix;")
    op.execute("ALTER TABLE email_verification_tokens DROP COLUMN IF EXISTS token_prefix;")
    
    # Revert foreign keys (remove CASCADE, add back without CASCADE)
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.table_constraints 
                WHERE table_name = 'refresh_tokens' 
                AND constraint_name = 'refresh_tokens_user_id_fkey'
            ) THEN
                ALTER TABLE refresh_tokens 
                DROP CONSTRAINT refresh_tokens_user_id_fkey;
                
                ALTER TABLE refresh_tokens 
                ADD CONSTRAINT refresh_tokens_user_id_fkey 
                FOREIGN KEY (user_id) 
                REFERENCES auth_users(id);
            END IF;
            
            IF EXISTS (
                SELECT 1 FROM information_schema.table_constraints 
                WHERE table_name = 'password_reset_tokens' 
                AND constraint_name = 'password_reset_tokens_user_id_fkey'
            ) THEN
                ALTER TABLE password_reset_tokens 
                DROP CONSTRAINT password_reset_tokens_user_id_fkey;
                
                ALTER TABLE password_reset_tokens 
                ADD CONSTRAINT password_reset_tokens_user_id_fkey 
                FOREIGN KEY (user_id) 
                REFERENCES auth_users(id);
            END IF;
            
            IF EXISTS (
                SELECT 1 FROM information_schema.table_constraints 
                WHERE table_name = 'email_verification_tokens' 
                AND constraint_name = 'email_verification_tokens_user_id_fkey'
            ) THEN
                ALTER TABLE email_verification_tokens 
                DROP CONSTRAINT email_verification_tokens_user_id_fkey;
                
                ALTER TABLE email_verification_tokens 
                ADD CONSTRAINT email_verification_tokens_user_id_fkey 
                FOREIGN KEY (user_id) 
                REFERENCES auth_users(id);
            END IF;
        END $$;
    """)

