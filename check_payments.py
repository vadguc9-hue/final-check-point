#!/usr/bin/env python3
"""
Check recent payments and user balances
"""

from database import db, app
from models import User, Payment

def check_payments():
    with app.app_context():
        print("=== Recent Payments ===")
        payments = Payment.query.order_by(Payment.created_at.desc()).limit(10).all()
        
        if not payments:
            print("No payments found yet.")
        else:
            for payment in payments:
                user = User.query.get(payment.user_id)
                print(f"Payment ID: {payment.id}")
                print(f"User: {user.username if user else 'Unknown'}")
                print(f"Amount: {payment.amount} tokens")
                print(f"From: {payment.sender_phone}")
                print(f"Status: {payment.status}")
                print(f"Transaction ID: {payment.transaction_id}")
                print(f"Created: {payment.created_at}")
                print("-" * 40)
        
        print("\n=== User Balances ===")
        users = User.query.all()
        for user in users:
            print(f"{user.username}: {user.balance} tokens")

if __name__ == '__main__':
    check_payments()
