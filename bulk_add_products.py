from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import sys
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///new_inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define Product model (same as in app.py)
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    category = db.Column(db.String(50), default='Uncategorized')
    purchase_price = db.Column(db.Float, default=0)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    low_stock_threshold = db.Column(db.Integer, default=10)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    
    def is_low_stock(self):
        return self.stock <= self.low_stock_threshold
    
    def get_profit_margin(self):
        if self.purchase_price > 0:
            return ((self.price - self.purchase_price) / self.price) * 100
        return 100  # If purchase price is 0, profit margin is 100%

def add_or_update_product(name, stock, price=None, purchase_price=None, category="General"):
    """
    Add a new product or update an existing one.
    
    Args:
        name (str): Product name
        stock (int): Current stock quantity
        price (float, optional): Selling price
        purchase_price (float, optional): Purchase price
        category (str, optional): Product category
    
    Returns:
        tuple: (Product object, str status message)
    """
    # Check if product already exists
    existing_product = Product.query.filter_by(name=name).first()
    
    if existing_product:
        # Update existing product
        old_stock = existing_product.stock
        existing_product.stock = stock
        
        if price is not None:
            existing_product.price = price
            
        if purchase_price is not None:
            existing_product.purchase_price = purchase_price
            
        if category:
            existing_product.category = category
            
        db.session.commit()
        return existing_product, f"Updated product: {name} (Stock: {old_stock} → {stock})"
    else:
        # Create new product
        if price is None:
            # Default price if not provided
            price = 0
            
        new_product = Product(
            name=name,
            description=f"{name} description",
            category=category,
            purchase_price=purchase_price if purchase_price is not None else 0,
            price=price,
            stock=stock,
            low_stock_threshold=5  # Default low stock threshold
        )
        
        db.session.add(new_product)
        db.session.commit()
        return new_product, f"Added new product: {name} (Stock: {stock})"

def bulk_add_products(product_list):
    """
    Add multiple products from a list.
    
    Args:
        product_list (list): List of tuples (name, stock, price, purchase_price, category)
                            Price, purchase_price and category are optional
    
    Returns:
        list: Status messages for each product
    """
    results = []
    
    for product_data in product_list:
        # Handle different formats of input data
        if len(product_data) == 2:  # Only name and stock
            name, stock = product_data
            price = None
            purchase_price = None
            category = "General"
        elif len(product_data) == 3:  # Name, stock, and price
            name, stock, price = product_data
            purchase_price = None
            category = "General"
        elif len(product_data) == 4:  # Name, stock, price, and purchase_price
            name, stock, price, purchase_price = product_data
            category = "General"
        else:  # All fields
            name, stock, price, purchase_price, category = product_data
        
        _, message = add_or_update_product(name, stock, price, purchase_price, category)
        results.append(message)
    
    return results

def parse_product_line(line):
    """
    Parse a product line in the format: "1.Product Name:Quantity"
    
    Args:
        line (str): Line to parse
    
    Returns:
        tuple: (name, stock)
    """
    # Remove any leading/trailing whitespace
    line = line.strip()
    
    # Skip empty lines
    if not line:
        return None
    
    # Try to parse the line
    try:
        # Split at the colon to separate name and quantity
        if ':' in line:
            name_part, quantity_part = line.split(':', 1)
            
            # Remove any numbering at the beginning (e.g., "1.")
            if '.' in name_part:
                _, name = name_part.split('.', 1)
                name = name.strip()
            else:
                name = name_part.strip()
            
            # Convert quantity to integer
            stock = int(quantity_part.strip())
            
            return (name, stock)
        else:
            # If there's no colon, try to find the last space and assume it separates name and quantity
            parts = line.rsplit(' ', 1)
            if len(parts) == 2 and parts[1].isdigit():
                name = parts[0].strip()
                # Remove any numbering at the beginning
                if '.' in name:
                    _, name = name.split('.', 1)
                    name = name.strip()
                stock = int(parts[1])
                return (name, stock)
    except Exception as e:
        print(f"Error parsing line: {line} - {str(e)}")
    
    return None

def process_product_list(text):
    """
    Process a multi-line text of products.
    
    Args:
        text (str): Multi-line text with product information
    
    Returns:
        list: List of processed products
    """
    products = []
    lines = text.strip().split('\n')
    
    for line in lines:
        result = parse_product_line(line)
        if result:
            products.append(result)
    
    return products

