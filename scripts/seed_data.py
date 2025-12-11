"""
Database seeding script with sample data
File: scripts/seed_data.py

Run with: python -m scripts.seed_data
"""
from datetime import datetime, timedelta, date
from uuid import UUID
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from app.database.session import async_engine, create_db_and_tables
from app.database.models import (
    Agency, User, Lead, Property, PropertyMedia, 
    Conversation, Message, Booking, Consent, AgentCalendar
)


async def seed_agencies(session: AsyncSession) -> list[Agency]:
    """Create sample agencies"""
    agencies = [
        Agency(
            name="Prime London Properties",
            whatsapp_business_account_id="44207123456",
            phone_number="+442071234567",
            email="info@primelondonprop.co.uk"
        ),
        Agency(
            name="Urban Living Estates",
            whatsapp_business_account_id="44207654321",
            phone_number="+442076543210",
            email="contact@urbanliving.co.uk"
        ),
        Agency(
            name="Riverside Realty",
            whatsapp_business_account_id="44208111222",
            phone_number="+442081112222",
            email="hello@riversiderealty.co.uk"
        ),
    ]
    
    for agency in agencies:
        session.add(agency)
    await session.commit()
    
    for agency in agencies:
        await session.refresh(agency)
    
    print(f"✅ Created {len(agencies)} agencies")
    return agencies


async def seed_users(session: AsyncSession, agencies: list[Agency]) -> list[User]:
    """Create sample agents and staff"""
    users = [
        User(
            agency_id=agencies[0].id,
            name="Sarah Mitchell",
            email="sarah.mitchell@primelondonprop.co.uk",
            phone="+447700123456",
            role="agent"
        ),
        User(
            agency_id=agencies[0].id,
            name="James Wilson",
            email="james.wilson@primelondonprop.co.uk",
            phone="+447700123457",
            role="agent"
        ),
        User(
            agency_id=agencies[0].id,
            name="Emma Thompson",
            email="emma.thompson@primelondonprop.co.uk",
            phone="+447700123458",
            role="admin"
        ),
        User(
            agency_id=agencies[1].id,
            name="Oliver Davies",
            email="oliver.davies@urbanliving.co.uk",
            phone="+447700234567",
            role="agent"
        ),
        User(
            agency_id=agencies[1].id,
            name="Sophie Anderson",
            email="sophie.anderson@urbanliving.co.uk",
            phone="+447700234568",
            role="agent"
        ),
    ]
    
    for user in users:
        session.add(user)
    await session.commit()
    
    for user in users:
        await session.refresh(user)
    
    print(f"✅ Created {len(users)} users")
    return users


async def seed_leads(session: AsyncSession, agencies: list[Agency]) -> list[Lead]:
    """Create sample leads"""
    leads = [
        Lead(
            agency_id=agencies[0].id,
            phone="+447800111222",
            email="john.doe@email.com",
            name="John Doe",
            budget_min=180000,
            budget_max=250000,
            preferred_areas={"areas": ["Angel", "Islington", "King's Cross"]},
            bedrooms=2,
            move_in_date=date.today() + timedelta(days=30),
            lead_score=85,
            status="qualified"
        ),
        Lead(
            agency_id=agencies[0].id,
            phone="+447800222333",
            email="alice.smith@email.com",
            name="Alice Smith",
            budget_min=150000,
            budget_max=200000,
            preferred_areas={"areas": ["Shoreditch", "Hoxton", "Old Street"]},
            bedrooms=1,
            move_in_date=date.today() + timedelta(days=14),
            lead_score=92,
            status="viewing_scheduled"
        ),
        Lead(
            agency_id=agencies[0].id,
            phone="+447800333444",
            name="Robert Brown",
            budget_min=200000,
            budget_max=300000,
            preferred_areas={"areas": ["Camden", "Chalk Farm"]},
            bedrooms=2,
            lead_score=65,
            status="contacted"
        ),
        Lead(
            agency_id=agencies[1].id,
            phone="+447800444555",
            email="emily.jones@email.com",
            name="Emily Jones",
            budget_min=250000,
            budget_max=350000,
            preferred_areas={"areas": ["Canary Wharf", "Docklands"]},
            bedrooms=3,
            move_in_date=date.today() + timedelta(days=60),
            lead_score=78,
            status="qualified"
        ),
        Lead(
            agency_id=agencies[1].id,
            phone="+447800555666",
            name="Michael Taylor",
            budget_min=120000,
            budget_max=160000,
            preferred_areas={"areas": ["Stratford", "Hackney Wick"]},
            bedrooms=1,
            lead_score=55,
            status="new"
        ),
    ]
    
    for lead in leads:
        session.add(lead)
    await session.commit()
    
    for lead in leads:
        await session.refresh(lead)
    
    print(f"✅ Created {len(leads)} leads")
    return leads


