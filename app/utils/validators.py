"""Data validation utilities."""
from typing import Dict, Any, Optional
import re


class Validators:
    """Data validation utilities."""
    
    @staticmethod
    def is_valid_phone(phone: str) -> bool:
        """Validate phone number format.
        
        Args:
            phone: Phone number to validate.
            
        Returns:
            True if valid phone number.
        """
        # International format validation
        pattern = r'^\\+?1?\\d{9,15}$'
        return bool(re.match(pattern, phone.replace(" ", "")))
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Validate email format.
        
        Args:
            email: Email to validate.
            
        Returns:
            True if valid email.
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def normalize_phone(phone: str) -> str:
        """Normalize phone number to standard format.
        
        Args:
            phone: Phone number to normalize.
            
        Returns:
            Normalized phone number.
        """
        # TODO: Implement phone normalization
        return phone.replace(" ", "").replace("-", "")
    
    @staticmethod
    def validate_lead_data(data: Dict[str, Any]) -> bool:
        """Validate lead data structure.
        
        Args:
            data: Lead data dictionary.
            
        Returns:
            True if data is valid.
        """
        # TODO: Implement lead data validation
        required_fields = ["phone_number"]
        return all(field in data for field in required_fields)
