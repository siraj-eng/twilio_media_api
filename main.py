from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, field_validator, ValidationError
from typing import Optional
from twilio.rest import Client
from dotenv import load_dotenv
import os
import logging
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Twilio WhatsApp API",
    description="API for sending WhatsApp messages using Twilio",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Validate required environment variables
required_vars = ['TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN', 'TWILIO_WHATSAPP_NUMBER']
for var in required_vars:
    if not os.getenv(var):
        raise ValueError(f"Missing required environment variable: {var}")

# Initialize Twilio client
try:
    client = Client(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))
    # Verify credentials
    client.api.accounts(os.getenv('TWILIO_ACCOUNT_SID')).fetch()
    logger.info("Twilio client initialized successfully")
except Exception as e:
    logger.error(f"Twilio initialization failed: {str(e)}")
    raise

# Pydantic model for request validation
class WhatsAppMessage(BaseModel):
    """Pydantic model for WhatsApp message validation"""
    to: str
    body: str
    media_url: Optional[str] = None

    @field_validator('to')
    @classmethod
    def validate_whatsapp_number(cls, v: str) -> str:
        """Validate WhatsApp number format"""
        if not v.startswith('whatsapp:+'):
            raise ValueError('Number must be in format "whatsapp:+1234567890"')
        
        # Remove 'whatsapp:' prefix for validation
        phone_number = v[9:]
        
        # Basic phone number validation
        if not phone_number.startswith('+'):
            raise ValueError('Phone number must start with a plus sign (+)')
        if not phone_number[1:].isdigit():
            raise ValueError('Phone number must contain only digits after the plus sign')
        if len(phone_number) < 10 or len(phone_number) > 20:
            raise ValueError('Invalid phone number length')
            
        return v

    @field_validator('body')
    @classmethod
    def validate_body(cls, v: str) -> str:
        """Validate message body"""
        if not v or not v.strip():
            raise ValueError('Message body cannot be empty')
        if len(v) > 1600:
            raise ValueError('Message too long (max 1600 characters)')
        return v.strip()

    @field_validator('media_url')
    @classmethod
    def validate_media_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate media URL if provided"""
        if v is None:
            return None
            
        try:
            result = urlparse(v)
            if not all([result.scheme, result.netloc]):
                raise ValueError('Invalid URL format')
                
            # Check for allowed file extensions
            allowed_extensions = ['.png', '.jpg', '.jpeg', '.pdf', '.doc', '.docx']
            if not any(v.lower().endswith(ext) for ext in allowed_extensions):
                raise ValueError(f'Unsupported file type. Allowed types: {", ".join(allowed_extensions)}')
                
            if len(v) > 2000:  # Reasonable limit for URLs
                raise ValueError('URL is too long')
                
            return v
            
        except Exception as e:
            raise ValueError(f'Invalid media URL: {str(e)}')

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Twilio WhatsApp API",
        "version": "1.0.0",
        "endpoints": {
            "send_message": "/send-whatsapp/",
            "verify_config": "/verify-config",
            "docs": "/docs",
            "openapi": "/openapi.json"
        },
        "status": "running"
    }

# Middleware for request validation
@app.middleware("http")
async def validate_request(request: Request, call_next):
    """Middleware to validate incoming requests"""
    if request.method == "POST":
        try:
            # Validate JSON body
            body = await request.body()
            if body:
                try:
                    await request.json()
                except ValueError:
                    return JSONResponse(
                        status_code=400,
                        content={"detail": "Invalid JSON format in request body"}
                    )
        except Exception as e:
            logger.error(f"Request validation error: {str(e)}")
            return JSONResponse(
                status_code=400,
                content={"detail": "Error processing request"}
            )
    return await call_next(request)

@app.post("/send-whatsapp/", response_model=dict, status_code=200, tags=["Messages"])
async def send_whatsapp_message(message: WhatsAppMessage):
    """
    Send a WhatsApp message with optional media attachment
    
    - **to**: WhatsApp number in format 'whatsapp:+1234567890'
    - **body**: Message content (1-1600 characters)
    - **media_url**: Optional URL of media to attach (image, PDF, or document)
    """
    try:
        logger.info(f"Sending message to {message.to}")
        
        # Prepare message parameters
        message_params = {
            "from_": f"whatsapp:{TWILIO_WHATSAPP_NUMBER}",
            "to": message.to,
            "body": message.body
        }
        
        if message.media_url:
            logger.info(f"Including media: {message.media_url}")
            message_params["media_url"] = [message.media_url]

        # Send message through Twilio
        twilio_message = client.messages.create(**message_params)
        
        logger.info(f"Message sent successfully: {twilio_message.sid}")

        return {
            "status": "success",
            "message_sid": twilio_message.sid,
            "to": twilio_message.to,
            "body": twilio_message.body,
            "num_media": twilio_message.num_media
        }

    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Failed to send message",
                "details": str(e)
            }
        )


@app.get("/verify-config", tags=["Configuration"])
async def verify_config():
    """
    Verify Twilio API configuration
    
    Returns the current configuration status including:
    - Whether the Twilio number is configured
    - If authentication is working
    - The configured WhatsApp number
    """
    try:
        # Test Twilio client connectivity
        account = client.api.accounts(TWILIO_ACCOUNT_SID).fetch()
        
        return {
            "status": "success",
            "twilio_account_sid": account.sid,
            "twilio_number_configured": bool(TWILIO_WHATSAPP_NUMBER),
            "twilio_auth_working": True,
            "whatsapp_number": TWILIO_WHATSAPP_NUMBER,
            "account_status": account.status
        }
    except Exception as e:
        logger.error(f"Configuration verification failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "error": "Configuration verification failed",
                "details": str(e)
            }
        )

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation failed",
            "errors": exc.errors(),
            "error_type": "validation_error",
            "help": {
                "phone_format": "Phone number must be in format 'whatsapp:+1234567890'",
                "body_length": "Message body must be 1-1600 characters",
                "example": {
                    "to": "whatsapp:+1234567890",
                    "body": "Hello! This is a test message."
                }
            }
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder({
            "detail": exc.detail,
            "error_type": "api_error"
        }),
    )

if __name__ == "__main__":
    import uvicorn
    
    # Run the FastAPI application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )