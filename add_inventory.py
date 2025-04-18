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
            description=f"{name}",
            category=category,
            purchase_price=purchase_price if purchase_price is not None else 0,
            price=price,
            stock=stock,
            low_stock_threshold=5  # Default low stock threshold
        )
        
        db.session.add(new_product)
        db.session.commit()
        return new_product, f"Added new product: {name} (Stock: {stock})"

def interactive_add_products():
    """Interactive mode to add products one by one"""
    print("\n=== Interactive Product Entry ===")
    print("Enter product details (leave empty to finish):")
    
    products_added = 0
    
    while True:
        name = input("\nProduct name (or press Enter to finish): ")
        if not name:
            break
            
        # Check if product exists
        existing = Product.query.filter_by(name=name).first()
        if existing:
            print(f"Product '{name}' already exists with stock: {existing.stock}, price: {existing.price}")
            update = input("Update this product? (y/n): ").lower()
            if update != 'y':
                continue
        
        # Get stock
        while True:
            stock_input = input("Stock quantity: ")
            try:
                stock = int(stock_input)
                break
            except ValueError:
                print("Please enter a valid number for stock")
        
        # Get price
        while True:
            price_input = input("Selling price (RWF): ")
            if not price_input:
                price = None
                break
            try:
                price = float(price_input)
                break
            except ValueError:
                print("Please enter a valid number for price")
        
        # Get purchase price
        while True:
            purchase_input = input("Purchase price (RWF, optional): ")
            if not purchase_input:
                purchase_price = None
                break
            try:
                purchase_price = float(purchase_input)
                break
            except ValueError:
                print("Please enter a valid number for purchase price")
        
        # Get category
        category = input("Category (optional, press Enter for 'General'): ")
        if not category:
            category = "General"
        
        # Add or update the product
        _, message = add_or_update_product(name, stock, price, purchase_price, category)
        print(message)
        products_added += 1
    
    print(f"\nTotal products added/updated: {products_added}")
    return products_added

def process_bulk_text():
    """Process a bulk text input of products"""
    print("\n=== Bulk Product Entry ===")
    print("Enter your product list in the format:")
    print("1. Product Name: Quantity")
    print("(Enter an empty line when finished)")
    
    lines = []
    print("\nEnter products (empty line to finish):")
    while True:
        line = input()
        if not line:
            break
        lines.append(line)
    
    product_text = "\n".join(lines)
    products = []
    
    # Process each line
    for line in product_text.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        # Try to parse the line
        try:
            # Remove numbering if present
            if '.' in line:
                parts = line.split('.', 1)
                if parts[0].strip().isdigit():
                    line = parts[1].strip()
            
            # Split name and quantity
            if ':' in line:
                name_part, quantity_part = line.split(':', 1)
                name = name_part.strip()
                
                # Handle quantity with additional text
                quantity_text = quantity_part.strip()
                # Extract first number from the quantity text
                import re
                quantity_match = re.search(r'\d+', quantity_text)
                if quantity_match:
                    stock = int(quantity_match.group())
                    products.append((name, stock))
            else:
                # Try to find the last number in the line
                import re
                match = re.search(r'(.*?)(\d+)$', line)
                if match:
                    name = match.group(1).strip()
                    stock = int(match.group(2))
                    products.append((name, stock))
        except Exception as e:
            print(f"Error parsing line: {line} - {str(e)}")
    
    # Now ask for prices
    print("\n=== Enter Prices for Products ===")
    results = []
    
    for name, stock in products:
        # Check if product exists
        existing = Product.query.filter_by(name=name).first()
        if existing:
            print(f"\nProduct '{name}' already exists with stock: {existing.stock}, price: {existing.price}")
            update = input(f"Update {name}? (y/n): ").lower()
            if update != 'y':
                continue
                
            # Get new price or use existing
            price_input = input(f"Selling price for {name} (RWF, press Enter to keep {existing.price}): ")
            if price_input:
                try:
                    price = float(price_input)
                except ValueError:
                    print("Invalid price, keeping existing price")
                    price = existing.price
            else:
                price = existing.price
                
            # Get new purchase price or use existing
            purchase_input = input(f"Purchase price (RWF, press Enter to keep {existing.purchase_price}): ")
            if purchase_input:
                try:
                    purchase_price = float(purchase_input)
                except ValueError:
                    print("Invalid purchase price, keeping existing purchase price")
                    purchase_price = existing.purchase_price
            else:
                purchase_price = existing.purchase_price
        else:
            print(f"\nNew product: {name}")
            # Get price
            while True:
                price_input = input(f"Selling price for {name} (RWF): ")
                if not price_input:
                    price = 0
                    break
                try:
                    price = float(price_input)
                    break
                except ValueError:
                    print("Please enter a valid number for price")
            
            # Get purchase price
            while True:
                purchase_input = input(f"Purchase price for {name} (RWF, optional): ")
                if not purchase_input:
                    purchase_price = 0
                    break
                try:
                    purchase_price = float(purchase_input)
                    break
                except ValueError:
                    print("Please enter a valid number for purchase price")
        
        # Get category
        category = input(f"Category for {name} (optional, press Enter for 'General'): ")
        if not category:
            category = "General"
        
        # Add or update the product
        _, message = add_or_update_product(name, stock, price, purchase_price, category)
        results.append(message)
        print(message)
    
    print(f"\nTotal products processed: {len(results)}")
    return len(results)

