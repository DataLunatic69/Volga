"""Test environment variables."""
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from app.config import settings

print("Environment Variable Check:")
print(f"QDRANT_URL: {settings.QDRANT_URL}")
print(f"QDRANT_API_KEY: {'*' * 20}{settings.QDRANT_API_KEY[-10:] if settings.QDRANT_API_KEY else 'NOT SET'}")
print(f"QDRANT_COLLECTION_NAME: {settings.QDRANT_COLLECTION_NAME}")
print(f"\nAll settings loaded: {bool(settings.QDRANT_URL and settings.QDRANT_API_KEY)}")