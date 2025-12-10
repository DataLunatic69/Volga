"""
Database seeding script with sample data
File: data/seed_data.py

Run with: python -m data.seed_data
"""
from datetime import datetime, timedelta, date
from uuid import UUID
from sqlmodel import Session
from app.database.session import engine, create_db_and_tables
from app.database.models import (
    Agency, User, Lead, Property, PropertyMedia, 
    Conversation, Message, Booking, Consent, AgentCalendar
)


def seed_agencies(session: Session) -> list[Agency]:
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
    session.commit()
    
    for agency in agencies:
        session.refresh(agency)
    
    print(f"✅ Created {len(agencies)} agencies")
    return agencies


def seed_users(session: Session, agencies: list[Agency]) -> list[User]:
    """Create sample agents and staff"""
    users = [
        # Prime London Properties agents
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
        # Urban Living Estates agents
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
    session.commit()
    
    for user in users:
        session.refresh(user)
    
    print(f"✅ Created {len(users)} users")
    return users


def seed_leads(session: Session, agencies: list[Agency]) -> list[Lead]:
    """Create sample leads"""
    leads = [
        Lead(
            agency_id=agencies[0].id,
            phone="+447800111222",
            email="john.doe@email.com",
            name="John Doe",
            budget_min=180000,  # £1800/month in pence
            budget_max=250000,  # £2500/month in pence
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
    session.commit()
    
    for lead in leads:
        session.refresh(lead)
    
    print(f"✅ Created {len(leads)} leads")
    return leads


def seed_properties(session: Session, agencies: list[Agency]) -> list[Property]:
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
            price=220000,  # £2200/month
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
            surrounded by Shoreditch's vibrant scene including Boxpark, restaurants, and nightlife. The property 
            is offered unfurnished but with integrated kitchen appliances. Council tax band: C. EPC rating: B.""",
            address={
                "line1": "The Forge, 133 Shoreditch High Street",
                "area": "Shoreditch",
                "city": "London",
                "postcode": "E1 6JE",
                "coordinates": {"lat": 51.5255, "lon": -0.0754}
            },
            price=175000,  # £1750/month
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
            including high ceilings, sash windows, and ornate cornicing, while being tastefully modernized. 
            The property comprises a generous reception room with bay window, separate modern kitchen with 
            breakfast bar, two well-proportioned double bedrooms, and a renovated bathroom. Located on a 
            quiet residential street yet just moments from Camden's famous markets, live music venues, and 
            canal-side walks. Camden Town (Northern Line) and Chalk Farm stations are within 10 minutes walk. 
            Local amenities include Sainsbury's, independent coffee shops, and Regent's Park. The property 
            is available part-furnished (white goods included) with flexible move-in dates.""",
            address={
                "line1": "78 Kentish Town Road",
                "area": "Camden",
                "city": "London",
                "postcode": "NW1 9PS",
                "coordinates": {"lat": 51.5450, "lon": -0.1426}
            },
            price=240000,  # £2400/month
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
            Thames and city skyline from floor-to-ceiling windows. The interior features a vast open-plan 
            reception/kitchen area with designer Miele appliances and granite worktops, a master bedroom with 
            en-suite bathroom and walk-in wardrobe, two further double bedrooms, and a luxury family bathroom. 
            The development offers world-class amenities including a swimming pool, spa, gym, cinema room, 
            resident's lounge, and 24-hour concierge. Located in the heart of Canary Wharf with underground 
            parking (2 spaces included), residents enjoy easy access to DLR, Jubilee line, and Crossrail 
            stations, along with abundant shopping and dining options at Canary Wharf Mall. Available furnished 
            or unfurnished with immediate occupancy.""",
            address={
                "line1": "Pan Peninsula Square",
                "area": "Canary Wharf",
                "city": "London",
                "postcode": "E14 9HL",
                "coordinates": {"lat": 51.5007, "lon": -0.0102}
            },
            price=450000,  # £4500/month
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
            area with integrated kitchen (including fridge/freezer, oven, and washing machine), a comfortable 
            double bedroom with built-in storage, and a modern bathroom with shower over bath. The apartment 
            benefits from a Juliet balcony with park views, gas central heating, and double glazing throughout. 
            The development offers secure entry, bike storage, and is within walking distance of Westfield 
            Stratford City shopping centre - one of Europe's largest malls. Transport links are exceptional with 
            Stratford station providing access to Central, Jubilee lines, DLR, Overground, and Crossrail 
            (Elizabeth Line). The area has seen significant regeneration and offers great amenities including 
            gyms, restaurants, and the Olympic Park facilities. Perfect for first-time renters or city 
            professionals seeking affordability and convenience.""",
            address={
                "line1": "Victory Parade, Stratford",
                "area": "Stratford",
                "city": "London",
                "postcode": "E20 1FS",
                "coordinates": {"lat": 51.5433, "lon": 0.0030}
            },
            price=145000,  # £1450/month
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
    session.commit()
    
    for prop in properties:
        session.refresh(prop)
    
    print(f"✅ Created {len(properties)} properties")
    return properties


def seed_property_media(session: Session, properties: list[Property]) -> list[PropertyMedia]:
    """Create sample property media entries"""
    media = []
    
    # Angel property media
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
    
    # Shoreditch studio media
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
    session.commit()
    
    print(f"✅ Created {len(media)} property media entries")
    return media


def seed_conversations_and_messages(session: Session, leads: list[Lead]) -> tuple[list[Conversation], list[Message]]:
    """Create sample conversations and messages"""
    conversations = []
    messages = []
    
    # Conversation 1: John Doe - complete qualification flow
    conv1 = Conversation(
        lead_id=leads[0].id,
        channel="whatsapp",
        status="active",
        last_message_at=datetime.utcnow() - timedelta(hours=2)
    )
    session.add(conv1)
    session.commit()
    session.refresh(conv1)
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
            content="Hello! I'm the AI assistant for Prime London Properties. I can help you find the perfect property. May I use your contact details to show you suitable properties and arrange viewings?",
            timestamp=datetime.utcnow() - timedelta(hours=3) + timedelta(seconds=5),
            platform_message_id="wamid.002",
            status="read"
        ),
        Message(
            conversation_id=conv1.id,
            direction="inbound",
            message_type="text",
            content="Yes, that's fine",
            timestamp=datetime.utcnow() - timedelta(hours=3) + timedelta(minutes=1),
            platform_message_id="wamid.003",
            status="read"
        ),
        Message(
            conversation_id=conv1.id,
            direction="outbound",
            message_type="text",
            content="Great! I have some excellent 2-bedroom properties in Angel. I found a stunning apartment at 45 Liverpool Road with a private balcony for £2,200/month. Would you like to see details?",
            timestamp=datetime.utcnow() - timedelta(hours=2, minutes=59),
            platform_message_id="wamid.004",
            status="read"
        ),
        Message(
            conversation_id=conv1.id,
            direction="inbound",
            message_type="text",
            content="Yes please, that sounds interesting",
            timestamp=datetime.utcnow() - timedelta(hours=2, minutes=55),
            platform_message_id="wamid.005",
            status="read"
        ),
    ]
    
    for msg in conv1_messages:
        session.add(msg)
        messages.append(msg)
    
    # Conversation 2: Alice Smith - viewing scheduled
    conv2 = Conversation(
        lead_id=leads[1].id,
        channel="whatsapp",
        status="active",
        last_message_at=datetime.utcnow() - timedelta(days=1)
    )
    session.add(conv2)
    session.commit()
    session.refresh(conv2)
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
            content="Perfect! I have a modern studio in Shoreditch with gym access for £1,750/month. When would you like to view it?",
            timestamp=datetime.utcnow() - timedelta(days=2) + timedelta(minutes=2),
            platform_message_id="wamid.102",
            status="read"
        ),
        Message(
            conversation_id=conv2.id,
            direction="inbound",
            message_type="text",
            content="Tomorrow afternoon?",
            timestamp=datetime.utcnow() - timedelta(days=1, hours=23),
            platform_message_id="wamid.103",
            status="read"
        ),
        Message(
            conversation_id=conv2.id,
            direction="outbound",
            message_type="text",
            content="I have slots available at 2:00 PM or 4:30 PM tomorrow. Which works better for you?",
            timestamp=datetime.utcnow() - timedelta(days=1, hours=23) + timedelta(minutes=1),
            platform_message_id="wamid.104",
            status="read"
        ),
    ]
    
    for msg in conv2_messages:
        session.add(msg)
        messages.append(msg)
    
    session.commit()
    print(f"✅ Created {len(conversations)} conversations with {len(messages)} messages")
    return conversations, messages


def seed_bookings(session: Session, leads: list[Lead], properties: list[Property], users: list[User]) -> list[Booking]:
    """Create sample viewing bookings"""
    bookings = [
        Booking(
            lead_id=leads[1].id,  # Alice Smith
            property_id=properties[1].id,  # Shoreditch studio
            agent_id=users[0].id,  # Sarah Mitchell
            start_time=datetime.utcnow() + timedelta(days=1, hours=14),
            end_time=datetime.utcnow() + timedelta(days=1, hours=14, minutes=30),
            status="scheduled",
            meeting_point="Property entrance, 133 Shoreditch High Street",
            notes="Lead is interested in gym facilities and commute to Old Street"
        ),
        Booking(
            lead_id=leads[0].id,  # John Doe
            property_id=properties[0].id,  # Angel apartment
            agent_id=users[1].id,  # James Wilson
            start_time=datetime.utcnow() + timedelta(days=3, hours=11),
            end_time=datetime.utcnow() + timedelta(days=3, hours=11, minutes=30),
            status="scheduled",
            meeting_point="45 Liverpool Road, building reception",
            notes="Lead interested in balcony and local amenities"
        ),
        Booking(
            lead_id=leads[3].id,  # Emily Jones
            property_id=properties[3].id,  # Canary Wharf luxury
            agent_id=users[3].id,  # Oliver Davies
            start_time=datetime.utcnow() + timedelta(days=5, hours=16),
            end_time=datetime.utcnow() + timedelta(days=5, hours=16, minutes=45),
            status="scheduled",
            meeting_point="Pan Peninsula reception desk",
            notes="High-value lead, interested in parking and amenities"
        ),
    ]
    
    for booking in bookings:
        session.add(booking)
    session.commit()
    
    for booking in bookings:
        session.refresh(booking)
    
    print(f"✅ Created {len(bookings)} bookings")
    return bookings