async def seed_properties(session: AsyncSession, agencies: list[Agency]) -> list[Property]:
    """Create sample properties with rich descriptions for vector embeddings"""
    properties = [
        Property(
            agency_id=agencies[0].id,
            title="Stunning 2-Bed Apartment in Angel with Private Balcony",
            description="""Beautifully presented two-bedroom apartment located in the heart of Angel, 
            offering contemporary living spaces with high-quality finishes throughout. The property features 
            a spacious open-plan kitchen and living area with modern integrated appliances, two double bedrooms 
            with built-in wardrobes, and a stylish family bathroom. The private balcony offers pleasant views 
            over the tree-lined street. The development includes a secure entry system, bike storage, and is 
            just moments from Upper Street with its excellent selection of restaurants, bars, and boutiques. 
            Angel tube station (Northern Line) is a 5-minute walk away, providing excellent transport links 
            to the City and West End. Available immediately with no onward chain.""",
            address={
                "line1": "45 Liverpool Road",
                "area": "Angel",
                "city": "London",
                "postcode": "N1 0RW",
                "coordinates": {"lat": 51.5364, "lon": -0.1058}
            },
            price=220000,
            bedrooms=2,
            bathrooms=1,
            area_sqft=850,
            property_type="apartment",
            furnishing="unfurnished",
            amenities={"features": ["balcony", "bike_storage", "secure_entry", "double_glazing", "central_heating"]},
            availability_status="available",
            available_from=date.today()
        ),
        Property(
            agency_id=agencies[0].id,
            title="Modern 1-Bed Studio in Shoreditch with Gym Access",
            description="""Exceptional one-bedroom studio apartment situated in a sought-after Shoreditch 
            development. This modern property combines style and functionality, featuring an open-plan living 
            area with a sleek fitted kitchen, a dedicated sleeping area with ample storage, and a contemporary 
            bathroom with walk-in shower. Residents benefit from access to a fully equipped gymnasium, 
            24-hour concierge service, and secure underground parking (available at additional cost). The 
            location is perfect for city professionals, with Old Street station just 8 minutes away, and 
            surrounded by Shoreditch's vibrant scene including Boxpark, restaurants, and nightlife.""",
            address={
                "line1": "The Forge, 133 Shoreditch High Street",
                "area": "Shoreditch",
                "city": "London",
                "postcode": "E1 6JE",
                "coordinates": {"lat": 51.5255, "lon": -0.0754}
            },
            price=175000,
            bedrooms=1,
            bathrooms=1,
            area_sqft=580,
            property_type="studio",
            furnishing="unfurnished",
            amenities={"features": ["gym", "concierge", "parking_available", "double_glazing", "lift"]},
            availability_status="available",
            available_from=date.today() + timedelta(days=14)
        ),
        Property(
            agency_id=agencies[0].id,
            title="Spacious 2-Bed Victorian Conversion in Camden Town",
            description="""Charming two-bedroom Victorian conversion flat on the second floor of a beautiful 
            period building in Camden Town. This bright and airy apartment retains many original features 
            including high ceilings, sash windows, and ornate cornicing, while being tastefully modernized.""",
            address={
                "line1": "78 Kentish Town Road",
                "area": "Camden",
                "city": "London",
                "postcode": "NW1 9PS",
                "coordinates": {"lat": 51.5450, "lon": -0.1426}
            },
            price=240000,
            bedrooms=2,
            bathrooms=1,
            area_sqft=920,
            property_type="apartment",
            furnishing="part_furnished",
            amenities={"features": ["period_features", "high_ceilings", "bay_windows", "near_transport"]},
            availability_status="available",
            available_from=date.today() + timedelta(days=21)
        ),
        Property(
            agency_id=agencies[1].id,
            title="Luxury 3-Bed Riverside Apartment with Stunning Thames Views",
            description="""An exceptional three-bedroom apartment on the 15th floor of a prestigious riverside 
            development in Canary Wharf. This stunning property offers breathtaking panoramic views across the 
            Thames and city skyline from floor-to-ceiling windows.""",
            address={
                "line1": "Pan Peninsula Square",
                "area": "Canary Wharf",
                "city": "London",
                "postcode": "E14 9HL",
                "coordinates": {"lat": 51.5007, "lon": -0.0102}
            },
            price=450000,
            bedrooms=3,
            bathrooms=2,
            area_sqft=1450,
            property_type="apartment",
            furnishing="furnished",
            amenities={"features": ["river_views", "swimming_pool", "gym", "concierge", "parking", "balcony", "spa"]},
            availability_status="available",
            available_from=date.today()
        ),
        Property(
            agency_id=agencies[1].id,
            title="Affordable 1-Bed in Stratford with Olympic Park Views",
            description="""Excellent value one-bedroom apartment in a modern development overlooking Queen 
            Elizabeth Olympic Park in Stratford. This well-maintained property features an open-plan living 
            area with integrated kitchen.""",
            address={
                "line1": "Victory Parade, Stratford",
                "area": "Stratford",
                "city": "London",
                "postcode": "E20 1FS",
                "coordinates": {"lat": 51.5433, "lon": 0.0030}
            },
            price=145000,
            bedrooms=1,
            bathrooms=1,
            area_sqft=550,
            property_type="apartment",
            furnishing="unfurnished",
            amenities={"features": ["park_views", "bike_storage", "secure_entry", "near_shopping", "transport_links"]},
            availability_status="available",
            available_from=date.today() + timedelta(days=7)
        ),
    ]
    
    for prop in properties:
        session.add(prop)
    await session.commit()
    
    for prop in properties:
        await session.refresh(prop)
    
    print(f"✅ Created {len(properties)} properties")
    return properties


