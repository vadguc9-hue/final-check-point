#!/usr/bin/env python3
"""
Test script to simulate SMS payment processing
"""

import requests
import json

def test_sms_payment():
    """Test the SMS payment API endpoint"""
    # Test data - simulate an SMS payment
    payment_data = {
        'sender_phone': '+994501234567',  # Phone number that sent SMS
        'amount': 5,  # 5 manat
        'message': 'PAY 5',  # SMS content
        'transaction_id': 'TEST_TX_123456'  # Unique transaction ID
    }
    
    try:
        # Send POST request to payment API
        response = requests.post(
            'http://localhost:5000/api/payment/sms',
            json=payment_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Payment processed successfully!")
            print(f"User ID: {result.get('user_id')}")
            print(f"New Balance: {result.get('new_balance')} tokens")
            print(f"Payment ID: {result.get('payment_id')}")
        else:
            print(f"❌ Payment failed: {response.status_code}")
            print(response.json())
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to the server. Make sure the Flask app is running on localhost:5000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    print("Testing SMS Payment System...")
    print("Note: This requires a user with phone number '+994501234567' to exist in the database")
    print("=" * 60)
    test_sms_payment()
