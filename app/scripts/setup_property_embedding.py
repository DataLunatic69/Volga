"""
Script to generate embeddings for all properties and upload to Qdrant.
"""
import asyncio
import sys
from pathlib import Path
from uuid import UUID

# Add project root to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import select
from app.database.session import get_db, async_engine
from app.database.models import Property
from app.database.vectors.qdrant_client import qdrant_manager
from app.database.vectors.embeddings import embedding_generator, create_property_text


async def generate_property_embeddings():
    """Generate and upload embeddings for all properties."""
    print("🏠 Generating property embeddings...")
    
    # Get database session
    async with async_engine.begin() as conn:
        # Fetch all available properties
        result = await conn.execute(
            select(Property).where(Property.status == "available")
        )
        properties = result.scalars().all()
        
        if not properties:
            print("⚠️  No properties found")
            return
        
        print(f"Found {len(properties)} properties to process")
        
        # Process properties in batches
        batch_size = 50
        total_processed = 0
        total_errors = 0
        
        for i in range(0, len(properties), batch_size):
            batch = properties[i:i + batch_size]
            print(f"\nProcessing batch {i//batch_size + 1} ({len(batch)} properties)...")
            
            for property in batch:
                try:
                    # Create searchable text
                    property_dict = {
                        "title": property.title,
                        "description": property.description,
                        "property_type": property.property_type,
                        "transaction_type": property.transaction_type,
                        "area_name": property.area_name,
                        "bedrooms": property.bedrooms,
                        "bathrooms": property.bathrooms,
                        "price": float(property.price) if property.price else None,
                        "price_period": property.price_period,
                        "furnishing": property.furnishing,
                        "features": property.features or []
                    }
                    
                    property_text = create_property_text(property_dict)
                    
                    if not property_text.strip():
                        print(f"  ⚠️  Skipping property {property.id}: No text content")
                        continue
                    
                    # Generate embedding
                    embedding = embedding_generator.generate_embedding(property_text)
                    
                    # Prepare payload for Qdrant
                    payload = {
                        "property_id": str(property.id),
                        "agency_id": str(property.agency_id),
                        "title": property.title,
                        "description": property.description[:500] if property.description else "",  # Truncate
                        "property_type": property.property_type,
                        "transaction_type": property.transaction_type,
                        "price": float(property.price) if property.price else None,
                        "bedrooms": property.bedrooms,
                        "bathrooms": property.bathrooms,
                        "area_name": property.area_name,
                        "features": property.features or [],
                        "status": property.status,
                        "updated_at": property.updated_at.isoformat() if property.updated_at else None
                    }
                    
                    # Upload to Qdrant
                    await qdrant_manager.upsert_property(
                        property_id=property.id,
                        embedding=embedding,
                        payload=payload
                    )
                    
                    total_processed += 1
                    print(f"  ✅ Processed: {property.title[:50]}...")
                    
                except Exception as e:
                    total_errors += 1
                    print(f"  ❌ Error processing property {property.id}: {e}")
        
        print(f"\n📊 Summary:")
        print(f"  Total processed: {total_processed}")
        print(f"  Total errors: {total_errors}")
        print(f"  Success rate: {(total_processed / len(properties) * 100):.1f}%")


async def main():
    """Main function."""
    try:
        await generate_property_embeddings()
        print("\n✅ Property embeddings generated successfully!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())