async def seed_property_media(session: AsyncSession, properties: list[Property]) -> list[PropertyMedia]:
    """Create sample property media entries"""
    media = []
    
    for i, url in enumerate([
        "https://example.com/properties/angel-apt/living-room.jpg",
        "https://example.com/properties/angel-apt/bedroom.jpg",
        "https://example.com/properties/angel-apt/kitchen.jpg",
        "https://example.com/properties/angel-apt/balcony.jpg",
    ]):
        media.append(PropertyMedia(
            property_id=properties[0].id,
            media_type="image",
            url=url,
            caption=f"Angel Property View {i+1}",
            order_index=i
        ))
    
    for i, url in enumerate([
        "https://example.com/properties/shoreditch-studio/main.jpg",
        "https://example.com/properties/shoreditch-studio/kitchen.jpg",
        "https://example.com/properties/shoreditch-studio/bathroom.jpg",
    ]):
        media.append(PropertyMedia(
            property_id=properties[1].id,
            media_type="image",
            url=url,
            caption=f"Shoreditch Studio View {i+1}",
            order_index=i
        ))
    
    for m in media:
        session.add(m)
    await session.commit()
    
    print(f"✅ Created {len(media)} property media entries")
    return media


async def seed_conversations_and_messages(session: AsyncSession, leads: list[Lead]) -> tuple[list[Conversation], list[Message]]:
    """Create sample conversations and messages"""
    conversations = []
    messages = []
    
    conv1 = Conversation(
        lead_id=leads[0].id,
        channel="whatsapp",
        status="active",
        last_message_at=datetime.utcnow() - timedelta(hours=2)
    )
    session.add(conv1)
    await session.commit()
    await session.refresh(conv1)
    conversations.append(conv1)
    
    conv1_messages = [
        Message(
            conversation_id=conv1.id,
            direction="inbound",
            message_type="text",
            content="Hi, I'm looking for a 2-bed flat in Angel under £2500",
            timestamp=datetime.utcnow() - timedelta(hours=3),
            platform_message_id="wamid.001",
            status="read"
        ),
        Message(
            conversation_id=conv1.id,
            direction="outbound",
            message_type="text",
            content="Hello! I'm the AI assistant for Prime London Properties. I can help you find the perfect property.",
            timestamp=datetime.utcnow() - timedelta(hours=3) + timedelta(seconds=5),
            platform_message_id="wamid.002",
            status="read"
        ),
    ]
    
    for msg in conv1_messages:
        session.add(msg)
        messages.append(msg)
    
    conv2 = Conversation(
        lead_id=leads[1].id,
        channel="whatsapp",
        status="active",
        last_message_at=datetime.utcnow() - timedelta(days=1)
    )
    session.add(conv2)
    await session.commit()
    await session.refresh(conv2)
    conversations.append(conv2)
    
    conv2_messages = [
        Message(
            conversation_id=conv2.id,
            direction="inbound",
            message_type="text",
            content="Looking for 1 bed in Shoreditch, budget £1800",
            timestamp=datetime.utcnow() - timedelta(days=2),
            platform_message_id="wamid.101",
            status="read"
        ),
        Message(
            conversation_id=conv2.id,
            direction="outbound",
            message_type="text",
            content="Perfect! I have a modern studio in Shoreditch with gym access for £1,750/month.",
            timestamp=datetime.utcnow() - timedelta(days=2) + timedelta(minutes=2),
            platform_message_id="wamid.102",
            status="read"
        ),
    ]
    
    for msg in conv2_messages:
        session.add(msg)
        messages.append(msg)
    
    await session.commit()
    print(f"✅ Created {len(conversations)} conversations with {len(messages)} messages")
    return conversations, messages


