#!/usr/bin/env python3
"""
Add test products for testing the search functionality
"""

from app import create_app
from models import db, User, Category, Product

def add_test_products():
    app = create_app()
    with app.app_context():
        # Get the seller user
        seller = User.query.filter_by(email='seller@ecomaterial.com').first()
        if not seller:
            print("❌ Seller user not found!")
            return
        
        # Get categories
        categories = Category.query.all()
        if not categories:
            print("❌ No categories found!")
            return
        
        # Create test products
        test_products = [
            {
                'title': 'Recycled Steel Beams',
                'description': 'High-quality recycled steel beams perfect for construction projects. Environmentally friendly and cost-effective.',
                'category': 'Metals',
                'price': 450.00,
                'quantity': 50
            },
            {
                'title': 'Sustainable Wood Planks',
                'description': 'FSC-certified wood planks from sustainably managed forests. Ideal for eco-friendly building.',
                'category': 'Wood',
                'price': 125.50,
                'quantity': 100
            },
            {
                'title': 'Biodegradable Plastic Sheets',
                'description': 'Environmentally friendly plastic sheets that decompose naturally. Great for packaging.',
                'category': 'Plastics',
                'price': 35.75,
                'quantity': 200
            },
            {
                'title': 'Organic Cotton Fabric',
                'description': '100% organic cotton fabric, perfect for sustainable textile manufacturing.',
                'category': 'Textiles',
                'price': 15.25,
                'quantity': 500
            },
            {
                'title': 'Green Chemical Solvent',
                'description': 'Eco-friendly chemical solvent for industrial cleaning applications.',
                'category': 'Chemicals',
                'price': 89.99,
                'quantity': 25
            },
            {
                'title': 'Metal Construction Frame',
                'description': 'Durable metal frame for construction projects. Made from recycled materials.',
                'category': 'Construction',
                'price': 750.00,
                'quantity': 15
            }
        ]
        
        added_count = 0
        for product_data in test_products:
            # Find category
            category = next((c for c in categories if c.name == product_data['category']), None)
            if not category:
                print(f"❌ Category '{product_data['category']}' not found!")
                continue
            
            # Check if product already exists
            existing = Product.query.filter_by(title=product_data['title']).first()
            if existing:
                print(f"⚠️ Product '{product_data['title']}' already exists!")
                continue
            
            # Create product
            product = Product(
                title=product_data['title'],
                description=product_data['description'],
                category_id=category.id,
                price=product_data['price'],
                quantity=product_data['quantity'],
                seller_id=seller.id
            )
            
            db.session.add(product)
            added_count += 1
            print(f"✅ Added product: {product_data['title']}")
        
        db.session.commit()
        print(f"\n🎉 Successfully added {added_count} test products!")
        print("🔍 You can now test the search functionality!")

if __name__ == '__main__':
    add_test_products()
