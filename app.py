from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm, CSRFProtect
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import uuid
import logging

from database import db, app
from models import User, Product, Category, Review, Favorite, Payment
from forms import LoginForm, RegistrationForm, ProductForm, ReviewForm, SearchForm, ProfileForm

# Initialize extensions
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Routes
@app.route('/', methods=['GET', 'POST'])
def home():
    """Home page with search functionality"""
    form = SearchForm()
    
    # Load categories for search dropdown
    try:
        categories = Category.query.all()
        form.category.choices = [(0, 'All Categories')]
        if current_user.is_authenticated:
            form.category.choices.append((-1, '❤️ My Favorites'))
        form.category.choices += [(c.id, c.name) for c in categories]
    except Exception as e:
        logger.error(f"Error loading home page categories: {e}")
        categories = []
        form.category.choices = [(0, 'All Categories')]
    
    # Handle search on home page
    products = []
    search_performed = False
    
    if request.method == 'POST' and form.validate_on_submit():
        query = form.query.data.strip() if form.query.data else ''
        category_id = form.category.data
        search_performed = True
        
        logger.info(f"Home search query: '{query}', category_id: {category_id}")
        
        # Handle favorites category
        if category_id == -1:  # Favorites category
            if current_user.is_authenticated:
                favorite_product_ids = [f.product_id for f in Favorite.query.filter_by(user_id=current_user.id).all()]
                products = Product.query.filter(Product.id.in_(favorite_product_ids)).order_by(Product.created_at.desc()).all()
            else:
                products = []
        else:
            # Regular search
            product_query = Product.query.filter_by(status='Available')
            
            if category_id and category_id != 0:
                product_query = product_query.filter_by(category_id=category_id)
            
            if query:
                product_query = product_query.filter(
                    Product.title.contains(query) | 
                    Product.description.contains(query)
                )
            
            products = product_query.order_by(Product.created_at.desc()).all()
            logger.info(f"Home search found {len(products)} products")
    else:
        # Show featured products when no search is performed
        try:
            products = Product.query.filter_by(status='Available').order_by(Product.created_at.desc()).limit(6).all()
        except Exception as e:
            logger.error(f"Error loading featured products: {e}")
            products = []
    
    return render_template('home.html', products=products, categories=categories, form=form, search_performed=search_performed)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page"""
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if email already exists
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already exists', 'error')
            return render_template('register.html', form=form)
        
        # Check if username already exists
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists', 'error')
            return render_template('register.html', form=form)
        
        # Create new user
        user = User(
            business_name=form.business_name.data,
            username=form.username.data,
            email=form.email.data,
            phone_number=form.phone_number.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    """Logout user"""
    logout_user()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('home'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile page"""
    form = ProfileForm()
    
    if form.validate_on_submit():
        # Update user information
        current_user.business_name = form.business_name.data
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.phone_number = form.phone_number.data
        current_user.telegram_id = form.telegram_id.data
        
        # Handle password change
        if form.new_password.data:
            if form.current_password.data and current_user.check_password(form.current_password.data):
                current_user.set_password(form.new_password.data)
                flash('Password updated successfully!', 'success')
            else:
                flash('Current password is incorrect', 'error')
                return render_template('profile.html', form=form)
        
        # Check for duplicates
        if User.query.filter(User.id != current_user.id, User.email == form.email.data).first():
            flash('Email already exists', 'error')
            return render_template('profile.html', form=form)
        
        if User.query.filter(User.id != current_user.id, User.username == form.username.data).first():
            flash('Username already exists', 'error')
            return render_template('profile.html', form=form)
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    
    elif request.method == 'GET':
        # Pre-fill form with current user data
        form.business_name.data = current_user.business_name
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.phone_number.data = current_user.phone_number
        form.telegram_id.data = current_user.telegram_id
    
    return render_template('profile.html', form=form, balance=float(current_user.balance))

