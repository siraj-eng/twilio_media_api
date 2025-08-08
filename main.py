from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl, validator
from typing import Optional, List
from twilio.rest import Client
from dotenv import load_dotenv
import os
import re

load_dotenv()

app = FastAPI()

class MessageRequest(BaseModel):
    to: str
    body: Optional[str] = None
    media_url: Optional[List[HttpUrl]] = None

    @validator('to')
    def validate_to_number(cls, v):
        """Validate WhatsApp number format"""
        if not re.match(r'^whatsapp:\+\d{1,15}$', v):
            raise ValueError('Number must be in format "whatsapp:+254716160370"')
        return v

# Initialize Twilio client with error handling for credentials purposes
try:
    client = Client(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))
    # Test credentials are valid
    client.api.accounts(os.getenv('TWILIO_ACCOUNT_SID')).fetch()
except Exception as e:
    print(f"Twilio client initialization failed: {str(e)}")
    raise RuntimeError("Failed to initialize Twilio client")

@app.post("/send-whatsapp/")
async def send_whatsapp_message(message: MessageRequest):
    try:
        # Get WhatsApp number from environment
        whatsapp_number = os.getenv('TWILIO_WHATSAPP_NUMBER')
        if not whatsapp_number:
            raise HTTPException(
                status_code=500,
                detail="Twilio WhatsApp number not configured"
            )

        # Prepare message parameters
        message_params = {
            "from_": f"whatsapp:{whatsapp_number}",
            "to": message.to
        }

        if message.body:
            message_params["body"] = message.body
        if message.media_url:
            message_params["media_url"] = [str(url) for url in message.media_url]

        # Validate we have either body or media it accepts media too 
        if not message.body and not message.media_url:
            raise HTTPException(
                status_code=400,
                detail="Either body or media_url must be provided"
            )

        # Send message
        message = client.messages.create(**message_params)

        return {
            "status": "success",
            "message_sid": message.sid,
            "to": message.to,
            "body": message.body,
            "num_media": message.num_media
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to send message: {clean_twilio_error(str(e))}"
        )

def clean_twilio_error(error_msg: str) -> str:
    """Remove ANSI color codes and format Twilio errors"""
    import re
    # Remove ANSI color codes
    error_msg = re.sub(r'\x1b\[[0-9;]*m', '', error_msg)
    # Extract the main error message
    match = re.search(r'Unable to create record: (.+)', error_msg)
    return match.group(1) if match else error_msg

