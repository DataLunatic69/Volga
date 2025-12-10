"""
SQLModel database models for NexCell AI Receptionist
File: app/database/models.py
"""
from datetime import datetime, date
from typing import Optional, List
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship, Column, JSON
from sqlalchemy.dialects.postgresql import INET, JSONB


class Agency(SQLModel, table=True):
    """Agency/Real Estate Company"""
    __tablename__ = "agencies"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=255, nullable=False)
    whatsapp_business_account_id: Optional[str] = Field(max_length=255)
    phone_number: str = Field(max_length=50)
    email: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    users: List["User"] = Relationship(back_populates="agency")
    leads: List["Lead"] = Relationship(back_populates="agency")
    properties: List["Property"] = Relationship(back_populates="agency")


class User(SQLModel, table=True):
    """Agency staff members (agents, admins)"""
    __tablename__ = "users"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    agency_id: UUID = Field(foreign_key="agencies.id", nullable=False)
    name: str = Field(max_length=255, nullable=False)
    email: str = Field(max_length=255, unique=True, nullable=False)
    phone: str = Field(max_length=50)
    role: str = Field(max_length=50)  # admin, agent, viewer
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    agency: Agency = Relationship(back_populates="users")
    bookings: List["Booking"] = Relationship(back_populates="agent")
    calendar_events: List["AgentCalendar"] = Relationship(back_populates="agent")


class Lead(SQLModel, table=True):
    """Potential clients (tenants/buyers)"""
    __tablename__ = "leads"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    agency_id: UUID = Field(foreign_key="agencies.id", nullable=False)
    phone: str = Field(max_length=50, nullable=False)
    email: Optional[str] = Field(max_length=255)
    name: Optional[str] = Field(max_length=255)
    budget_min: Optional[int] = None  # in pence/cents
    budget_max: Optional[int] = None  # in pence/cents
    preferred_areas: Optional[dict] = Field(default=None, sa_column=Column(JSONB))
    bedrooms: Optional[int] = None
    move_in_date: Optional[date] = None
    lead_score: int = Field(default=0)
    status: str = Field(default="new", max_length=50)  # new, contacted, qualified, viewing_scheduled, converted, lost
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    agency: Agency = Relationship(back_populates="leads")
    conversations: List["Conversation"] = Relationship(back_populates="lead")
    bookings: List["Booking"] = Relationship(back_populates="lead")
    consents: List["Consent"] = Relationship(back_populates="lead")


class Property(SQLModel, table=True):
    """Property listings"""
    __tablename__ = "properties"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    agency_id: UUID = Field(foreign_key="agencies.id", nullable=False)
    title: str = Field(max_length=500, nullable=False)
    description: str = Field(nullable=False)  # Full text stored here, embeddings in Qdrant
    address: dict = Field(sa_column=Column(JSONB))  # {line1, area, city, postcode, coordinates: {lat, lon}}
    price: int = Field(nullable=False)  # in pence/cents
    bedrooms: int = Field(nullable=False)
    bathrooms: int = Field(nullable=False)
    area_sqft: Optional[int] = None
    property_type: str = Field(max_length=100)  # apartment, house, studio, etc.
    furnishing: str = Field(max_length=50)  # furnished, unfurnished, part_furnished
    amenities: Optional[dict] = Field(default=None, sa_column=Column(JSONB))  # ["parking", "gym", "garden"]
    availability_status: str = Field(default="available", max_length=50)  # available, under_offer, let, sold
    available_from: Optional[date] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    agency: Agency = Relationship(back_populates="properties")
    media: List["PropertyMedia"] = Relationship(back_populates="property")
    bookings: List["Booking"] = Relationship(back_populates="property")


class PropertyMedia(SQLModel, table=True):
    """Media files for properties"""
    __tablename__ = "property_media"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    property_id: UUID = Field(foreign_key="properties.id", nullable=False)
    media_type: str = Field(max_length=50)  # image, video, virtual_tour
    url: str = Field(max_length=1000, nullable=False)
    caption: Optional[str] = Field(max_length=500)
    order_index: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    property: Property = Relationship(back_populates="media")


class Conversation(SQLModel, table=True):
    """Conversation threads with leads"""
    __tablename__ = "conversations"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    lead_id: UUID = Field(foreign_key="leads.id", nullable=False)
    channel: str = Field(max_length=50)  # whatsapp, phone, web_chat
    status: str = Field(default="active", max_length=50)  # active, closed, escalated
    last_message_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    lead: Lead = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(back_populates="conversation")


class Message(SQLModel, table=True):
    """Individual messages in conversations"""
    __tablename__ = "messages"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", nullable=False)
    direction: str = Field(max_length=20)  # inbound, outbound
    message_type: str = Field(max_length=50)  # text, image, template, audio, video
    content: Optional[str] = None  # message text or caption
    media_url: Optional[str] = Field(max_length=1000)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    platform_message_id: Optional[str] = Field(max_length=255)  # WhatsApp/platform message ID
    status: str = Field(default="sent", max_length=50)  # sent, delivered, read, failed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    conversation: Conversation = Relationship(back_populates="messages")


class Booking(SQLModel, table=True):
    """Property viewing appointments"""
    __tablename__ = "bookings"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    lead_id: UUID = Field(foreign_key="leads.id", nullable=False)
    property_id: UUID = Field(foreign_key="properties.id", nullable=False)
    agent_id: UUID = Field(foreign_key="users.id", nullable=False)
    start_time: datetime = Field(nullable=False)
    end_time: datetime = Field(nullable=False)
    status: str = Field(default="scheduled", max_length=50)  # scheduled, completed, cancelled, no_show
    meeting_point: Optional[str] = Field(max_length=500)
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    lead: Lead = Relationship(back_populates="bookings")
    property: Property = Relationship(back_populates="bookings")
    agent: User = Relationship(back_populates="bookings")


class Consent(SQLModel, table=True):
    """GDPR consent records"""
    __tablename__ = "consents"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    lead_id: UUID = Field(foreign_key="leads.id", nullable=False)
    consent_type: str = Field(max_length=100)  # data_processing, marketing, communication
    granted: bool = Field(nullable=False)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    consent_text: str = Field(nullable=False)  # Exact text shown to user
    ip_address: Optional[str] = Field(sa_column=Column(INET))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    lead: Lead = Relationship(back_populates="consents")


class AgentCalendar(SQLModel, table=True):
    """Agent calendar events"""
    __tablename__ = "agent_calendars"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    agent_id: UUID = Field(foreign_key="users.id", nullable=False)
    event_id: Optional[str] = Field(max_length=255)  # Google Calendar event ID
    title: str = Field(max_length=500)
    start_time: datetime = Field(nullable=False)
    end_time: datetime = Field(nullable=False)
    event_type: str = Field(max_length=50)  # viewing, meeting, break, unavailable
    status: str = Field(default="scheduled", max_length=50)  # scheduled, completed, cancelled
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    agent: User = Relationship(back_populates="calendar_events")