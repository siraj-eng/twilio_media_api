# Twilio WhatsApp API

A FastAPI application for sending WhatsApp messages using Twilio's API.

## Features

- Send WhatsApp text messages
- Send messages with media attachments (images, documents)
- Input validation and error handling
- Environment-based configuration
- CORS support

## Prerequisites

- Python 3.8+
- Twilio account with WhatsApp Sandbox access
- Twilio Account SID and Auth Token

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your Twilio credentials:
   ```env
   TWILIO_ACCOUNT_SID=your_account_sid
   TWILIO_AUTH_TOKEN=your_auth_token
   TWILIO_WHATSAPP_NUMBER=+1234567890  # Your Twilio WhatsApp number
   ```

## Usage

1. Start the server:
   ```bash
   python main.py
   ```
2. The API will be available at `http://localhost:8000`
3. Access interactive docs at `http://localhost:8000/docs`

## API Endpoints

### Send Message

```
POST /send-whatsapp/
```

**Request Body:**
```json
{
  "to": "whatsapp:+1234567890",
  "body": "Your message here"
}
```

### Send Message with Media

```
POST /send-whatsapp/
```

**Request Body:**
```json
{
  "to": "whatsapp:+1234567890",
  "body": "Check this out!",
  "media_url": "https://example.com/image.jpg"
}
```

## Testing

The test client provides a comprehensive way to test all API endpoints. It includes tests for:
- Configuration verification
- Sending text messages
- Sending media messages
- Input validation

### Running Tests

1. Make sure the API server is running:
   ```bash
   python main.py
   ```

2. In a separate terminal, run the test client:
   ```bash
   python example_usage.py --to +254716160370
   ```

   Replace `+254716160370` with your WhatsApp number in international format (without the 'whatsapp:' prefix).

### Command Line Options

- `--base-url`: Base URL of the API (default: http://localhost:8000)
- `--to`: WhatsApp number to send test messages to (required, without 'whatsapp:' prefix)

Example:
```bash
python example_usage.py --base-url http://localhost:8000 --to +254716160370
```

## License

MIT

**Request Body:**
```json
{
  "to": "whatsapp:+1234567890",
  "body": "Your message here",
  "media_url": "https://example.com/image.jpg" // optional
}
```

**Response:**
```json
{
  "status": "success",
  "message_sid": "SM1234567890abcdef",
  "to": "whatsapp:+1234567890",
  "body": "Your message here",
  "num_media": "0"
}
```

### GET `/verify-config`

Verify Twilio configuration.

**Response:**
```json
{
  "twilio_number_configured": true,
  "twilio_auth_working": true,
  "whatsapp_number": "+1234567890"
}
```

## Testing

### Run Unit Tests

```bash
pytest test_main.py -v
```

### Run Example Usage Script

```bash
python example_usage.py
```

### Manual Testing with curl

```bash
# Test configuration
curl http://localhost:8000/verify-config

# Send a message
curl -X POST http://localhost:8000/send-whatsapp/ \
  -H "Content-Type: application/json" \
  -d '{
    "to": "whatsapp:+1234567890",
    "body": "Hello from API!"
  }'
```

## Validation Rules

- **Phone Number**: Must be in format `whatsapp:+1234567890`
- **Message Body**: 1-1600 characters
- **Media URL**: Optional, must be a valid URL

## Error Handling

The API provides detailed error messages for:
- Invalid phone number formats
- Message body length violations
- Twilio API errors
- Invalid JSON requests

## Development

### Project Structure

```
twilio_api_doc/
├── main.py              # Main FastAPI application
├── test_main.py         # Unit tests
├── example_usage.py     # Example usage script
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (create this)
└── README.md           # This file
```

### Key Features Fixed

1. **SSL Configuration**: Removed hardcoded SSL certificates for easier development
2. **Dependencies**: Added `requirements.txt` with all necessary packages
3. **Testing**: Comprehensive test suite with mocked Twilio client
4. **Examples**: Ready-to-use example scripts for testing

## Troubleshooting

### Common Issues

1. **"Twilio initialization failed"**
   - Check your `.env` file has correct Twilio credentials
   - Verify credentials in Twilio Console

2. **Connection refused**
   - Make sure the server is running (`python main.py`)
   - Check if port 8000 is available

3. **Validation errors**
   - Ensure phone numbers include `whatsapp:` prefix
   - Check message body length (1-1600 characters)

### Getting Twilio Credentials

1. Sign up at [Twilio](https://www.twilio.com/)
2. Get your Account SID and Auth Token from the Console
3. Set up WhatsApp Sandbox or get approved WhatsApp number
4. Add credentials to your `.env` file

## License

This project is for educational/development purposes.
