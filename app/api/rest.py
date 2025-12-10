"""REST API endpoints for admin operations."""
from fastapi import APIRouter
from typing import Dict, Any, List

router = APIRouter()


@router.get("/conversations")
async def get_conversations() -> List[Dict[str, Any]]:
    """Get all conversations.
    
    Returns:
        List of conversations.
    """
    # TODO: Implement get conversations
    pass


@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str) -> Dict[str, Any]:
    """Get specific conversation details.
    
    Args:
        conversation_id: ID of the conversation.
        
    Returns:
        Conversation details.
    """
    # TODO: Implement get conversation
    pass


@router.get("/leads")
async def get_leads() -> List[Dict[str, Any]]:
    """Get all leads.
    
    Returns:
        List of leads.
    """
    # TODO: Implement get leads
    pass


@router.get("/properties")
async def get_properties() -> List[Dict[str, Any]]:
    """Get all properties.
    
    Returns:
        List of properties.
    """
    # TODO: Implement get properties
    pass


@router.post("/sync-properties")
async def sync_properties() -> Dict[str, Any]:
    """Trigger property synchronization.
    
    Returns:
        Sync status.
    """
    # TODO: Implement property sync
    pass


@router.post("/test-message")
async def send_test_message(phone_number: str, message: str) -> Dict[str, Any]:
    """Send a test WhatsApp message.
    
    Args:
        phone_number: Recipient phone number.
        message: Message content.
        
    Returns:
        Send status.
    """
    # TODO: Implement test message
    pass
