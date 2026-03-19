#!/usr/bin/env python3
"""
Test payment processing without Telegram bot
"""

import requests
import json

def test_payment_web():
    """Test payment processing via web interface"""
    
    print("=== Payment Testing Web Interface ===")
    print("Open this URL in your browser:")
    print("http://localhost:5000/test-payment")
    print()
    print("Or use this curl command:")
    print('curl -X POST http://localhost:5000/api/payment/test -H "Content-Type: application/json" -d \'{"username": "your_username", "amount": 5}\'')
    print()
    
    # Test with a sample request
    test_data = {
        'telegram_id': '123456789',
        'username': 'test_user',  # Change this to your actual username
        'amount': 5,
        'message': 'PAY 5'
    }
    
    try:
        response = requests.post(
            'http://127.0.0.1:5000/api/payment/telegram',
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Test Payment Successful!")
            print(f"Response: {result}")
        else:
            print(f"❌ Test Failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        print("Make sure your Flask app is running on localhost:5000")

if __name__ == '__main__':
    test_payment_web()
