"""LangGraph state schema for AI workflow."""
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ConversationMessage(BaseModel):
    """Single message in conversation."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


class LeadInfo(BaseModel):
    """Lead information."""
    phone_number: str
    name: Optional[str] = None
    email: Optional[str] = None
    location: Optional[str] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    preferences: Optional[Dict[str, Any]] = None
    qualification_score: float = 0.0


class PropertyMatch(BaseModel):
    """Property matching result."""
    property_id: str
    title: str
    relevance_score: float
    reason: str


class BookingSlot(BaseModel):
    """Available booking slot."""
    date: str
    time: str
    agent_name: str


class WorkflowState(BaseModel):
    """Main workflow state for LangGraph."""
    
    # Conversation
    messages: List[ConversationMessage] = Field(default_factory=list)
    conversation_id: str
    user_phone: str
    
    # Lead tracking
    lead_info: Optional[LeadInfo] = None
    is_qualified: bool = False
    
    # Property matching
    matched_properties: List[PropertyMatch] = Field(default_factory=list)
    user_interests: List[str] = Field(default_factory=list)
    
    # Booking
    booking_intent: bool = False
    available_slots: List[BookingSlot] = Field(default_factory=list)
    booked_slot: Optional[BookingSlot] = None
    booking_confirmed: bool = False
    
    # Workflow control
    current_agent: str = "receptionist"  # Current agent handling conversation
    next_agent: Optional[str] = None
    should_escalate: bool = False
    workflow_complete: bool = False
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    language: str = "en"


class AgentResponse(BaseModel):
    """Response from an agent."""
    message: str
    action: Optional[str] = None
    next_agent: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
