"""Notification service."""
from typing import Dict, Any, Optional, List


class NotificationService:
    """Service for sending notifications."""
    
    async def send_notification(
        self,
        recipient_phone: str,
        message: str,
        notification_type: str = "info"
    ) -> bool:
        """Send notification to user.
        
        Args:
            recipient_phone: Recipient phone number.
            message: Message to send.
            notification_type: Type of notification (info, alert, etc.).
            
        Returns:
            True if notification sent successfully.
        """
        # TODO: Implement notification sending
        pass
    
    async def send_bulk_notifications(
        self,
        recipients: List[str],
        message: str
    ) -> Dict[str, bool]:
        """Send notifications to multiple recipients.
        
        Args:
            recipients: List of phone numbers.
            message: Message to send.
            
        Returns:
            Dictionary with send status for each recipient.
        """
        # TODO: Implement bulk notification
        pass
    
    async def schedule_notification(
        self,
        recipient_phone: str,
        message: str,
        send_at: str
    ) -> bool:
        """Schedule notification for future delivery.
        
        Args:
            recipient_phone: Recipient phone number.
            message: Message to send.
            send_at: ISO datetime for sending.
            
        Returns:
            True if scheduling successful.
        """
        # TODO: Implement scheduled notification
        pass
