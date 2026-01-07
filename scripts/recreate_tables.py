#!/usr/bin/env python3
"""
Script to drop and recreate all database tables with correct schema.
WARNING: This will delete all data!
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from sqlmodel import SQLModel
from app.database.session import async_engine
from app.database.models import *  # Import all models


async def drop_all_tables():
    """Drop all tables."""
    print("Dropping all tables...")
    async with async_engine.begin() as conn:
        # Drop all tables
        await conn.run_sync(SQLModel.metadata.drop_all)
    print("✓ All tables dropped")


async def create_all_tables():
    """Create all tables."""
    print("Creating all tables...")
    async with async_engine.begin() as conn:
        # Create all tables
        await conn.run_sync(SQLModel.metadata.create_all)
    print("✓ All tables created")


async def verify_schema():
    """Verify that datetime columns have timezone."""
    print("\nVerifying schema...")
    async with async_engine.begin() as conn:
        result = await conn.execute(text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'auth_users'
            AND column_name IN ('created_at', 'updated_at', 'email_verified_at', 'last_login_at', 'locked_until')
            ORDER BY column_name;
        """))
        rows = result.fetchall()
        print("\nAuthUsers datetime columns:")
        for row in rows:
            col_name, data_type, is_nullable = row
            timezone_info = "WITH TIME ZONE" if "time" in data_type.lower() else "WITHOUT TIME ZONE"
            print(f"  {col_name}: {data_type} ({timezone_info})")


async def main():
    """Main function."""
    print("=" * 70)
    print("Database Table Recreation Script")
    print("=" * 70)
    print("\n⚠️  WARNING: This will delete ALL data in the database!")
    
    response = input("\nDo you want to continue? (yes/no): ")
    if response.lower() != "yes":
        print("Cancelled.")
        return
    
    try:
        await drop_all_tables()
        await create_all_tables()
        await verify_schema()
        print("\n" + "=" * 70)
        print("✓ Database tables recreated successfully!")
        print("=" * 70)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        await async_engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())