@app.route('/sell', methods=['GET', 'POST'])
@login_required
def sell():
    """Sell product page"""
    # Check if user has sufficient balance (require at least 1 token to sell)
    if current_user.balance < 1:
        flash('You need at least 1 token to sell products. Please add funds to your account.', 'error')
        return redirect(url_for('payment_instructions'))
    
    form = ProductForm()
    
    # Populate category choices
    try:
        categories = Category.query.all()
        form.category_id.choices = [(c.id, c.name) for c in categories]
        logger.info(f"Loaded {len(categories)} categories for product form")
    except Exception as e:
        logger.error(f"Error loading categories: {e}")
        form.category_id.choices = []
    
    if form.validate_on_submit():
        # Handle file upload
        photo_filename = None
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename:
                # Generate unique filename
                filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
                photo_filename = secure_filename(filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))
        
        # Create new product
        product = Product(
            title=form.title.data,
            description=form.description.data,
            price=form.price.data,
            quantity=form.quantity.data,
            category_id=form.category_id.data,
            status=form.status.data,
            seller_id=current_user.id,
            photo_filename=photo_filename
        )
        
        db.session.add(product)
        db.session.commit()
        
        flash('Product listed successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('sell.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    try:
        user_products = Product.query.filter_by(seller_id=current_user.id).order_by(Product.created_at.desc()).all()
    except Exception as e:
        logger.error(f"Error loading dashboard: {e}")
        user_products = []
    
    # Create a form for CSRF token
    from forms import SearchForm
    form = SearchForm()
    return render_template('dashboard.html', products=user_products, form=form, balance=float(current_user.balance))

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    """Product detail page"""
    product = Product.query.get_or_404(product_id)
    
    # Check if current user has favorited this product
    is_favorited = False
    if current_user.is_authenticated:
        is_favorited = Favorite.query.filter_by(user_id=current_user.id, product_id=product_id).first() is not None
        has_reviewed = Review.query.filter_by(product_id=product_id, reviewer_id=current_user.id).first() is not None
    else:
        has_reviewed = False
    
    # Create a form for CSRF token
    from forms import SearchForm
    form = SearchForm()
    return render_template('product_detail.html', product=product, is_favorited=is_favorited, has_reviewed=has_reviewed, form=form)

@app.route('/product/<int:product_id>/review', methods=['POST'])
@login_required
def add_review(product_id):
    """Add a review to a product"""
    product = Product.query.get_or_404(product_id)
    
    # Check if user already reviewed this product
    existing_review = Review.query.filter_by(product_id=product_id, reviewer_id=current_user.id).first()
    if existing_review:
        flash('You have already reviewed this product', 'error')
        return redirect(url_for('product_detail', product_id=product_id))
    
    form = ReviewForm()
    if form.validate_on_submit():
        review = Review(
            rating=form.rating.data,
            comment=form.comment.data,
            product_id=product_id,
            reviewer_id=current_user.id
        )
        
        db.session.add(review)
        db.session.commit()
        
        flash('Review added successfully!', 'success')
    else:
        flash('Invalid review data', 'error')
    
    return redirect(url_for('product_detail', product_id=product_id))

@app.route('/toggle_favorite/<int:product_id>', methods=['POST'])
@login_required
def toggle_favorite(product_id):
    """Toggle favorite status"""
    try:
        product = Product.query.get_or_404(product_id)
        
        existing_favorite = Favorite.query.filter_by(user_id=current_user.id, product_id=product_id).first()
        
        if existing_favorite:
            # Remove from favorites
            db.session.delete(existing_favorite)
            action = 'removed'
            message = 'Removed from favorites'
        else:
            # Add to favorites
            favorite = Favorite(user_id=current_user.id, product_id=product_id)
            db.session.add(favorite)
            action = 'added'
            message = 'Added to favorites'
        
        db.session.commit()
        
        # Return JSON for AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
            return jsonify({'success': True, 'action': action, 'message': message})
        else:
            flash(message, 'success' if action == 'added' else 'info')
            return redirect(url_for('product_detail', product_id=product_id))
    
    except Exception as e:
        db.session.rollback()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 500
        else:
            flash('An error occurred while updating favorites', 'error')
            return redirect(url_for('product_detail', product_id=product_id))

@app.route('/favorites')
@login_required
def favorites():
    """User favorites page"""
    try:
        favorites = Favorite.query.filter_by(user_id=current_user.id).order_by(Favorite.created_at.desc()).all()
    except Exception as e:
        logger.error(f"Error loading favorites: {e}")
        favorites = []
    
    # Create a form for CSRF token
    from forms import SearchForm
    form = SearchForm()
    return render_template('favorites.html', favorites=favorites, form=form)

@app.route('/search', methods=['GET', 'POST'])
def search():
    """Search products"""
    form = SearchForm()
    
    try:
        categories = Category.query.all()
        form.category.choices = [(0, 'All Categories')]
        if current_user.is_authenticated:
            form.category.choices.append((-1, '❤️ My Favorites'))
        form.category.choices += [(c.id, c.name) for c in categories]
    except Exception as e:
        logger.error(f"Error loading search categories: {e}")
        categories = []
        form.category.choices = [(0, 'All Categories')]
    
    products = []
    if request.method == 'POST' and form.validate_on_submit():
        query = form.query.data.strip() if form.query.data else ''
        category_id = form.category.data
        
        logger.info(f"Search query: '{query}', category_id: {category_id}")
        logger.info(f"Form validation passed: {form.validate_on_submit()}")
        logger.info(f"Form errors: {form.errors}")
        
        # Handle favorites category
        if category_id == -1:  # Favorites category
            if current_user.is_authenticated:
                favorite_product_ids = [f.product_id for f in Favorite.query.filter_by(user_id=current_user.id).all()]
                products = Product.query.filter(Product.id.in_(favorite_product_ids)).order_by(Product.created_at.desc()).all()
            else:
                products = []
        else:
            # Regular search
            product_query = Product.query.filter_by(status='Available')
            
            if category_id and category_id != 0:
                product_query = product_query.filter_by(category_id=category_id)
            
            if query:
                product_query = product_query.filter(
                    Product.title.contains(query) | 
                    Product.description.contains(query)
                )
            
            products = product_query.order_by(Product.created_at.desc()).all()
            logger.info(f"Found {len(products)} products with query '{query}'")
            for p in products:
                logger.info(f"  - {p.title}")
    elif request.method == 'GET':
        # Show all available products on initial load
        products = Product.query.filter_by(status='Available').order_by(Product.created_at.desc()).all()
    
    return render_template('search.html', form=form, products=products, categories=categories)

@app.route('/api/search')
def api_search():
    """API endpoint for AJAX search"""
    query = request.args.get('q', '').strip()
    category_id = request.args.get('category', type=int)
    
    if not query:
        return jsonify([])
    
    try:
        product_query = Product.query.filter_by(status='Available')
        
        if category_id and category_id > 0:
            product_query = product_query.filter_by(category_id=category_id)
        
        if query:
            product_query = product_query.filter(
                Product.title.contains(query) | 
                Product.description.contains(query)
            )
        
        products = product_query.order_by(Product.created_at.desc()).limit(20).all()
        
        # Format for JSON response
        result = []
        for product in products:
            is_favorited = False
            if current_user.is_authenticated:
                is_favorited = Favorite.query.filter_by(user_id=current_user.id, product_id=product.id).first() is not None
            
            result.append({
                'id': product.id,
                'title': product.title,
                'description': product.description,
                'price': float(product.price),
                'category': product.category.name if product.category else 'Unknown',
                'is_favorited': is_favorited,
                'photo_filename': product.photo_filename
            })
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin')
@login_required
def admin():
    """Admin dashboard"""
    if current_user.role != 'Admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
    try:
        products = Product.query.order_by(Product.created_at.desc()).all()
    except Exception as e:
        logger.error(f"Error loading admin dashboard: {e}")
        products = []
    
    return render_template('admin.html', products=products)

@app.route('/product/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    """Edit a product"""
    product = Product.query.get_or_404(product_id)
    
    # Check if current user is the seller
    if product.seller_id != current_user.id:
        flash('You can only edit your own products', 'error')
        return redirect(url_for('dashboard'))
    
    form = ProductForm()
    
    # Populate category choices
    try:
        categories = Category.query.all()
        form.category_id.choices = [(c.id, c.name) for c in categories]
        logger.info(f"Loaded {len(categories)} categories for edit form")
    except Exception as e:
        logger.error(f"Error loading categories: {e}")
        form.category_id.choices = []
    
    if form.validate_on_submit():
        # Handle file upload
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename:
                # Generate unique filename
                filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
                photo_filename = secure_filename(filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))
                product.photo_filename = photo_filename
        
        # Update product fields
        product.title = form.title.data
        product.description = form.description.data
        product.price = form.price.data
        product.quantity = form.quantity.data
        product.category_id = form.category_id.data
        product.status = form.status.data
        
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    elif request.method == 'GET':
        # Pre-fill form with current product data
        form.title.data = product.title
        form.description.data = product.description
        form.price.data = float(product.price)
        form.quantity.data = product.quantity
        form.category_id.data = product.category_id
        form.status.data = product.status
    
    return render_template('edit_product.html', form=form, product=product)

@app.route('/product/<int:product_id>/delete', methods=['POST'])
@login_required
def delete_product(product_id):
    """Delete a product (owner only)"""
    product = Product.query.get_or_404(product_id)
    
    # Check if current user is the seller or admin
    if product.seller_id != current_user.id and current_user.role != 'Admin':
        flash('Access denied. You can only delete your own products.', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        # Delete the product (this will also delete related reviews and favorites due to cascade)
        db.session.delete(product)
        db.session.commit()
        flash(f'Product "{product.title}" has been deleted successfully.', 'success')
        logger.info(f'Product {product_id} deleted by user {current_user.id}')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting product {product_id}: {e}")
        flash('An error occurred while deleting the product. Please try again.', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/admin/delete_product/<int:product_id>')
@login_required
def admin_delete_product(product_id):
    """Delete a product (admin only)"""
    if current_user.role != 'Admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash(f'Product "{product.title}" has been deleted', 'success')
    return redirect(url_for('admin'))

@app.route('/payment-instructions')
@login_required
def payment_instructions():
    """Payment instructions page"""
    return render_template('payment_instructions.html', balance=float(current_user.balance))

@app.route('/view-seller/<int:product_id>')
@login_required
def view_seller_number(product_id):
    """View seller phone number (requires tokens)"""
    product = Product.query.get_or_404(product_id)
    
    # Check if user has sufficient balance (require at least 1 token)
    if current_user.balance < 1:
        flash('You need at least 1 token to view seller contact information. Please add funds to your account.', 'error')
        return redirect(url_for('payment_instructions'))
    
    # Deduct 1 token for viewing seller number
    current_user.balance -= 1
    db.session.commit()
    
    flash('1 token has been deducted for viewing seller contact information.', 'info')
    return render_template('seller_contact.html', product=product, seller=product.seller)

@app.route('/test-payment')
def test_payment_page():
    """Simple test page for payment processing"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Payment Test</title>
        <style>
            body { font-family: Arial; padding: 20px; }
            .container { max-width: 600px; margin: 0 auto; }
            .form-group { margin: 10px 0; }
            input, button { padding: 10px; margin: 5px; }
            .result { margin: 20px 0; padding: 10px; background: #f0f0f0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>🧪 Payment Testing Interface</h2>
            <p>Test your payment system without Telegram bot</p>
            
            <form id="paymentForm">
                <div class="form-group">
                    <label>Username:</label>
                    <input type="text" id="username" value="your_username" required>
                </div>
                <div class="form-group">
                    <label>Amount:</label>
                    <input type="number" id="amount" value="5" min="1" required>
                </div>
                <button type="submit">Test Payment</button>
            </form>
            
            <div id="result" class="result" style="display:none;"></div>
        </div>
        
        <script>
        document.getElementById('paymentForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const data = {
                telegram_id: '123456789',
                username: document.getElementById('username').value,
                amount: parseFloat(document.getElementById('amount').value),
                message: 'PAY ' + document.getElementById('amount').value
            };
            
            try {
                const response = await fetch('/api/payment/telegram', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                const resultDiv = document.getElementById('result');
                
                if (response.ok) {
                    resultDiv.innerHTML = `
                        <h3>✅ Payment Successful!</h3>
                        <p><strong>Amount:</strong> ${result.amount} tokens</p>
                        <p><strong>New Balance:</strong> ${result.new_balance} tokens</p>
                        <p><strong>Transaction ID:</strong> ${result.payment_id}</p>
                        <p><strong>User ID:</strong> ${result.user_id}</p>
                    `;
                    resultDiv.style.background = '#d4edda';
                } else {
                    resultDiv.innerHTML = `
                        <h3>❌ Payment Failed</h3>
                        <p><strong>Error:</strong> ${result.error}</p>
                    `;
                    resultDiv.style.background = '#f8d7da';
                }
                
                resultDiv.style.display = 'block';
            } catch (error) {
                document.getElementById('result').innerHTML = `
                    <h3>❌ Connection Error</h3>
                    <p>${error.message}</p>
                `;
                document.getElementById('result').style.display = 'block';
            }
        });
        </script>
    </body>
    </html>
    '''

@app.route('/api/payment/test', methods=['POST'])
def test_payment_api():
    """Simple test API endpoint"""
    return jsonify({
        'message': 'Test API is working',
        'status': 'success'
    })

@app.route('/api/payment/telegram', methods=['POST'])
@csrf.exempt  # Disable CSRF for API endpoint
def telegram_payment():
    """API endpoint to receive Telegram payment notifications"""
    try:
        data = request.get_json()
        
        telegram_id = data.get('telegram_id')
        username = data.get('username')
        amount = data.get('amount')
        message_text = data.get('message', '')
        
        if not telegram_id or not amount or amount <= 0:
            return jsonify({'error': 'Invalid telegram_id or amount'}), 400
        
        # Find user by telegram_id, username, or phone number
        user = None
        
        # Try to find by telegram_id first
        if telegram_id:
            user = User.query.filter_by(telegram_id=str(telegram_id)).first()
        
        # If not found, try username
        if not user and username:
            user = User.query.filter_by(username=username).first()
        
        # If still not found, try phone number (for users who registered with phone as telegram_id)
        if not user:
            user = User.query.filter_by(phone_number=str(telegram_id)).first()
        
        if not user:
            return jsonify({'error': 'User not found. Please link your Telegram account in profile.'}), 404
        
        # Generate unique transaction ID
        transaction_id = f"TG_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{str(telegram_id)[-4:]}"
        
        # Check if transaction already exists
        existing_payment = Payment.query.filter_by(transaction_id=transaction_id).first()
        if existing_payment:
            return jsonify({'error': 'Transaction already processed'}), 400
        
        # Create payment record
        payment = Payment(
            amount=amount,
            sender_phone=f"TG_{telegram_id}",  # Store Telegram ID as phone
            transaction_id=transaction_id,
            user_id=user.id,
            status='completed',
            processed_at=datetime.utcnow()
        )
        
        # Update user balance
        user.balance += amount
        
        # Save to database
        db.session.add(payment)
        db.session.commit()
        
        logger.info(f"Telegram payment processed: {amount} manat from @{username} (TG:{telegram_id})")
        
        return jsonify({
            'success': True,
            'message': 'Payment processed successfully',
            'user_id': user.id,
            'new_balance': float(user.balance),
            'payment_id': payment.id
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error processing Telegram payment: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/payment/sms', methods=['POST'])
def sms_payment():
    """API endpoint to receive SMS payment notifications (Clickatell compatible)"""
    try:
        # Get SMS data from request (Clickatell format)
        data = request.get_json() if request.is_json else request.form
        
        # Clickatell webhook format
        if request.is_json:
            sender_phone = data.get('from_number') or data.get('sender_phone')
            message_text = data.get('text') or data.get('message', '')
        else:
            # Form data format
            sender_phone = data.get('from_number') or data.get('sender_phone')
            message_text = data.get('text') or data.get('message', '')
        
        # Extract amount from message (e.g., "PAY 5" -> 5)
        amount = 0
        import re
        match = re.search(r'PAY\s+(\d+(?:\.\d+)?)', message_text.upper())
        if match:
            amount = float(match.group(1))
        
        if not sender_phone or amount <= 0:
            return jsonify({'error': 'Invalid phone number or amount'}), 400
        
        # Clean phone number (remove +, spaces, etc.)
        sender_phone = re.sub(r'[^\d]', '', sender_phone)
        if len(sender_phone) == 9 and not sender_phone.startswith('994'):
            sender_phone = '994' + sender_phone
        
        # Find user by phone number
        user = User.query.filter_by(phone_number=sender_phone).first()
        if not user:
            return jsonify({'error': 'User not found for this phone number'}), 404
        
        # Generate unique transaction ID
        transaction_id = f"CL_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{sender_phone[-4:]}"
        
        # Check if transaction already exists
        existing_payment = Payment.query.filter_by(transaction_id=transaction_id).first()
        if existing_payment:
            return jsonify({'error': 'Transaction already processed'}), 400
        
        # Create payment record
        payment = Payment(
            amount=amount,
            sender_phone=sender_phone,
            transaction_id=transaction_id,
            user_id=user.id,
            status='completed',
            processed_at=datetime.utcnow()
        )
        
        # Update user balance
        user.balance += amount
        
        # Save to database
        db.session.add(payment)
        db.session.commit()
        
        logger.info(f"Clickatell payment processed: {amount} manat from {sender_phone} for user {user.id}")
        
        return jsonify({
            'success': True,
            'message': 'Payment processed successfully',
            'user_id': user.id,
            'new_balance': float(user.balance),
            'payment_id': payment.id
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error processing SMS payment: {e}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
