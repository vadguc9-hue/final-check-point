#!/usr/bin/env python3
"""
Update database with new Review model and re-initialize data
"""

from app import create_app
from models import db, User, Category, Product, seed_categories

def update_database():
    app = create_app()
    with app.app_context():
        # Drop and recreate all tables with new schema
        db.drop_all()
        db.create_all()
        
        # Seed categories
        seed_categories()
        
        # Create test users
        admin_user = User(
            business_name='EcoMaterial Admin',
            username='admin',
            email='admin@ecomaterial.com',
            role='Admin',
            phone_number='+1 (555) 000-0000'
        )
        admin_user.set_password('admin123')
        
        seller_user = User(
            business_name='Green Materials Co.',
            username='greenseller',
            email='seller@ecomaterial.com',
            role='Seller',
            phone_number='+1 (555) 123-4567'
        )
        seller_user.set_password('seller123')
        
        buyer_user = User(
            business_name='Eco Builders Inc.',
            username='ecobuyer',
            email='buyer@ecomaterial.com',
            role='Buyer',
            phone_number='+1 (555) 987-6543'
        )
        buyer_user.set_password('buyer123')
        
        db.session.add_all([admin_user, seller_user, buyer_user])
        db.session.commit()
        
        print("✅ Database updated successfully!")
        print("📝 Added Review model for star ratings")
        print("👥 Re-created test users")
        print("📦 Categories seeded")
        print("\n🚀 Ready for testing with reviews and AJAX search!")

if __name__ == '__main__':
    update_database()