def seed_consents(session: Session, leads: list[Lead]) -> list[Consent]:
    """Create sample GDPR consent records"""
    consents = [
        Consent(
            lead_id=leads[0].id,
            consent_type="data_processing",
            granted=True,
            timestamp=datetime.utcnow() - timedelta(hours=3),
            consent_text="I agree to Prime London Properties using my contact details to show me properties and arrange viewings.",
            ip_address="92.40.123.45"
        ),
        Consent(
            lead_id=leads[0].id,
            consent_type="marketing",
            granted=False,
            timestamp=datetime.utcnow() - timedelta(hours=3),
            consent_text="I agree to receive marketing communications about new properties.",
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
        Consent(
            lead_id=leads[3].id,
            consent_type="data_processing",
            granted=True,
            timestamp=datetime.utcnow() - timedelta(days=1),
            consent_text="I agree to Urban Living Estates processing my information.",
            ip_address="78.105.234.12"
        ),
    ]
    
    for consent in consents:
        session.add(consent)
    session.commit()
    
    print(f"✅ Created {len(consents)} consent records")
    return consents


def seed_agent_calendars(session: Session, users: list[User], bookings: list[Booking]) -> list[AgentCalendar]:
    """Create sample calendar events for agents"""
    events = []
    
    # Add booking-related events
    for booking in bookings:
        events.append(AgentCalendar(
            agent_id=booking.agent_id,
            event_id=f"gcal_{booking.id}",
            title=f"Property Viewing - {booking.property.address['area']}",
            start_time=booking.start_time,
            end_time=booking.end_time,
            event_type="viewing",
            status="scheduled"
        ))
    
    # Add some regular calendar events
    events.extend([
        AgentCalendar(
            agent_id=users[0].id,  # Sarah Mitchell
            title="Team Meeting",
            start_time=datetime.utcnow() + timedelta(days=2, hours=9),
            end_time=datetime.utcnow() + timedelta(days=2, hours=10),
            event_type="meeting",
            status="scheduled"
        ),
        AgentCalendar(
            agent_id=users[0].id,
            title="Lunch Break",
            start_time=datetime.utcnow() + timedelta(days=1, hours=12),
            end_time=datetime.utcnow() + timedelta(days=1, hours=13),
            event_type="break",
            status="scheduled"
        ),
        AgentCalendar(
            agent_id=users[1].id,  # James Wilson
            title="Training Session",
            start_time=datetime.utcnow() + timedelta(days=4, hours=14),
            end_time=datetime.utcnow() + timedelta(days=4, hours=16),
            event_type="meeting",
            status="scheduled"
        ),
    ])
    
    for event in events:
        session.add(event)
    session.commit()
    
    print(f"✅ Created {len(events)} calendar events")
    return events


def seed_all():
    """Main function to seed all sample data"""
    print("\n🌱 Starting database seeding...\n")
    
    # Create tables first
    create_db_and_tables()
    
    with Session(engine) as session:
        # Seed in order of dependencies
        agencies = seed_agencies(session)
        users = seed_users(session, agencies)
        leads = seed_leads(session, agencies)
        properties = seed_properties(session, agencies)
        property_media = seed_property_media(session, properties)
        conversations, messages = seed_conversations_and_messages(session, leads)
        bookings = seed_bookings(session, leads, properties, users)
        consents = seed_consents(session, leads)
        calendar_events = seed_agent_calendars(session, users, bookings)
    
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


if __name__ == "__main__":
    seed_all()