def main():
    # Sample data - you can replace this with your actual data
    products_to_add = [
        ("Vimu", 4),
        ("liqiuid soap", 4),
        ("hand soap", 2),
        ("shampoo", 6),
        ("isabune Nini", 8),
        ("isabune ntoya", 12),
        ("Serviette", 15),
        ("cinthol soap", 4),
        ("everyday papier muswara", 4),
        ("jambo", 10),
        ("pad", 2),
        ("Colgate Nini", 3),
        ("colgate ntoya", 6),
        ("charcoal Colgate", 11),
        ("whitedent cavity", 6),
        ("white dent Nini", 6),
        ("Gilbey's Nini", 2),
        ("Gilbey's ntoya", 1),
        ("Konyagi Nini", 1),
        ("Konyagi half", 1),
        ("Konyagi ntoya", 2),
        ("Club", 1),
        ("Radiant", 3),
        ("Rackgin", 4),
        ("Be one", 2),
        ("United gin", 8),
        ("American", 1),
        ("ingwe gin", 5),
        ("Red waragi ngufi", 4),
        ("Bavaria", 2),
        ("cock", 10),
        ("Super towel pro", 2),
        ("Salama for 1L", 2),
        ("Salama for 2L", 6),
        ("Salama for 4L", 2),
        ("fanta Nini citron", 7),
        ("fanta Nini sprite", 4),
        ("fanta Nini coca", 1),
        ("amazi inyange Nini", 6),
        ("amazi mato y'inyange", 8),
        ("Nil Nini", 12),
        ("Flourish water", 2),
        ("Fanta nto (orange)", 11),
        ("Fanta pineapple", 10),
        ("Citron", 11),
        ("Sprite", 12),
        ("Vitalo", 12),
        ("Sana apple", 22),
        ("Sana mango", 19),
        ("Embe Nini", 12),
        ("Embe ntoya", 22),
        ("Malte", 12),
        ("Malte coffee", 9),
        ("Novida", 20),
        ("Merinda", 7),
        ("Twist tangawizi", 8),
        ("Twist zindi", 6),
        ("Afiya", 7),
        ("Portello", 8),
        ("Mo pineapple", 2),
        ("Energy", 9),
        ("Inyange juice apple", 5),
        ("Inyange juice mango", 12),
        ("Inyange juice for 2300", 10),
        ("Inyange milk for 2k", 2),
        ("Frosti juice", 2),
        ("Inyange milk for 1k", 10),
        ("Mukamira milk", 17),
        ("Inyange juice mango for 500", 23),
        ("Inyange juice apple", 18),
        ("Ketchup for 2k", 2),
        ("Ketchup for 1500", 1),
        ("Urusenda 1500", 3),
        ("Isukari", 10),
        ("American mayonnaise", 2),
        ("Jambo mayonnaise", 8),
        ("Citron mayonnaise", 3),
        ("Marie biscuits", 4),
        ("Nice Nini", 3),
        ("Nice ntoya", 6),
        ("Rio biscuits", 11),
        ("Milkstar", 4),
        ("Short cake", 3),
        ("Butter cookies", 6),
        ("Creamy", 3),
        ("Petit beure", 3),
        ("Big happy", 16),
        ("Bourbon", 20),
        ("Britannia", 28),
        ("Bombo for 100", 39),
        ("Bombo for 200", 42),
        ("Gorilossi", 21),
        ("Didoz", 16),
        ("Sunlight omoo for 1kg", 3),
        ("For half", 2),
        ("Oxi omo", 50),
        ("Ikibiriti", 5),
        ("Umuntu", 27),
        ("Red gold", 21),
        ("Amajyane (Rwahi tea)", 18),
        ("amajyane (Asante tea)", 14),
        ("Amakaroni manini", 10),
        ("amakaroni matoya", 20),
        ("intore", 5),
        ("Sm", 2),
        ("Dunhill", 2),
        ("Ph", 45),
        ("uburoso bwa 500", 5),
        ("uburoso bwa 300", 6),
        ("Mentors", 14),
        ("chocolate", 11),
        ("maggi", 39),
        ("0rbit", 34),
        ("imyeyo", 5),
        ("yoghurt", 2),
    ]

    with app.app_context():
        # Add all products
        results = bulk_add_products(products_to_add)
        
        # Print results
        for result in results:
            print(result)
        
        print(f"\nTotal products processed: {len(results)}")
        print(f"Total products in database: {Product.query.count()}")

if __name__ == "__main__":
    main()
