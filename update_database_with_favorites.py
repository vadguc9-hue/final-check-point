#!/usr/bin/env python3
"""
Update database with Favorite model and fix user roles
"""

from database import app, db
from models import User, Category, Product

def update_database():
    with app.app_context():
        # Drop and recreate all tables with new schema
        db.drop_all()
        db.create_all()
        
        # Seed categories
        seed_categories_data()
        
        # Create test users with 'User' role (can both buy and sell)
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
            role='User',  # Can both buy and sell
            phone_number='+1 (555) 123-4567'
        )
        seller_user.set_password('seller123')
        
        buyer_user = User(
            business_name='Eco Builders Inc.',
            username='ecobuyer',
            email='buyer@ecomaterial.com',
            role='User',  # Can both buy and sell
            phone_number='+1 (555) 987-6543'
        )
        buyer_user.set_password('buyer123')
        
        db.session.add_all([admin_user, seller_user, buyer_user])
        db.session.commit()
        
        print("✅ Database updated successfully!")
        print("📝 Added Favorite model for favorites functionality")
        print("👥 Updated all users to 'User' role (can both buy and sell)")
        print("📦 Categories seeded")
        print("❤️ Favorites system ready!")
        print("\n🚀 Ready for testing with favorites and improved user roles!")

def seed_categories_data():
    """Seed initial categories"""
    categories = [
        Category(name='Building Materials', description='Sustainable building and construction materials'),
        Category(name='Insulation', description='Eco-friendly insulation products'),
        Category(name='Flooring', description='Sustainable flooring options'),
        Category(name='Roofing', description='Green roofing materials'),
        Category(name='Paints & Coatings', description='Eco-friendly paints and coatings'),
        Category(name='Plumbing', description='Sustainable plumbing fixtures and materials'),
        Category(name='Electrical', description='Energy-efficient electrical components'),
        Category(name='Landscaping', description='Sustainable landscaping materials'),
        Category(name='Waste Management', description='Recycling and waste reduction products'),
        Category(name='Water Conservation', description='Water-saving products and systems')
    ]
    
    for category in categories:
        db.session.add(category)
    
    db.session.commit()
    print("✅ Categories seeded successfully!")

if __name__ == '__main__':
    update_database()
