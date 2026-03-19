# EcoMaterial Hub

A high-end, mobile-responsive Flask B2B marketplace for sustainable materials and resources.

## Features

- **Mobile-First Design**: Responsive layout with bottom navigation for mobile and traditional navbar for desktop
- **Sustainable Tech Palette**: Forest Green, Mint, and Slate color scheme
- **Flask Factory Architecture**: Modular structure with app.py, models.py, forms.py
- **Database Support**: SQLite for development, PostgreSQL ready for Railway deployment
- **Product Management**: List, search, and browse materials by category
- **User Profiles**: Track listings and manage account settings

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Up Environment**
   ```bash
   # Copy .env file and update with your settings
   cp .env.example .env
   ```

3. **Initialize Database**
   ```bash
   python app.py
   # Visit http://localhost:5000/init_db to seed categories
   ```

4. **Run the Application**
   ```bash
   python app.py
   ```

5. **Open in Browser**
   Visit `http://localhost:5000`

## Project Structure

```
EcoMaterial Hub/
├── app.py              # Flask application factory
├── models.py           # SQLAlchemy models (User, Category, Product)
├── forms.py            # WTForms for user input
├── routes.py           # Application routes and views
├── requirements.txt    # Python dependencies
├── .env               # Environment variables
├── static/
│   ├── uploads/       # User uploaded images
│   └── style.css      # Mobile-first CSS with sustainable colors
└── templates/
    ├── layout.html    # Base template with responsive navigation
    ├── home.html      # Homepage with featured products
    ├── search.html    # Product search and filtering
    ├── sell.html      # Product listing form
    ├── profile.html   # User profile and listings
    └── product_detail.html  # Individual product view
```

## Database Models

### User
- id, username, email, password_hash, role, phone_number
- Relationships: Products (as seller)

### Category  
- id, name, description
- Seeded categories: Construction, Wood, Metals, Plastics, Textiles, Chemicals
- Relationships: Products

### Product
- id, title, category_id, description, photo_filename, price, quantity, status, timestamp, seller_id
- Relationships: Category, User (seller)

## Responsive Design

- **Mobile (< 768px)**: Bottom navigation bar, single column layouts
- **Desktop (≥ 768px)**: Traditional top navigation, multi-column grids

## Color Palette

- Forest Green: `#2E7D32` (Primary actions, branding)
- Mint: `#A5D6A7` (Secondary elements, highlights)  
- Slate: `#37474F` (Text, UI elements)
- Light Mint: `#C8E6C9` (Backgrounds, subtle accents)

## Deployment

### Railway (PostgreSQL)

1. Set `DATABASE_URL` environment variable to your Railway PostgreSQL connection string
2. Deploy the application
3. Run database migrations

### Local Development

Uses SQLite database (`eco.db`) by default for easy local development.

## Future Enhancements

- User authentication and authorization
- Real-time messaging between buyers and sellers
- Payment processing integration
- Advanced search and filtering
- Product reviews and ratings
- Inventory management
- Shipping and logistics integration

## License

MIT License
