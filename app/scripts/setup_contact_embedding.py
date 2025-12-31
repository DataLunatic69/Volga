"""
Script to generate embeddings for contact preferences and upload to Qdrant.
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import select
from app.database.session import async_engine
from app.database.models import LeadPreferences, Lead
from app.database.vectors.qdrant_client import qdrant_manager
from app.database.vectors.embeddings import embedding_generator, create_contact_preference_text


async def generate_contact_embeddings():
    """Generate and upload embeddings for all contact preferences."""
    print("👤 Generating contact preference embeddings...")
    
    # Get database session
    async with async_engine.begin() as conn:
        # Fetch all contact preferences
        result = await conn.execute(
            select(LeadPreferences)
        )
        preferences = result.scalars().all()
        
        if not preferences:
            print("⚠️  No contact preferences found")
            return
        
        print(f"Found {len(preferences)} contact preferences to process")
        
        total_processed = 0
        total_errors = 0
        
        for preference in preferences:
            try:
                # Create searchable text
                preference_dict = {
                    "property_type": preference.property_type,
                    "transaction_type": preference.transaction_type,
                    "budget_min": float(preference.budget_min) if preference.budget_min else None,
                    "budget_max": float(preference.budget_max) if preference.budget_max else None,
                    "preferred_locations": preference.preferred_locations or [],
                    "bedrooms_min": preference.bedrooms_min,
                    "bathrooms_min": preference.bathrooms_min,
                    "furnishing": preference.furnishing,
                    "must_have_features": preference.must_have_features or [],
                    "urgency": preference.urgency,
                    "additional_notes": preference.additional_notes
                }
                
                preference_text = create_contact_preference_text(preference_dict)
                
                if not preference_text.strip():
                    print(f"  ⚠️  Skipping contact {preference.contact_id}: No text content")
                    continue
                
                # Generate embedding
                embedding = embedding_generator.generate_embedding(preference_text)
                
                # Get contact info for agency_id
                contact_result = await conn.execute(
                    select(Lead).where(Lead.id == preference.contact_id)
                )
                contact = contact_result.scalar_one_or_none()
                
                if not contact:
                    print(f"  ⚠️  Contact not found for preference {preference.id}")
                    continue
                
                # Prepare payload for Qdrant
                payload = {
                    "contact_id": str(preference.contact_id),
                    "agency_id": str(contact.agency_id),
                    "preference_text": preference_text[:500],  # Truncate
                    "property_type": preference.property_type,
                    "transaction_type": preference.transaction_type,
                    "budget_min": float(preference.budget_min) if preference.budget_min else None,
                    "budget_max": float(preference.budget_max) if preference.budget_max else None,
                    "locations": preference.preferred_locations or [],
                    "must_have_features": preference.must_have_features or [],
                    "urgency": preference.urgency,
                    "updated_at": preference.updated_at.isoformat() if preference.updated_at else None
                }
                
                # Upload to Qdrant
                await qdrant_manager.upsert_contact_preference(
                    contact_id=preference.contact_id,
                    embedding=embedding,
                    payload=payload
                )
                
                total_processed += 1
                print(f"  ✅ Processed contact: {preference.contact_id}")
                
            except Exception as e:
                total_errors += 1
                print(f"  ❌ Error processing contact {preference.contact_id}: {e}")
        
        print(f"\n📊 Summary:")
        print(f"  Total processed: {total_processed}")
        print(f"  Total errors: {total_errors}")
        if len(preferences) > 0:
            print(f"  Success rate: {(total_processed / len(preferences) * 100):.1f}%")


async def main():
    """Main function."""
    try:
        await generate_contact_embeddings()
        print("\n✅ Contact preference embeddings generated successfully!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())