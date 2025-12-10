"""
WHATSAPP.PY - WhatsApp Integration Client
Sends WhatsApp messages directly via Twilio Python SDK
"""

import os
from typing import Dict, Optional
from twilio.rest import Client
from dotenv import load_dotenv

# Import utilities
from app import validate_phone_number, truncate_message, clean_phone_number

# Load environment variables
load_dotenv()

class WhatsAppClient:
    """
    WhatsApp client for sending messages via Twilio
    
    This client uses Twilio's Python SDK to send WhatsApp messages directly.
    No Node.js needed - all in Python!
    """
    
    def __init__(self):
        """Initialize WhatsApp client with Twilio credentials"""
        
        # Get Twilio credentials from environment
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = os.getenv("TWILIO_WHATSAPP_NUMBER")
        
        # Validate credentials exist
        if not account_sid or not auth_token:
            raise ValueError("Missing Twilio credentials in .env file")
        
        if not self.from_number:
            raise ValueError("Missing TWILIO_WHATSAPP_NUMBER in .env file")
        
        # Initialize Twilio client
        self.client = Client(account_sid, auth_token)
        
        print(f"🔧 WhatsApp Client initialized")
        print(f"   From: {self.from_number}")
    
    async def send_message(
        self, 
        to: str, 
        message: str,
        media_url: Optional[str] = None
    ) -> Dict:
        """
        Send WhatsApp message to user
        
        Args:
            to: User's WhatsApp number (whatsapp:+447904448006)
            message: Message text to send
            media_url: Optional media URL (images, videos, documents)
        
        Returns:
            dict: {
                "success": True/False,
                "message_sid": "SM...",
                "status": "queued/sent/delivered",
                "error": "error message if failed"
            }
        """
        
        # Validate phone number
        if not validate_phone_number(to):
            print(f"❌ Invalid phone number: {to}")
            return {
                "success": False,
                "error": f"Invalid phone number format: {to}"
            }
        
        # Truncate message if too long
        truncated_message = truncate_message(message, 1600)
        
        if len(message) > len(truncated_message):
            print(f"⚠️  Message truncated: {len(message)} → {len(truncated_message)} chars")
        
        # Clean phone number for Twilio
        clean_to = to if to.startswith('whatsapp:') else f'whatsapp:{clean_phone_number(to)}'
        
        print(f"\n📤 Sending WhatsApp message via Twilio:")
        print(f"   From: {self.from_number}")
        print(f"   To: {clean_to}")
        print(f"   Message length: {len(truncated_message)} chars")
        print(f"   Has media: {'Yes' if media_url else 'No'}")
        
        try:
            # Send via Twilio Python SDK
            twilio_message = self.client.messages.create(
                from_=self.from_number,
                to=clean_to,
                body=truncated_message,
                media_url=[media_url] if media_url else None
            )
            
            print(f"✅ Message sent successfully!")
            print(f"   Message SID: {twilio_message.sid}")
            print(f"   Status: {twilio_message.status}")
            
            return {
                "success": True,
                "message_sid": twilio_message.sid,
                "status": twilio_message.status,
                "to": clean_to,
                "timestamp": twilio_message.date_created.isoformat() if twilio_message.date_created else None
            }
            
        except Exception as e:
            print(f"❌ Error sending message:")
            print(f"   Error: {str(e)}")
            
            return {
                "success": False,
                "error": str(e),
                "to": clean_to
            }
    
    async def send_media_message(
        self,
        to: str,
        message: str,
        media_url: str
    ) -> Dict:
        """
        Send WhatsApp message with media attachment
        
        Args:
            to: User's WhatsApp number
            message: Caption text
            media_url: URL of media file
        
        Returns:
            dict: Send result
        """
        
        print(f"🖼️  Sending media message")
        print(f"   Media URL: {media_url}")
        
        return await self.send_message(to, message, media_url)
    
    async def send_template_message(
        self,
        to: str,
        template_name: str,
        parameters: Dict
    ) -> Dict:
        """
        Send WhatsApp template message
        
        NOTE: Requires approved WhatsApp templates (Phase 2)
        
        Args:
            to: User's WhatsApp number
            template_name: Approved template name
            parameters: Template parameters
        
        Returns:
            dict: Send result
        """
        
        print(f"📋 Template message (Phase 2 - not implemented)")
        
        return {
            "success": False,
            "error": "Template messages not implemented (Phase 2)"
        }

# =====================================================
# HELPER FUNCTION
# =====================================================

def get_whatsapp_client() -> WhatsAppClient:
    """
    Get WhatsApp client instance
    
    Returns:
        WhatsAppClient: Ready to send messages
    """
    return WhatsAppClient()