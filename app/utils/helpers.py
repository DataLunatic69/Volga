"""Helper utilities."""
from typing import Any, Optional, Dict
import uuid
from datetime import datetime


class Helpers:
    """General helper utilities."""
    
    @staticmethod
    def generate_id(prefix: str = "") -> str:
        """Generate unique ID.
        
        Args:
            prefix: Optional prefix for ID.
            
        Returns:
            Unique identifier.
        """
        uid = str(uuid.uuid4()).replace("-", "")
        return f"{prefix}_{uid}" if prefix else uid
    
    @staticmethod
    def get_timestamp() -> str:
        """Get current timestamp.
        
        Returns:
            ISO format timestamp.
        """
        return datetime.utcnow().isoformat()
    
    @staticmethod
    def safe_get(
        data: Dict[str, Any],
        key: str,
        default: Optional[Any] = None
    ) -> Any:
        """Safely get value from dictionary.
        
        Args:
            data: Dictionary to access.
            key: Key to retrieve.
            default: Default value if key not found.
            
        Returns:
            Value or default.
        """
        return data.get(key, default)
    
    @staticmethod
    def is_empty(value: Any) -> bool:
        """Check if value is empty.
        
        Args:
            value: Value to check.
            
        Returns:
            True if value is empty/None/false.
        """
        return value is None or (isinstance(value, (list, dict, str)) and len(value) == 0)
