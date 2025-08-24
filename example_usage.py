"""
Twilio WhatsApp API Test Client

This script provides example usage of the Twilio WhatsApp API endpoints.
It includes test cases for sending messages, media, and error handling.
"""

import argparse
import json
import sys
from typing import Dict, Any, Optional, Tuple

import requests

# API configuration
DEFAULT_BASE_URL = "http://localhost:8000"
TEST_IMAGE_URL = "https://picsum.photos/1200/800"

class WhatsAppAPITest:
    """Test client for WhatsApp API endpoints"""
    
    def __init__(self, base_url: str = DEFAULT_BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def test_config_endpoint(self) -> Tuple[bool, str]:
        """Test the configuration verification endpoint"""
        endpoint = f"{self.base_url}/verify-config"
        print(f"Testing GET {endpoint}")
        
        try:
            response = self.session.get(endpoint)
            response.raise_for_status()
            print(f"✓ Success\n{json.dumps(response.json(), indent=2)}")
            return True, "Configuration verified"
            
        except requests.exceptions.RequestException as e:
            error_msg = self._format_error(e)
            print(f"✗ Failed: {error_msg}")
            return False, error_msg

    def test_send_message(self, to_number: str, message: str) -> Tuple[bool, str]:
        """Test sending a text message"""
        endpoint = f"{self.base_url}/send-whatsapp/"
        payload = {
            "to": f"whatsapp:{to_number}",
            "body": message
        }
        
        print(f"\nTesting POST {endpoint}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        try:
            response = self.session.post(endpoint, json=payload)
            response.raise_for_status()
            print(f"✓ Message sent successfully\n{json.dumps(response.json(), indent=2)}")
            return True, "Message sent successfully"
            
        except requests.exceptions.RequestException as e:
            error_msg = self._format_error(e)
            print(f"✗ Failed to send message: {error_msg}")
            return False, error_msg

    def test_send_media_message(self, to_number: str, message: str, media_url: str) -> Tuple[bool, str]:
        """Test sending a message with media attachment"""
        endpoint = f"{self.base_url}/send-whatsapp/"
        payload = {
            "to": f"whatsapp:{to_number}",
            "body": message,
            "media_url": media_url
        }
        
        print(f"\nTesting POST {endpoint} with media")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        try:
            response = self.session.post(endpoint, json=payload)
            response.raise_for_status()
            print(f"✓ Media message sent successfully\n{json.dumps(response.json(), indent=2)}")
            return True, "Media message sent successfully"
            
        except requests.exceptions.RequestException as e:
            error_msg = self._format_error(e)
            print(f"✗ Failed to send media message: {error_msg}")
            return False, error_msg

    def test_invalid_phone_format(self) -> Tuple[bool, str]:
        """Test validation with invalid phone number format"""
        endpoint = f"{self.base_url}/send-whatsapp/"
        payload = {
            "to": "+254716160370",  # Missing 'whatsapp:' prefix
            "body": "This should fail validation"
        }
        
        print(f"\nTesting invalid phone number format")
        print(f"Sending to: {endpoint}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        try:
            response = self.session.post(endpoint, json=payload)
            if response.status_code == 422:
                print("✓ Correctly received validation error")
                print(f"Response: {json.dumps(response.json(), indent=2)}")
                return True, "Validation error as expected"
            else:
                print(f"✗ Expected 422 but got {response.status_code}")
                return False, f"Unexpected status code: {response.status_code}"
                
        except requests.exceptions.RequestException as e:
            error_msg = self._format_error(e)
            print(f"✗ Request failed: {error_msg}")
            return False, error_msg
    
    def _format_error(self, error: Exception) -> str:
        """Format error message from exception"""
        if hasattr(error, 'response') and error.response is not None:
            try:
                error_data = error.response.json()
                return f"{error}: {error_data.get('detail', 'No details')}"
            except ValueError:
                return str(error)
        return str(error)

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Test Twilio WhatsApp API')
    parser.add_argument('--base-url', default=DEFAULT_BASE_URL,
                       help=f'Base URL of the API (default: {DEFAULT_BASE_URL})')
    parser.add_argument('--to', required=True,
                       help='WhatsApp number to send test messages to (without whatsapp: prefix)')
    return parser.parse_args()

def run_tests(api: WhatsAppAPITest, to_number: str) -> bool:
    """Run all test cases"""
    test_cases = [
        ("Configuration", lambda: api.test_config_endpoint()),
        ("Send Text Message", lambda: api.test_send_message(
            to_number, "Hello from Twilio WhatsApp API Test")),
        ("Send Media Message", lambda: api.test_send_media_message(
            to_number, "Check out this test image!", TEST_IMAGE_URL)),
        ("Invalid Phone Format", lambda: api.test_invalid_phone_format())
    ]
    
    print("\n" + "=" * 50)
    print(" TWILIO WHATSAPP API TEST SUITE")
    print("=" * 50)
    
    results = []
    for name, test_func in test_cases:
        print(f"\n{' ' + name + ' ':-^50}")
        success, message = test_func()
        results.append((name, success, message))
    
    # Print summary
    print("\n" + "=" * 50)
    print(" TEST SUMMARY")
    print("=" * 50)
    
    for name, success, message in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status} - {name}")
        if not success:
            print(f"   {message}")
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    print(f"\nResults: {passed}/{total} tests passed")
    
    return all(success for _, success, _ in results)

if __name__ == "__main__":
    args = parse_arguments()
    api = WhatsAppAPITest(base_url=args.base_url)
    
    try:
        success = run_tests(api, args.to)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nTest run interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        sys.exit(1)
