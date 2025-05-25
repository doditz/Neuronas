"""
This work is licensed under CC BY-NC 4.0 International.
Commercial use requires prior written consent and compensation.
Contact: sebastienbrulotte@gmail.com
Attribution: Sebastien Brulotte aka [ Doditz ]

This document is part of the NEURONAS cognitive system.
Core modules referenced: BRONAS (Ethical Reflex Filter) and QRONAS (Probabilistic Symbolic Vector Engine).
All outputs are subject to integrity validation and ethical compliance enforced by BRONAS.
"""

import os
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def send_sms(to_phone_number, message):
    """
    Send an SMS message using Twilio
    
    Args:
        to_phone_number (str): The recipient's phone number in E.164 format (e.g., +15551234567)
        message (str): The message content to send
        
    Returns:
        dict: Information about the sent message or error
    """
    # Get credentials from environment variables
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    from_number = os.environ.get("TWILIO_PHONE_NUMBER")
    
    # Validate environment variables
    if not all([account_sid, auth_token, from_number]):
        logger.error("Missing Twilio credentials. Please set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER environment variables.")
        return {
            "success": False,
            "error": "Missing Twilio credentials. Please configure the required environment variables."
        }
    
    try:
        # Initialize Twilio client
        client = Client(account_sid, auth_token)
        
        # Send SMS message
        message_obj = client.messages.create(
            body=message,
            from_=from_number,
            to=to_phone_number
        )
        
        logger.info(f"Message sent successfully. SID: {message_obj.sid}")
        return {
            "success": True,
            "message_sid": message_obj.sid,
            "status": message_obj.status
        }
        
    except TwilioRestException as e:
        logger.error(f"Twilio error: {e}")
        return {
            "success": False,
            "error": str(e),
            "code": e.code
        }
    except Exception as e:
        logger.error(f"Unexpected error sending SMS: {e}")
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }