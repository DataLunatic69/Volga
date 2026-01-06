#!/usr/bin/env python3
"""
Test script to verify environment configuration.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from app.config import settings
    from app.core.cache import redis_cache
    import asyncio
    
    def test_config():
        """Test configuration settings."""
        print("=" * 60)
        print("Configuration Test")
        print("=" * 60)
        
        # Database
        print("\n📊 Database:")
        db_url = settings.DATABASE_URL
        if db_url:
            # Mask password in URL
            if "@" in db_url:
                parts = db_url.split("@")
                if ":" in parts[0]:
                    user_pass = parts[0].split(":")
                    masked = f"{user_pass[0]}:****@{parts[1]}"
                    print(f"  URL: {masked}")
                else:
                    print(f"  URL: {db_url[:50]}...")
            else:
                print(f"  URL: {db_url[:50]}...")
        else:
            print("  ❌ DATABASE_URL not set")
        
        # Redis
        print("\n🔴 Redis:")
        redis_url = settings.redis_connection_url
        if redis_url:
            # Mask password
            if "://:" in redis_url:
                masked = redis_url.split("@")[0] + "@****"
                print(f"  URL: {masked}")
            else:
                print(f"  URL: {redis_url}")
        else:
            print("  ❌ Redis URL not configured")
        
        # JWT
        print("\n🔐 JWT:")
        jwt_key = settings.JWT_SECRET_KEY
        if jwt_key and jwt_key != "your-256-bit-secret-key-change-in-production":
            print(f"  Secret Key: ✓ Set ({len(jwt_key)} chars)")
        else:
            print("  ⚠️  Using default JWT_SECRET_KEY - NOT SECURE!")
            print("     Generate with: openssl rand -hex 32")
        
        print(f"  Algorithm: {settings.JWT_ALGORITHM}")
        print(f"  Expiry: {settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES} minutes")
        
        # Email
        print("\n📧 Email (FastMail):")
        if settings.MAIL_SERVER:
            print(f"  Server: {settings.MAIL_SERVER}")
            print(f"  Port: {settings.MAIL_PORT}")
            print(f"  Username: {settings.MAIL_USERNAME or 'Not set'}")
            print(f"  Password: {'✓ Set' if settings.MAIL_PASSWORD else '❌ Not set'}")
            print(f"  From: {settings.MAIL_FROM or 'Not set'}")
            print(f"  From Name: {settings.MAIL_FROM_NAME or 'Not set'}")
            print(f"  STARTTLS: {settings.MAIL_STARTTLS}")
            print(f"  SSL/TLS: {settings.MAIL_SSL_TLS}")
            print(f"  Frontend URL: {settings.FRONTEND_URL}")
        else:
            print("  ⚠️  Email not configured (MAIL_SERVER missing)")
            print("     Email functionality will not work")
        
        # Application
        print("\n⚙️  Application:")
        print(f"  Name: {settings.APP_NAME}")
        print(f"  Version: {settings.APP_VERSION}")
        print(f"  Environment: {settings.ENVIRONMENT}")
        print(f"  Debug: {settings.DEBUG}")
        print(f"  Port: {settings.API_PORT}")
        
        # CORS
        print("\n🌐 CORS:")
        print(f"  Origins: {', '.join(settings.CORS_ORIGINS)}")
        
        print("\n" + "=" * 60)
        
        # Test Redis connection
        print("\nTesting Redis Connection...")
        try:
            async def test_redis():
                await redis_cache.connect()
                if redis_cache.is_connected():
                    print("  ✓ Redis connection successful")
                    await redis_cache.disconnect()
                else:
                    print("  ❌ Redis connection failed")
            
            asyncio.run(test_redis())
        except Exception as e:
            print(f"  ❌ Redis error: {e}")
        
        print("\n" + "=" * 60)
        print("\n✅ Configuration check complete!")
        print("\nNext steps:")
        print("  1. Fix any ❌ errors above")
        print("  2. Start Redis: redis-server (or docker run redis)")
        print("  3. Start FastAPI: uvicorn app.main:app --reload")
        print("  4. Start Celery: celery -A app.workers.celery_app worker --queues=email_queue")
        print("=" * 60)
    
    if __name__ == "__main__":
        test_config()
        
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're in the project root and dependencies are installed.")
    sys.exit(1)

