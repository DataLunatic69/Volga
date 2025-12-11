"""Phone number utilities."""
import re
from datetime import datetime
from typing import Optional


def validate_phone_number(phone: str) -> bool:
    """Validate phone number format.
    
    Args:
        phone: Phone number to validate
        
    Returns:
        True if valid phone number
    """
    # Remove any non-digit characters except +
    cleaned = re.sub(r'[^\d+]', '', phone)
    
    # Check if it starts with + and has 10-15 digits
    if phone.startswith('+'):
        # International format
        return len(cleaned) >= 10 and len(cleaned) <= 15
    else:
        # Local format (assuming)
        return len(cleaned) >= 9 and len(cleaned) <= 15


def clean_phone_number(phone: str) -> str:
    """Clean phone number for Twilio.
    
    Args:
        phone: Raw phone number
        
    Returns:
        Cleaned phone number
    """
    # Remove all non-digit characters
    cleaned = re.sub(r'[^\d+]', '', phone)
    
    # If doesn't start with +, add it
    if not cleaned.startswith('+'):
        # Assuming UK numbers for now
        if cleaned.startswith('0'):
            cleaned = '+44' + cleaned[1:]
        else:
            cleaned = '+' + cleaned
            
    return cleaned


def truncate_message(message: str, max_length: int = 1600) -> str:
    """Truncate message to maximum length.
    
    Args:
        message: Message to truncate
        max_length: Maximum length
        
    Returns:
        Truncated message
    """
    if len(message) > max_length:
        return message[:max_length] + "..."
    return message


def get_timestamp() -> str:
    """Get current timestamp.
    
    Returns:
        ISO format timestamp
    """
    return datetime.now().isoformat()