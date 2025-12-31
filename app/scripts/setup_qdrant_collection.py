"""
Script to setup Qdrant collections for properties and contact preferences.
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from app.database.vectors.qdrant_client import qdrant_manager
from app.config import settings


async def main():
    """Create Qdrant collections."""
    print("🚀 Setting up Qdrant collections...")
    print(f"Qdrant URL: {settings.QDRANT_URL}")
    
    try:
        await qdrant_manager.create_collections()
        print("✅ Collections created successfully!")
        
        # Get collection info
        properties_info = await qdrant_manager.get_collection_info("properties_embeddings")
        contacts_info = await qdrant_manager.get_collection_info("contact_preferences_embeddings")
        
        print("\n📊 Collection Info:")
        print(f"Properties Collection:")
        print(f"  - Points: {properties_info['points_count']}")
        print(f"  - Vectors: {properties_info['vectors_count']}")
        print(f"  - Status: {properties_info['status']}")
        
        print(f"\nContact Preferences Collection:")
        print(f"  - Points: {contacts_info['points_count']}")
        print(f"  - Vectors: {contacts_info['vectors_count']}")
        print(f"  - Status: {contacts_info['status']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())