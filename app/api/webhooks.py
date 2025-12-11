"""
WEBHOOKS.PY - WhatsApp Webhook Endpoints
Receives incoming WhatsApp messages directly from Twilio
"""

from fastapi import APIRouter, Request, HTTPException
from typing import Dict
import json

# Import utilities - FIXED IMPORTS
from app.utils.phone_utils import validate_phone_number, get_timestamp

# Import WhatsApp client for sending responses
from app.integrations.whatsapp import WhatsAppClient  # Direct import

# Create router
router = APIRouter()

# =====================================================
# WEBHOOK ENDPOINT - Receives from Twilio
# =====================================================

@router.post("/webhook/twilio")
async def receive_whatsapp_message(request: Request):
    """
    Receive incoming WhatsApp message directly from Twilio
    """
    
    print("\n" + "="*80)
    print("📨 INCOMING WHATSAPP MESSAGE FROM TWILIO")
    print("="*80)
    print(f"Timestamp: {get_timestamp()}")
    
    try:
        # Extract complete raw payload from Twilio
        form_data = await request.form()
        payload = dict(form_data)
        
        # Display complete raw payload
        print("\n📦 COMPLETE RAW PAYLOAD:")
        print(json.dumps(payload, indent=2))
        
        # Extract key fields
        message_sid = payload.get("MessageSid")
        user_phone = payload.get("From")
        user_message = payload.get("Body", "")
        profile_name = payload.get("ProfileName", "User")
        num_media = payload.get("NumMedia", "0")
        
        print(f"\n📊 KEY FIELDS EXTRACTED:")
        print(f"  MessageSid: {message_sid}")
        print(f"  From: {user_phone}")
        print(f"  To: {payload.get('To')}")
        print(f"  Body: {user_message}")
        print(f"  Profile: {profile_name}")
        print(f"  Media Count: {num_media}")
        print(f"  Total Fields: {len(payload)}")
        
        # Validate required fields
        if not user_phone:
            raise HTTPException(
                status_code=400,
                detail="Missing 'From' field"
            )
        
        if not user_message and num_media == "0":
            raise HTTPException(
                status_code=400,
                detail="Missing message content"
            )
        
        # Validate phone number format
        if not validate_phone_number(user_phone):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid phone number: {user_phone}"
            )
        
        print(f"\n✅ Payload validated successfully")
        
        # TODO: Process with AI service
        # For now, just acknowledge receipt
        
        print("="*80 + "\n")
        
        # Return success to Twilio
        return {
            "success": True,
            "message_sid": message_sid,
            "from": user_phone,
            "body": user_message,
            "timestamp": get_timestamp()
        }
        
    except HTTPException:
        raise
        
    except Exception as e:
        print(f"\n❌ ERROR:")
        print(f"Error: {str(e)}")
        print("="*80 + "\n")
        
        raise HTTPException(
            status_code=500,
            detail=f"Error processing webhook: {str(e)}"
        )

# =====================================================
# WEBHOOK VERIFICATION
# =====================================================

@router.get("/webhook/twilio")
async def verify_webhook():
    """
    Twilio may send GET request to verify webhook is active
    """
    
    print("📋 Webhook verification request")
    
    return {
        "status": "active",
        "endpoint": "/webhook/twilio",
        "timestamp": get_timestamp()
    }