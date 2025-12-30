"""
Database models module - exports all SQLModel models.
"""
from .activity_log import ActivityLog, ActorType, Severity
from .agency import Agency, BusinessType, SubscriptionStatus, SubscriptionTier
from .agency_metrics_daily import AgencyMetricsDaily
from .agency_user import AgencyUser, UserRole
from .agent_calender import AgentCalendar
from .agent_performance import AgentPerformance
from .ai_agent_session import AIAgentSession
from .api_keys import APIKey
from .auth_users import AuthUser
from .base import BaseModel, TimestampMixin
from .calender_events import CalendarEvent, EventStatus, EventType
from .consent_logs import ConsentLog, ConsentMethod, ConsentType
from .conversation_state_snapshots import ConversationStateSnapshot, CreatedBy
from .conversations import Channel, Conversation, ConversationStatus, CurrentStage
from .deals import Deal, DealStage
from .email_verification_tokens import EmailVerificationToken
from .escalation_rules import EscalationRule
from .lead import ContactSource, Lead, LifecycleStage
from .lead_preferences import (
    Furnishing as LeadFurnishing,
    LeadPreferences,
    PropertyType as LeadPropertyType,
    TransactionType as LeadTransactionType,
    Urgency,
)
from .messages import Direction, Message, MessageType, SenderType
from .password_reset_tokens import PasswordResetToken
from .permissions import Permission
from .properties import (
    Furnishing as PropertyFurnishing,
    PricePeriod,
    Property,
    PropertyStatus,
    PropertyType,
    TransactionType as PropertyTransactionType,
)
from .property_availibility import PropertyAvailability
from .refresh_tokens import RefreshToken
from .role_permissions import RolePermission
from .roles import Role
from .user_roles import UserRole as UserRoleAssignment
from .viewing_feedback import CollectedBy, ViewingFeedback
from .viewings import CancelledBy, Viewing, ViewingStatus, ViewingType

__all__ = [
    # Base
    "BaseModel",
    "TimestampMixin",
    # Agency
    "Agency",
    "BusinessType",
    "SubscriptionTier",
    "SubscriptionStatus",
    # Agency User
    "AgencyUser",
    "UserRole",
    # Auth & Authorization
    "AuthUser",
    "RefreshToken",
    "Role",
    "Permission",
    "RolePermission",
    "UserRoleAssignment",
    "APIKey",
    "PasswordResetToken",
    "EmailVerificationToken",
    # Lead
    "Lead",
    "ContactSource",
    "LifecycleStage",
    # Lead Preferences
    "LeadPreferences",
    "LeadPropertyType",
    "LeadTransactionType",
    "LeadFurnishing",
    "Urgency",
    # Properties
    "Property",
    "PropertyType",
    "PropertyTransactionType",
    "PropertyStatus",
    "PricePeriod",
    "PropertyFurnishing",
    # Agent Calendar
    "AgentCalendar",
    # Calendar Events
    "CalendarEvent",
    "EventType",
    "EventStatus",
    # Viewings
    "Viewing",
    "ViewingType",
    "ViewingStatus",
    "CancelledBy",
    # Viewing Feedback
    "ViewingFeedback",
    "CollectedBy",
    # Property Availability
    "PropertyAvailability",
    # Conversations
    "Conversation",
    "Channel",
    "ConversationStatus",
    "CurrentStage",
    # Messages
    "Message",
    "Direction",
    "SenderType",
    "MessageType",
    # Deals
    "Deal",
    "DealStage",
    # AI Agent Session
    "AIAgentSession",
    # Activity Log
    "ActivityLog",
    "ActorType",
    "Severity",
    # Agency Metrics Daily
    "AgencyMetricsDaily",
    # Agent Performance
    "AgentPerformance",
    # Consent Logs
    "ConsentLog",
    "ConsentType",
    "ConsentMethod",
    # Conversation State Snapshots
    "ConversationStateSnapshot",
    "CreatedBy",
    # Escalation Rules
    "EscalationRule",
]

