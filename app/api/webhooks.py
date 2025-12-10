"""
WEBHOOKS.PY - WhatsApp Webhook Endpoints
Receives incoming WhatsApp messages directly from Twilio
"""

from fastapi import APIRouter, Request, HTTPException
from typing import Dict
import json

# Import utilities
from app import validate_phone_number, get_timestamp

# Import WhatsApp client for sending responses
from app.integrations import WhatsAppClient

# Create router
router = APIRouter()

# =====================================================
# WEBHOOK ENDPOINT - Receives from Twilio
# =====================================================

@router.post("/webhook/twilio")
async def receive_whatsapp_message(request: Request):
    """
    Receive incoming WhatsApp message directly from Twilio
    
    Twilio sends POST request with form data containing:
    - MessageSid: Unique message ID
    - From: Sender's WhatsApp number
    - To: Your Twilio WhatsApp number
    - Body: Message text
    - ProfileName: User's WhatsApp name
    - And many other fields...
    
    This endpoint:
    1. Receives and extracts the complete raw payload
    2. Validates required fields
    3. Passes to AI for processing (Aman's work)
    4. Sends response back to user
    """
    
    print("\n" + "="*80)
    print("📨 INCOMING WHATSAPP MESSAGE FROM TWILIO")
    print("="*80)
    print(f"Timestamp: {get_timestamp()}")
    
    try:
        # Extract complete raw payload from Twilio
        # Twilio sends form data, FastAPI converts to dict
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
        
        # TODO: Process with AI service (Aman's work)
        # For now, just acknowledge receipt
        # ai_response = await ai_service.process(user_message)
        
        # TODO: Send response back to user
        # whatsapp_client = WhatsAppClient()
        # await whatsapp_client.send_message(user_phone, ai_response)
        
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