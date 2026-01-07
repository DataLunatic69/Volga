#!/usr/bin/env python3
"""
Comprehensive test script to verify all configurations and connections.
Tests: Database (Supabase), Redis, Email (SMTP), JWT, Celery, etc.
"""
import sys
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_success(message: str):
    """Print success message."""
    print(f"{Colors.GREEN}✓{Colors.RESET} {message}")

def print_error(message: str):
    """Print error message."""
    print(f"{Colors.RED}✗{Colors.RESET} {message}")

def print_warning(message: str):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠{Colors.RESET} {message}")

def print_info(message: str):
    """Print info message."""
    print(f"{Colors.BLUE}ℹ{Colors.RESET} {message}")

def print_header(title: str):
    """Print section header."""
    print(f"\n{Colors.BOLD}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{title.center(70)}{Colors.RESET}")
    print(f"{Colors.BOLD}{'=' * 70}{Colors.RESET}\n")

def mask_url(url: str) -> str:
    """Mask sensitive information in URLs."""
    if not url:
        return "Not set"
    
    # Mask password in database URL
    if "@" in url:
        parts = url.split("@")
        if ":" in parts[0]:
            user_pass = parts[0].split(":")
            if len(user_pass) > 1:
                masked = f"{user_pass[0]}:****@{parts[1]}"
                return masked
    
    # Mask password in Redis URL
    if "://:" in url:
        return url.split("@")[0] + "@****"
    
    return url