def add_predefined_products():
    """Add the predefined list of products from the user's request"""
    products = [
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
    
    print("\n=== Adding Predefined Products ===")
    print("This will add all products from your list.")
    print("For each product, you'll be asked to enter the price.")
    
    results = []
    for name, stock in products:
        # Check if product exists
        existing = Product.query.filter_by(name=name).first()
        if existing:
            print(f"\nProduct '{name}' already exists with stock: {existing.stock}, price: {existing.price}")
            update = input(f"Update {name}? (y/n): ").lower()
            if update != 'y':
                continue
                
            # Get new price or use existing
            price_input = input(f"Selling price for {name} (RWF, press Enter to keep {existing.price}): ")
            if price_input:
                try:
                    price = float(price_input)
                except ValueError:
                    print("Invalid price, keeping existing price")
                    price = existing.price
            else:
                price = existing.price
                
            # Get new purchase price or use existing
            purchase_input = input(f"Purchase price (RWF, press Enter to keep {existing.purchase_price}): ")
            if purchase_input:
                try:
                    purchase_price = float(purchase_input)
                except ValueError:
                    print("Invalid purchase price, keeping existing purchase price")
                    purchase_price = existing.purchase_price
            else:
                purchase_price = existing.purchase_price
        else:
            print(f"\nNew product: {name}")
            # Get price
            while True:
                price_input = input(f"Selling price for {name} (RWF): ")
                if not price_input:
                    price = 0
                    break
                try:
                    price = float(price_input)
                    break
                except ValueError:
                    print("Please enter a valid number for price")
            
            # Get purchase price
            while True:
                purchase_input = input(f"Purchase price for {name} (RWF, optional): ")
                if not purchase_input:
                    purchase_price = 0
                    break
                try:
                    purchase_price = float(purchase_input)
                    break
                except ValueError:
                    print("Please enter a valid number for purchase price")
        
        # Get category (with default categories based on product name)
        default_category = get_default_category(name)
        category = input(f"Category for {name} (press Enter for '{default_category}'): ")
        if not category:
            category = default_category
        
        # Add or update the product
        _, message = add_or_update_product(name, stock, price, purchase_price, category)
        results.append(message)
        print(message)
    
    print(f"\nTotal products processed: {len(results)}")
    return len(results)

def get_default_category(product_name):
    """Determine a default category based on the product name"""
    product_name = product_name.lower()
    
    if any(term in product_name for term in ['soap', 'isabune', 'shampoo', 'colgate', 'whitedent', 'omo', 'sunlight']):
        return "Hygiene & Cleaning"
    elif any(term in product_name for term in ['fanta', 'sprite', 'coca', 'sana', 'juice', 'novida', 'merinda', 'twist', 'energy', 'vitalo']):
        return "Beverages - Soft Drinks"
    elif any(term in product_name for term in ['milk', 'yoghurt']):
        return "Dairy"
    elif any(term in product_name for term in ['gilbey', 'konyagi', 'club', 'gin', 'waragi', 'bavaria']):
        return "Beverages - Alcohol"
    elif any(term in product_name for term in ['biscuit', 'cookies', 'nice', 'marie', 'bourbon', 'britannia']):
        return "Snacks & Biscuits"
    elif any(term in product_name for term in ['mayonnaise', 'ketchup', 'maggi']):
        return "Condiments"
    elif any(term in product_name for term in ['tea', 'amajyane']):
        return "Tea & Coffee"
    elif any(term in product_name for term in ['amakaroni', 'isukari']):
        return "Groceries"
    elif any(term in product_name for term in ['dunhill', 'sm', 'intore']):
        return "Tobacco"
    elif any(term in product_name for term in ['pad', 'serviette', 'papier']):
        return "Personal Care"
    
    return "General"

def main():
    with app.app_context():
        print("\n===== SmartInventory Product Manager =====")
        print("This tool helps you add products to your inventory")
        print("It will check for duplicates and update stock if needed")
        
        while True:
            print("\nChoose an option:")
            print("1. Add products one by one (interactive)")
            print("2. Add products from bulk text")
            print("3. Add products from your predefined list")
            print("4. View all products")
            print("5. Exit")
            
            choice = input("\nEnter your choice (1-5): ")
            
            if choice == '1':
                interactive_add_products()
            elif choice == '2':
                process_bulk_text()
            elif choice == '3':
                add_predefined_products()
            elif choice == '4':
                # View all products
                products = Product.query.all()
                if not products:
                    print("\nNo products in the database.")
                else:
                    print("\n===== All Products =====")
                    print(f"{'ID':<5} {'Name':<30} {'Stock':<8} {'Price':<10} {'Category':<20}")
                    print("-" * 75)
                    for p in products:
                        print(f"{p.id:<5} {p.name[:30]:<30} {p.stock:<8} {p.price:<10.2f} {p.category[:20]:<20}")
                    print(f"\nTotal products: {len(products)}")
            elif choice == '5':
                print("\nExiting program. Your products have been saved.")
                break
            else:
                print("\nInvalid choice. Please try again.")

if __name__ == "__main__":
    main()