async def seed_bookings(session: AsyncSession, leads: list[Lead], properties: list[Property], users: list[User]) -> list[Booking]:
    """Create sample viewing bookings"""
    bookings = [
        Booking(
            lead_id=leads[1].id,
            property_id=properties[1].id,
            agent_id=users[0].id,
            start_time=datetime.utcnow() + timedelta(days=1, hours=14),
            end_time=datetime.utcnow() + timedelta(days=1, hours=14, minutes=30),
            status="scheduled",
            meeting_point="Property entrance, 133 Shoreditch High Street",
            notes="Lead is interested in gym facilities"
        ),
        Booking(
            lead_id=leads[0].id,
            property_id=properties[0].id,
            agent_id=users[1].id,
            start_time=datetime.utcnow() + timedelta(days=3, hours=11),
            end_time=datetime.utcnow() + timedelta(days=3, hours=11, minutes=30),
            status="scheduled",
            meeting_point="45 Liverpool Road, building reception",
            notes="Lead interested in balcony"
        ),
    ]
    
    for booking in bookings:
        session.add(booking)
    await session.commit()
    
    for booking in bookings:
        await session.refresh(booking)
    
    print(f"✅ Created {len(bookings)} bookings")
    return bookings


async def seed_consents(session: AsyncSession, leads: list[Lead]) -> list[Consent]:
    """Create sample GDPR consent records"""
    consents = [
        Consent(
            lead_id=leads[0].id,
            consent_type="data_processing",
            granted=True,
            timestamp=datetime.utcnow() - timedelta(hours=3),
            consent_text="I agree to Prime London Properties using my contact details.",
            ip_address="92.40.123.45"
        ),
        Consent(
            lead_id=leads[1].id,
            consent_type="data_processing",
            granted=True,
            timestamp=datetime.utcnow() - timedelta(days=2),
            consent_text="I consent to my data being used to find suitable properties.",
            ip_address="86.142.78.90"
        ),
    ]
    
    for consent in consents:
        session.add(consent)
    await session.commit()
    
    print(f"✅ Created {len(consents)} consent records")
    return consents


async def seed_agent_calendars(session: AsyncSession, users: list[User], bookings: list[Booking]) -> list[AgentCalendar]:
    """Create sample calendar events for agents"""
    events = []
    
    for booking in bookings:
        events.append(AgentCalendar(
            agent_id=booking.agent_id,
            event_id=f"gcal_{booking.id}",
            title=f"Property Viewing",
            start_time=booking.start_time,
            end_time=booking.end_time,
            event_type="viewing",
            status="scheduled"
        ))
    
    events.extend([
        AgentCalendar(
            agent_id=users[0].id,
            title="Team Meeting",
            start_time=datetime.utcnow() + timedelta(days=2, hours=9),
            end_time=datetime.utcnow() + timedelta(days=2, hours=10),
            event_type="meeting",
            status="scheduled"
        ),
    ])
    
    for event in events:
        session.add(event)
    await session.commit()
    
    print(f"✅ Created {len(events)} calendar events")
    return events


async def seed_all():
    """Main function to seed all sample data"""
    print("\n🌱 Starting database seeding...\n")
    
    # Create tables first
    await create_db_and_tables()
    
    # Create session factory
    async_session = async_sessionmaker(
        async_engine, 
        class_=AsyncSession, 
        expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            # Seed in order of dependencies
            agencies = await seed_agencies(session)
            users = await seed_users(session, agencies)
            leads = await seed_leads(session, agencies)
            properties = await seed_properties(session, agencies)
            property_media = await seed_property_media(session, properties)
            conversations, messages = await seed_conversations_and_messages(session, leads)
            bookings = await seed_bookings(session, leads, properties, users)
            consents = await seed_consents(session, leads)
            calendar_events = await seed_agent_calendars(session, users, bookings)
            
            print("\n✅ Database seeding completed successfully!")
            print(f"""
    Summary:
    --------
    📊 {len(agencies)} Agencies
    👥 {len(users)} Users (Agents/Staff)
    🎯 {len(leads)} Leads
    🏠 {len(properties)} Properties
    🖼️  {len(property_media)} Property Media
    💬 {len(conversations)} Conversations
    ✉️  {len(messages)} Messages
    📅 {len(bookings)} Bookings
    ✅ {len(consents)} Consent Records
    📆 {len(calendar_events)} Calendar Events
            """)
        except Exception as e:
            print(f"\n❌ Error during seeding: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(seed_all())