class ConnectionTester:
    """Test all connections and configurations."""
    
    def __init__(self):
        self.results: Dict[str, Dict[str, Any]] = {}
        self.start_time = datetime.now()
        
    async def test_all(self):
        """Run all tests."""
        print_header("NexCell AI Receptionist - Connection & Configuration Test")
        print(f"Started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Test configuration
        await self.test_configuration()
        
        # Test database connection
        await self.test_database()
        
        # Test Redis connection
        await self.test_redis()
        
        # Test email configuration and connection
        await self.test_email()
        
        # Test JWT configuration
        await self.test_jwt()
        
        # Test Celery configuration
        await self.test_celery()
        
        # Test Qdrant vector database
        await self.test_qdrant()
        
        # Print summary
        self.print_summary()
    
    async def test_configuration(self):
        """Test configuration values."""
        print_header("1. Configuration Check")
        
        try:
            from app.config import settings
            
            # Database config
            print_info("Database Configuration:")
            db_url = settings.DATABASE_URL
            if db_url:
                print_success(f"  DATABASE_URL: {mask_url(db_url)}")
            else:
                print_error("  DATABASE_URL not set")
                self.results['database_config'] = {'status': 'fail', 'error': 'DATABASE_URL not set'}
                return
            
            # Redis config
            print_info("Redis Configuration:")
            redis_url = settings.redis_connection_url
            if redis_url:
                print_success(f"  Redis URL: {mask_url(redis_url)}")
            else:
                print_warning("  Redis URL not configured")
            
            # JWT config
            print_info("JWT Configuration:")
            jwt_key = settings.JWT_SECRET_KEY
            if jwt_key and jwt_key != "your-256-bit-secret-key-change-in-production":
                print_success(f"  JWT_SECRET_KEY: Set ({len(jwt_key)} chars)")
            else:
                print_error("  JWT_SECRET_KEY: Using default - NOT SECURE!")
            
            print_success(f"  Algorithm: {settings.JWT_ALGORITHM}")
            print_success(f"  Token Expiry: {settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES} minutes")
            
            # Email config
            print_info("Email Configuration:")
            if settings.MAIL_SERVER:
                print_success(f"  MAIL_SERVER: {settings.MAIL_SERVER}")
                print_success(f"  MAIL_PORT: {settings.MAIL_PORT}")
                print_success(f"  MAIL_USERNAME: {settings.MAIL_USERNAME or 'Not set'}")
                print_success(f"  MAIL_PASSWORD: {'Set' if settings.MAIL_PASSWORD else 'Not set'}")
                print_success(f"  MAIL_FROM: {settings.MAIL_FROM or 'Not set'}")
                print_success(f"  MAIL_FROM_NAME: {settings.MAIL_FROM_NAME or 'Not set'}")
            else:
                print_warning("  Email not configured (MAIL_SERVER missing)")
            
            # Application config
            print_info("Application Configuration:")
            print_success(f"  APP_NAME: {settings.APP_NAME}")
            print_success(f"  ENVIRONMENT: {settings.ENVIRONMENT}")
            print_success(f"  DEBUG: {settings.DEBUG}")
            print_success(f"  API_PORT: {settings.API_PORT}")
            
            # Qdrant config
            print_info("Qdrant Configuration:")
            if settings.QDRANT_URL:
                print_success(f"  QDRANT_URL: {settings.QDRANT_URL}")
                print_success(f"  QDRANT_API_KEY: {'Set' if settings.QDRANT_API_KEY else 'Not set'}")
                print_success(f"  QDRANT_COLLECTION_NAME: {settings.QDRANT_COLLECTION_NAME}")
            else:
                print_warning("  Qdrant not configured (QDRANT_URL missing)")
            
            self.results['configuration'] = {'status': 'pass'}
            
        except Exception as e:
            print_error(f"Configuration check failed: {e}")
            self.results['configuration'] = {'status': 'fail', 'error': str(e)}
    
    async def test_database(self):
        """Test database connection."""
        print_header("2. Database Connection Test (Supabase/PostgreSQL)")
        
        try:
            from app.config import settings
            import asyncpg
            
            db_url = settings.DATABASE_URL
            if not db_url:
                print_error("DATABASE_URL not configured")
                self.results['database'] = {'status': 'fail', 'error': 'DATABASE_URL not set'}
                return
            
            print_info(f"Connecting to: {mask_url(db_url)}")
            
            # Parse database URL using urllib.parse for proper handling
            from urllib.parse import urlparse, unquote
            
            # Remove +asyncpg if present (asyncpg doesn't need it)
            clean_url = db_url.replace("+asyncpg", "")
            
            # Parse URL
            parsed = urlparse(clean_url)
            
            if not parsed.hostname:
                raise Exception("Invalid DATABASE_URL format: missing hostname")
            
            # Extract connection parameters
            user = parsed.username or "postgres"
            password = unquote(parsed.password) if parsed.password else None
            host = parsed.hostname
            port = parsed.port or 5432
            database = parsed.path.lstrip('/') or "postgres"
            
            # Test connection with asyncpg directly
            try:
                conn = await asyncpg.connect(
                    host=host,
                    port=port,
                    user=user,
                    password=password,
                    database=database,
                    timeout=10
                )
                
                # Test query
                version = await conn.fetchval("SELECT version()")
                db_name = await conn.fetchval("SELECT current_database()")
                db_user = await conn.fetchval("SELECT current_user")
                
                print_success("Database connection successful!")
                print_info(f"  PostgreSQL Version: {version.split(',')[0] if version else 'Unknown'}")
                print_info(f"  Database: {db_name}")
                print_info(f"  User: {db_user}")
                
                # Test simple query
                result = await conn.fetchval("SELECT 1")
                if result == 1:
                    print_success("Database query test passed")
                
                await conn.close()
                
                self.results['database'] = {
                    'status': 'pass',
                    'version': version,
                    'database': db_name,
                    'user': db_user
                }
                
            except Exception as e:
                raise Exception(f"Connection test failed: {e}")
            
        except ImportError:
            print_error("asyncpg package not installed")
            print_info("  Install with: pip install asyncpg")
            self.results['database'] = {'status': 'fail', 'error': 'asyncpg not installed'}
        except Exception as e:
            print_error(f"Database connection failed: {e}")
            print_info("  Troubleshooting:")
            print_info("    - Check DATABASE_URL format: postgresql+asyncpg://user:password@host:port/db")
            print_info("    - Verify database is running and accessible")
            print_info("    - Check firewall/network settings")
            print_info("    - For Supabase, use pooler endpoint: aws-1-region.pooler.supabase.com")
            self.results['database'] = {'status': 'fail', 'error': str(e)}
    
    async def test_redis(self):
        """Test Redis connection."""
        print_header("3. Redis Connection Test")
        
        try:
            from app.database.redis import redis_cache
            from app.config import settings
            
            redis_url = settings.redis_connection_url
            if not redis_url:
                print_warning("Redis URL not configured")
                self.results['redis'] = {'status': 'skip', 'reason': 'Not configured'}
                return
            
            print_info(f"Connecting to: {mask_url(redis_url)}")
            
            # Connect
            await redis_cache.connect()
            
            if not redis_cache.is_connected():
                raise Exception("Redis connection failed")
            
            # Test SET/GET
            test_key = "test:connection"
            test_value = f"test-{datetime.now().timestamp()}"
            
            await redis_cache.set(test_key, test_value, ttl=10)
            retrieved = await redis_cache.get(test_key)
            
            if retrieved == test_value:
                print_success("Redis connection successful!")
                print_success("  SET/GET operations working")
                
                # Test DELETE
                await redis_cache.delete(test_key)
                print_success("  DELETE operation working")
                
                # Get Redis info
                try:
                    info = await redis_cache.redis.info()
                    redis_version = info.get('redis_version', 'Unknown')
                    print_info(f"  Redis Version: {redis_version}")
                except Exception:
                    # Info might not be available
                    pass
                
                self.results['redis'] = {'status': 'pass'}
            else:
                raise Exception("Redis SET/GET test failed")
            
            await redis_cache.disconnect()
            
        except Exception as e:
            print_error(f"Redis connection failed: {e}")
            print_info("  Troubleshooting:")
            print_info("    - Check if Redis is running: redis-cli ping")
            print_info("    - Verify REDIS_URL format: redis://host:port/db")
            print_info("    - For cloud Redis, check password and SSL settings")
            print_info("    - Start Redis: docker run -d -p 6379:6379 redis:7")
            self.results['redis'] = {'status': 'fail', 'error': str(e)}
    
    async def test_email(self):
        """Test email configuration and SMTP connection."""
        print_header("4. Email (SMTP) Configuration & Connection Test")
        
        try:
            from app.config import settings
            from app.services.email_service import get_mail_config
            import smtplib
            from email.mime.text import MIMEText
            
            # Check configuration
            if not settings.MAIL_SERVER:
                print_warning("Email not configured (MAIL_SERVER missing)")
                print_info("  Email functionality will be disabled")
                self.results['email'] = {'status': 'skip', 'reason': 'Not configured'}
                return
            
            required_vars = {
                'MAIL_SERVER': settings.MAIL_SERVER,
                'MAIL_USERNAME': settings.MAIL_USERNAME,
                'MAIL_PASSWORD': settings.MAIL_PASSWORD,
                'MAIL_FROM': settings.MAIL_FROM,
            }
            
            missing = [k for k, v in required_vars.items() if not v]
            if missing:
                print_error(f"Missing required email variables: {', '.join(missing)}")
                self.results['email'] = {'status': 'fail', 'error': f'Missing: {missing}'}
                return
            
            print_success("Email configuration complete")
            print_info(f"  Server: {settings.MAIL_SERVER}:{settings.MAIL_PORT}")
            print_info(f"  Username: {settings.MAIL_USERNAME}")
            print_info(f"  From: {settings.MAIL_FROM}")
            print_info(f"  STARTTLS: {settings.MAIL_STARTTLS}")
            print_info(f"  SSL/TLS: {settings.MAIL_SSL_TLS}")
            
            # Test FastMail config
            try:
                mail_config = get_mail_config()
                print_success("FastMail configuration valid")
            except Exception as e:
                print_error(f"FastMail configuration error: {e}")
                self.results['email'] = {'status': 'fail', 'error': str(e)}
                return
            
            # Test SMTP connection (without sending email)
            print_info("Testing SMTP connection...")
            try:
                if settings.MAIL_SSL_TLS:
                    # SSL/TLS connection
                    server = smtplib.SMTP_SSL(settings.MAIL_SERVER, settings.MAIL_PORT, timeout=10)
                else:
                    # STARTTLS connection
                    server = smtplib.SMTP(settings.MAIL_SERVER, settings.MAIL_PORT, timeout=10)
                    if settings.MAIL_STARTTLS:
                        server.starttls()
                
                # Login test
                server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
                print_success("SMTP connection and authentication successful!")
                
                server.quit()
                self.results['email'] = {'status': 'pass'}
                
            except smtplib.SMTPAuthenticationError as e:
                print_error(f"SMTP authentication failed: {e}")
                print_info("  Troubleshooting:")
                print_info("    - Verify MAIL_USERNAME and MAIL_PASSWORD")
                print_info("    - For FastMail, use App Password (not main password)")
                print_info("    - Check MAIL_STARTTLS and MAIL_SSL_TLS settings")
                self.results['email'] = {'status': 'fail', 'error': f'Auth failed: {e}'}
            except Exception as e:
                print_error(f"SMTP connection failed: {e}")
                print_info("  Troubleshooting:")
                print_info("    - Check MAIL_SERVER and MAIL_PORT")
                print_info("    - Verify network connectivity")
                print_info("    - Check firewall settings")
                self.results['email'] = {'status': 'fail', 'error': str(e)}
            
        except Exception as e:
            print_error(f"Email test failed: {e}")
            self.results['email'] = {'status': 'fail', 'error': str(e)}
    
    async def test_jwt(self):
        """Test JWT configuration and token generation."""
        print_header("5. JWT Configuration Test")
        
        try:
            from app.config import settings
            from app.auth.jwt import create_access_token, verify_token
            from uuid import uuid4
            
            # Check secret key
            jwt_key = settings.JWT_SECRET_KEY
            if not jwt_key or jwt_key == "your-256-bit-secret-key-change-in-production":
                print_error("JWT_SECRET_KEY is using default value - NOT SECURE!")
                print_info("  Generate secure key: openssl rand -hex 32")
                self.results['jwt'] = {'status': 'fail', 'error': 'Using default secret key'}
                return
            
            print_success(f"JWT_SECRET_KEY: Set ({len(jwt_key)} chars)")
            print_success(f"Algorithm: {settings.JWT_ALGORITHM}")
            print_success(f"Token Expiry: {settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES} minutes")
            
            # Test token creation
            test_user_id = str(uuid4())
            test_email = "test@example.com"
            
            token = create_access_token(
                user_id=test_user_id,
                email=test_email
            )
            
            if token:
                print_success("Access token creation successful")
                
                # Test token verification
                try:
                    payload = await verify_token(token)
                    if payload.get("sub") == test_user_id:
                        print_success("Token verification successful")
                        print_success("  User ID matches")
                        print_success("  Token structure valid")
                        self.results['jwt'] = {'status': 'pass'}
                    else:
                        raise Exception("Token payload mismatch")
                except Exception as e:
                    print_error(f"Token verification failed: {e}")
                    self.results['jwt'] = {'status': 'fail', 'error': str(e)}
            else:
                raise Exception("Token creation returned None")
            
        except Exception as e:
            print_error(f"JWT test failed: {e}")
            self.results['jwt'] = {'status': 'fail', 'error': str(e)}
    
    async def test_celery(self):
        """Test Celery configuration."""
        print_header("6. Celery Configuration Test")
        
        try:
            from app.workers.celery_app import celery_app
            from app.config import settings
            
            # Check Redis for Celery broker
            redis_url = settings.redis_connection_url
            if not redis_url:
                print_warning("Celery requires Redis - not configured")
                self.results['celery'] = {'status': 'skip', 'reason': 'Redis not configured'}
                return
            
            # Check Celery app configuration
            broker_url = celery_app.conf.broker_url
            backend_url = celery_app.conf.result_backend
            
            print_info(f"Broker URL: {mask_url(broker_url)}")
            print_info(f"Backend URL: {mask_url(backend_url)}")
            
            # Test broker connection
            try:
                inspect = celery_app.control.inspect()
                active_queues = inspect.active_queues()
                
                if active_queues is not None:
                    print_success("Celery broker connection successful!")
                    print_info("  Note: This only tests broker connectivity")
                    print_info("  Start worker: celery -A app.workers.celery_app worker --queues=email_queue")
                else:
                    print_warning("Celery broker connection test inconclusive")
                    print_info("  Start a worker to verify full functionality")
                    self.results['celery'] = {'status': 'partial', 'note': 'No active workers'}
                    return
                
                self.results['celery'] = {'status': 'pass'}
                
            except Exception as e:
                print_warning(f"Celery broker test: {e}")
                print_info("  This is normal if no workers are running")
                print_info("  Start worker: celery -A app.workers.celery_app worker --queues=email_queue")
                self.results['celery'] = {'status': 'partial', 'note': 'No workers running'}
            
        except Exception as e:
            print_error(f"Celery test failed: {e}")
            self.results['celery'] = {'status': 'fail', 'error': str(e)}
    
    async def test_qdrant(self):
        """Test Qdrant vector database connection."""
        print_header("7. Qdrant Vector Database Test")
        
        try:
            from app.config import settings
            
            # Check configuration
            if not settings.QDRANT_URL:
                print_warning("Qdrant not configured (QDRANT_URL missing)")
                print_info("  Vector search functionality will be disabled")
                self.results['qdrant'] = {'status': 'skip', 'reason': 'Not configured'}
                return
            
            if not settings.QDRANT_API_KEY:
                print_error("QDRANT_API_KEY not set (required when QDRANT_URL is provided)")
                self.results['qdrant'] = {'status': 'fail', 'error': 'QDRANT_API_KEY missing'}
                return
            
            print_success("Qdrant configuration found")
            print_info(f"  URL: {settings.QDRANT_URL}")
            print_info(f"  API Key: {'Set' if settings.QDRANT_API_KEY else 'Not set'}")
            print_info(f"  Collection Name: {settings.QDRANT_COLLECTION_NAME}")
            
            # Test connection
            try:
                from qdrant_client import QdrantClient
                from qdrant_client.http.exceptions import UnexpectedResponse
                
                print_info("Connecting to Qdrant...")
                
                # Create client
                client = QdrantClient(
                    url=settings.QDRANT_URL,
                    api_key=settings.QDRANT_API_KEY,
                    timeout=10
                )
                
                # Test connection by getting collections
                collections = client.get_collections()
                
                if collections is not None:
                    print_success("Qdrant connection successful!")
                    
                    # List collections
                    collection_names = [col.name for col in collections.collections]
                    print_info(f"  Available collections: {len(collection_names)}")
                    
                    if collection_names:
                        print_info(f"  Collections: {', '.join(collection_names[:5])}")
                        if len(collection_names) > 5:
                            print_info(f"    ... and {len(collection_names) - 5} more")
                    else:
                        print_warning("  No collections found")
                        print_info("    Run: python app/scripts/setup_qdrant_collection.py")
                    
                    # Check if default collection exists
                    default_collection = settings.QDRANT_COLLECTION_NAME
                    if default_collection in collection_names:
                        try:
                            collection_info = client.get_collection(default_collection)
                            print_success(f"  Default collection '{default_collection}' exists")
                            print_info(f"    Points: {collection_info.points_count}")
                            print_info(f"    Vectors: {collection_info.vectors_count}")
                            print_info(f"    Status: {collection_info.status}")
                        except Exception as e:
                            print_warning(f"  Could not get collection info: {e}")
                    else:
                        print_warning(f"  Default collection '{default_collection}' not found")
                        print_info("    Run: python app/scripts/setup_qdrant_collection.py")
                    
                    # Test a simple operation (get cluster info if available)
                    try:
                        cluster_info = client.get_cluster_info()
                        if cluster_info:
                            print_success("  Cluster info retrieved")
                    except:
                        # Cluster info might not be available in cloud instances
                        pass
                    
                    self.results['qdrant'] = {
                        'status': 'pass',
                        'collections': len(collection_names),
                        'default_exists': default_collection in collection_names
                    }
                else:
                    raise Exception("Failed to retrieve collections")
                
            except UnexpectedResponse as e:
                print_error(f"Qdrant API error: {e}")
                print_info("  Troubleshooting:")
                print_info("    - Verify QDRANT_URL is correct")
                print_info("    - Check QDRANT_API_KEY is valid")
                print_info("    - Ensure API key has proper permissions")
                self.results['qdrant'] = {'status': 'fail', 'error': f'API error: {e}'}
            except Exception as e:
                print_error(f"Qdrant connection failed: {e}")
                print_info("  Troubleshooting:")
                print_info("    - Check QDRANT_URL format: https://your-cluster.qdrant.io")
                print_info("    - Verify QDRANT_API_KEY is correct")
                print_info("    - Check network connectivity")
                print_info("    - For cloud Qdrant, ensure URL includes protocol (https://)")
                self.results['qdrant'] = {'status': 'fail', 'error': str(e)}
            
        except ImportError:
            print_error("qdrant-client package not installed")
            print_info("  Install with: pip install qdrant-client")
            self.results['qdrant'] = {'status': 'fail', 'error': 'Package not installed'}
        except Exception as e:
            print_error(f"Qdrant test failed: {e}")
            self.results['qdrant'] = {'status': 'fail', 'error': str(e)}
    
    def print_summary(self):
        """Print test summary."""
        print_header("Test Summary")
        
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        # Count results
        passed = sum(1 for r in self.results.values() if r.get('status') == 'pass')
        failed = sum(1 for r in self.results.values() if r.get('status') == 'fail')
        skipped = sum(1 for r in self.results.values() if r.get('status') in ('skip', 'partial'))
        total = len(self.results)
        
        print(f"\nTotal Tests: {total}")
        print_success(f"Passed: {passed}")
        if failed > 0:
            print_error(f"Failed: {failed}")
        if skipped > 0:
            print_warning(f"Skipped/Partial: {skipped}")
        
        print(f"\nDuration: {duration:.2f} seconds")
        
        # Detailed results
        print("\nDetailed Results:")
        for test_name, result in self.results.items():
            status = result.get('status')
            if status == 'pass':
                print_success(f"  {test_name}: PASS")
            elif status == 'fail':
                print_error(f"  {test_name}: FAIL")
                if 'error' in result:
                    print(f"    Error: {result['error']}")
            elif status == 'skip':
                print_warning(f"  {test_name}: SKIPPED")
                if 'reason' in result:
                    print(f"    Reason: {result['reason']}")
            elif status == 'partial':
                print_warning(f"  {test_name}: PARTIAL")
                if 'note' in result:
                    print(f"    Note: {result['note']}")
        
        # Recommendations
        print("\n" + "=" * 70)
        if failed == 0 and skipped == 0:
            print_success("All tests passed! You're ready to start the application.")
        elif failed == 0:
            print_warning("Some optional tests were skipped, but core functionality is ready.")
        else:
            print_error("Some tests failed. Please fix the issues above before starting the application.")
        
        print("\nNext Steps:")
        if self.results.get('database', {}).get('status') == 'pass':
            print("  ✓ Database is ready")
        else:
            print("  ✗ Fix database connection")
        
        if self.results.get('redis', {}).get('status') == 'pass':
            print("  ✓ Redis is ready")
        else:
            print("  ✗ Fix Redis connection")
        
        if self.results.get('email', {}).get('status') == 'pass':
            print("  ✓ Email is configured")
        elif self.results.get('email', {}).get('status') == 'skip':
            print("  ⚠ Email is optional (not configured)")
        else:
            print("  ✗ Fix email configuration")
        
        if self.results.get('qdrant', {}).get('status') == 'pass':
            print("  ✓ Qdrant vector database is ready")
        elif self.results.get('qdrant', {}).get('status') == 'skip':
            print("  ⚠ Qdrant is optional (not configured)")
        else:
            print("  ✗ Fix Qdrant configuration")
        
        print("\nStart Services:")
        print("  1. FastAPI: uvicorn app.main:app --reload")
        print("  2. Celery: celery -A app.workers.celery_app worker --loglevel=info --queues=email_queue")
        print("=" * 70 + "\n")


async def main():
    """Main entry point."""
    tester = ConnectionTester()
    await tester.test_all()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print_error(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

