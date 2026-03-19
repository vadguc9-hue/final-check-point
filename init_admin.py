#!/usr/bin/env python3
"""
Initialize admin user for testing the authentication system
"""

from app import create_app
from models import db, User, Category, seed_categories

def init_admin():
    app = create_app()
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Seed categories
        seed_categories()
        
        # Check if admin user already exists
        admin_user = User.query.filter_by(email='admin@ecomaterial.com').first()
        if not admin_user:
            # Create admin user
            admin_user = User(
                business_name='EcoMaterial Admin',
                username='admin',
                email='admin@ecomaterial.com',
                role='Admin',
                phone_number='+1 (555) 000-0000'
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
            print("✅ Admin user created successfully!")
            print("   Email: admin@ecomaterial.com")
            print("   Password: admin123")
        else:
            print("ℹ️ Admin user already exists")
        
        # Create test seller user
        seller_user = User.query.filter_by(email='seller@ecomaterial.com').first()
        if not seller_user:
            seller_user = User(
                business_name='Green Materials Co.',
                username='greenseller',
                email='seller@ecomaterial.com',
                role='Seller',
                phone_number='+1 (555) 123-4567'
            )
            seller_user.set_password('seller123')
            db.session.add(seller_user)
            db.session.commit()
            print("✅ Test seller user created successfully!")
            print("   Email: seller@ecomaterial.com")
            print("   Password: seller123")
        else:
            print("ℹ️ Test seller user already exists")
        
        # Create test buyer user
        buyer_user = User.query.filter_by(email='buyer@ecomaterial.com').first()
        if not buyer_user:
            buyer_user = User(
                business_name='Eco Builders Inc.',
                username='ecobuyer',
                email='buyer@ecomaterial.com',
                role='Buyer',
                phone_number='+1 (555) 987-6543'
            )
            buyer_user.set_password('buyer123')
            db.session.add(buyer_user)
            db.session.commit()
            print("✅ Test buyer user created successfully!")
            print("   Email: buyer@ecomaterial.com")
            print("   Password: buyer123")
        else:
            print("ℹ️ Test buyer user already exists")

if __name__ == '__main__':
    init_admin()
    print("\n🚀 Authentication system is ready for testing!")
    print("📱 Open http://127.0.0.1:5000 to start testing")
