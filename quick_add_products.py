from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import os
import sys
from datetime import datetime
import csv
import io

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'quick-add-products-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///new_inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Internationalization support
try:
    from flask_babel import Babel, gettext as _

    def get_locale():
        return session.get('language', 'en')

    babel = Babel(app, locale_selector=get_locale)

    @app.route('/set_language/<language>')
    def set_language(language):
        session['language'] = language
        return redirect(request.referrer or url_for('index'))

except ImportError:
    # Fallback translation function if Flask-Babel is not available
    def _(text, **variables):
        return text % variables if variables else text

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

# Translation dictionary for categories (English to Kinyarwanda)
category_translations = {
    'General': 'Rusange',
    'Beverages': 'Ibinyobwa',
    'Snacks': 'Utunyobwa',
    'Hygiene': 'Isuku',
    'Groceries': 'Ibiribwa',
    'Alcohol': 'Inzoga',
    'Tobacco': 'Itabi',
    'Dairy': 'Amata',
    'Cleaning': 'Isukura'
}

def get_category_translation(category, language='en'):
    """Get category translation based on language"""
    if language == 'rw' and category in category_translations:
        return category_translations[category]
    return category

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
        tuple: (Product object, str status message, bool is_new)
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
        return existing_product, f"Updated: {name} (Stock: {old_stock} → {stock})", False
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
        return new_product, f"Added: {name} (Stock: {stock})", True

def get_default_category(product_name):
    """Determine a default category based on the product name"""
    product_name = product_name.lower()
    
    if any(term in product_name for term in ['soap', 'isabune', 'shampoo', 'colgate', 'whitedent', 'omo', 'sunlight']):
        return "Hygiene"
    elif any(term in product_name for term in ['fanta', 'sprite', 'coca', 'sana', 'juice', 'novida', 'merinda', 'twist', 'energy', 'vitalo']):
        return "Beverages"
    elif any(term in product_name for term in ['milk', 'yoghurt']):
        return "Dairy"
    elif any(term in product_name for term in ['gilbey', 'konyagi', 'club', 'gin', 'waragi', 'bavaria']):
        return "Alcohol"
    elif any(term in product_name for term in ['biscuit', 'cookies', 'nice', 'marie', 'bourbon', 'britannia']):
        return "Snacks"
    elif any(term in product_name for term in ['mayonnaise', 'ketchup', 'maggi']):
        return "Groceries"
    elif any(term in product_name for term in ['tea', 'amajyane']):
        return "Beverages"
    elif any(term in product_name for term in ['amakaroni', 'isukari']):
        return "Groceries"
    elif any(term in product_name for term in ['dunhill', 'sm', 'intore']):
        return "Tobacco"
    elif any(term in product_name for term in ['pad', 'serviette', 'papier']):
        return "Hygiene"
    
    return "General"

def parse_product_line(line):
    """Parse a product line in various formats"""
    line = line.strip()
    if not line:
        return None
    
    try:
        # Handle format: "1.Product Name:Quantity"
        if ':' in line:
            name_part, quantity_part = line.split(':', 1)
            
            # Remove numbering if present
            if '.' in name_part:
                parts = name_part.split('.', 1)
                if parts[0].strip().isdigit():
                    name = parts[1].strip()
                else:
                    name = name_part.strip()
            else:
                name = name_part.strip()
            
            # Extract first number from quantity part
            import re
            quantity_match = re.search(r'\d+', quantity_part)
            if quantity_match:
                stock = int(quantity_match.group())
                return (name, stock)
        
        # Handle format with number at the end: "Product Name 10"
        else:
            import re
            match = re.search(r'(.*?)(\d+)$', line)
            if match:
                name = match.group(1).strip()
                stock = int(match.group(2))
                return (name, stock)
            
            # Handle format with numbering: "1. Product Name 10"
            match = re.search(r'\d+\.\s*(.*?)(\d+)$', line)
            if match:
                name = match.group(1).strip()
                stock = int(match.group(2))
                return (name, stock)
    
    except Exception as e:
        print(f"Error parsing line: {line} - {str(e)}")
    
    return None

# Routes
@app.route('/')
def index():
    """Main page for quick add products"""
    products = Product.query.order_by(Product.category, Product.name).all()
    categories = db.session.query(Product.category).distinct().all()
    categories = [cat[0] for cat in categories]
    
    # Get language
    language = session.get('language', 'en')
    
    # Translate categories
    translated_categories = [(cat, get_category_translation(cat, language)) for cat in categories]
    
    return render_template(
        'quick_add.html',
        products=products,
        categories=translated_categories,
        current_language=language
    )

@app.route('/add', methods=['POST'])
def add_product():
    """Add a single product"""
    name = request.form.get('name')
    stock = int(request.form.get('stock', 0))
    price = float(request.form.get('price', 0))
    purchase_price = float(request.form.get('purchase_price', 0))
    category = request.form.get('category', 'General')
    
    _, message, is_new = add_or_update_product(name, stock, price, purchase_price, category)
    
    if is_new:
        flash(_('Product added successfully!'), 'success')
    else:
        flash(_('Product updated successfully!'), 'info')
    
    return redirect(url_for('index'))

@app.route('/bulk_add', methods=['POST'])
def bulk_add():
    """Process bulk text input"""
    bulk_text = request.form.get('bulk_text', '')
    
    products_data = []
    for line in bulk_text.split('\n'):
        result = parse_product_line(line)
        if result:
            products_data.append(result)
    
    added = 0
    updated = 0
    
    for name, stock in products_data:
        _, _, is_new = add_or_update_product(
            name=name,
            stock=stock,
            category=get_default_category(name)
        )
        if is_new:
            added += 1
        else:
            updated += 1
    
    if added > 0:
        flash(_('Added %(count)d new products!', count=added), 'success')
    if updated > 0:
        flash(_('Updated %(count)d existing products!', count=updated), 'info')
    
    return redirect(url_for('index'))

@app.route('/import_csv', methods=['POST'])
def import_csv():
    """Import products from CSV file"""
    if 'csv_file' not in request.files:
        flash(_('No file selected'), 'danger')
        return redirect(url_for('index'))
    
    file = request.files['csv_file']
    if file.filename == '':
        flash(_('No file selected'), 'danger')
        return redirect(url_for('index'))
    
    # Process CSV file
    stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
    csv_reader = csv.reader(stream)
    
    added = 0
    updated = 0
    
    for row in csv_reader:
        if len(row) >= 2:
            name = row[0].strip()
            try:
                stock = int(row[1])
                price = float(row[2]) if len(row) > 2 and row[2] else None
                purchase_price = float(row[3]) if len(row) > 3 and row[3] else None
                category = row[4] if len(row) > 4 and row[4] else get_default_category(name)
                
                _, _, is_new = add_or_update_product(name, stock, price, purchase_price, category)
                if is_new:
                    added += 1
                else:
                    updated += 1
            except (ValueError, IndexError):
                continue
    
    if added > 0:
        flash(_('Added %(count)d new products from CSV!', count=added), 'success')
    if updated > 0:
        flash(_('Updated %(count)d existing products from CSV!', count=updated), 'info')
    
    return redirect(url_for('index'))

@app.route('/update_price/<int:product_id>', methods=['POST'])
def update_price(product_id):
    """Update price for a product"""
    product = Product.query.get_or_404(product_id)
    
    try:
        price = float(request.form.get('price', 0))
        purchase_price = float(request.form.get('purchase_price', 0))
        
        product.price = price
        product.purchase_price = purchase_price
        db.session.commit()
        
        flash(_('Price updated for %(name)s', name=product.name), 'success')
    except ValueError:
        flash(_('Invalid price value'), 'danger')
    
    return redirect(url_for('index'))

@app.route('/update_stock/<int:product_id>', methods=['POST'])
def update_stock(product_id):
    """Update stock for a product"""
    product = Product.query.get_or_404(product_id)
    
    try:
        stock = int(request.form.get('stock', 0))
        
        product.stock = stock
        db.session.commit()
        
        flash(_('Stock updated for %(name)s', name=product.name), 'success')
    except ValueError:
        flash(_('Invalid stock value'), 'danger')
    
    return redirect(url_for('index'))

# Create templates directory if it doesn't exist
templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
if not os.path.exists(templates_dir):
    os.makedirs(templates_dir)

def create_template():
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'quick_add.html')
    
    if not os.path.exists(template_path):
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write('''
<!DOCTYPE html>
<html lang="{{ session.get('language', 'en') }}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ _('Quick Add Products') }}</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <style>
        body {
            padding-top: 20px;
            padding-bottom: 20px;
        }
        .product-card {
            margin-bottom: 15px;
        }
        .low-stock {
            background-color: #fff3cd;
        }
        .language-selector {
            margin-bottom: 20px;
        }
        .tab-content {
            padding-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="row mb-4">
            <div class="col-md-6">
                <h1>{{ _('Quick Add Products') }}</h1>
            </div>
            <div class="col-md-6 text-end">
                <div class="language-selector">
                    <a href="{{ url_for('set_language', language='en') }}" class="btn btn-sm {{ 'btn-primary' if current_language == 'en' else 'btn-outline-primary' }}">English</a>
                    <a href="{{ url_for('set_language', language='rw') }}" class="btn btn-sm {{ 'btn-primary' if current_language == 'rw' else 'btn-outline-primary' }}">Kinyarwanda</a>
                </div>
            </div>
        </div>

        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        <ul class="nav nav-tabs" id="myTab" role="tablist">
            <li class="nav-item" role="presentation">
                <button class="nav-link active" id="products-tab" data-bs-toggle="tab" data-bs-target="#products" type="button" role="tab" aria-controls="products" aria-selected="true">{{ _('Products') }}</button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="add-tab" data-bs-toggle="tab" data-bs-target="#add" type="button" role="tab" aria-controls="add" aria-selected="false">{{ _('Add Product') }}</button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="bulk-tab" data-bs-toggle="tab" data-bs-target="#bulk" type="button" role="tab" aria-controls="bulk" aria-selected="false">{{ _('Bulk Add') }}</button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="import-tab" data-bs-toggle="tab" data-bs-target="#import" type="button" role="tab" aria-controls="import" aria-selected="false">{{ _('Import CSV') }}</button>
            </li>
        </ul>

        <div class="tab-content" id="myTabContent">
            <!-- Products Tab -->
            <div class="tab-pane fade show active" id="products" role="tabpanel" aria-labelledby="products-tab">
                <div class="row mb-3">
                    <div class="col-md-6">
                        <input type="text" id="productSearch" class="form-control" placeholder="{{ _('Search products...') }}">
                    </div>
                    <div class="col-md-6">
                        <select id="categoryFilter" class="form-select">
                            <option value="">{{ _('All Categories') }}</option>
                            {% for cat, trans_cat in categories %}
                                <option value="{{ cat }}">{{ trans_cat }}</option>
                            {% endfor %}
                        </select>
                    </div>
                </div>

                <div class="table-responsive">
                    <table class="table table-striped table-hover">
                        <thead>
                            <tr>
                                <th>{{ _('Name') }}</th>
                                <th>{{ _('Category') }}</th>
                                <th>{{ _('Stock') }}</th>
                                <th>{{ _('Price (RWF)') }}</th>
                                <th>{{ _('Purchase Price') }}</th>
                                <th>{{ _('Actions') }}</th>
                            </tr>
                        </thead>
                        <tbody id="productTableBody">
                            {% for product in products %}
                                <tr class="product-row {{ 'low-stock' if product.stock <= product.low_stock_threshold }}" data-category="{{ product.category }}">
                                    <td>{{ product.name }}</td>
                                    <td>{{ get_category_translation(product.category, session.get('language', 'en')) }}</td>
                                    <td>
                                        <form action="{{ url_for('update_stock', product_id=product.id) }}" method="post" class="d-flex">
                                            <input type="number" name="stock" value="{{ product.stock }}" class="form-control form-control-sm" style="width: 70px;">
                                            <button type="submit" class="btn btn-sm btn-outline-primary ms-1">{{ _('Update') }}</button>
                                        </form>
                                    </td>
                                    <td>
                                        <form action="{{ url_for('update_price', product_id=product.id) }}" method="post" class="d-flex">
                                            <input type="number" name="price" value="{{ product.price }}" class="form-control form-control-sm" style="width: 80px;">
                                            <button type="submit" class="btn btn-sm btn-outline-primary ms-1">{{ _('Update') }}</button>
                                        </form>
                                    </td>
                                    <td>
                                        <form action="{{ url_for('update_price', product_id=product.id) }}" method="post" class="d-flex">
                                            <input type="number" name="purchase_price" value="{{ product.purchase_price }}" class="form-control form-control-sm" style="width: 80px;">
                                            <input type="hidden" name="price" value="{{ product.price }}">
                                            <button type="submit" class="btn btn-sm btn-outline-primary ms-1">{{ _('Update') }}</button>
                                        </form>
                                    </td>
                                    <td>
                                        <a href="{{ url_for('index') }}" class="btn btn-sm btn-outline-info">{{ _('Details') }}</a>
                                    </td>
                                </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Add Product Tab -->
            <div class="tab-pane fade" id="add" role="tabpanel" aria-labelledby="add-tab">
                <div class="card">
                    <div class="card-header">
                        <h5>{{ _('Add New Product') }}</h5>
                    </div>
                    <div class="card-body">
                        <form action="{{ url_for('add_product') }}" method="post">
                            <div class="mb-3">
                                <label for="name" class="form-label">{{ _('Product Name') }}</label>
                                <input type="text" class="form-control" id="name" name="name" required>
                            </div>
                            <div class="mb-3">
                                <label for="category" class="form-label">{{ _('Category') }}</label>
                                <select class="form-select" id="category" name="category">
                                    {% for cat, trans_cat in categories %}
                                        <option value="{{ cat }}">{{ trans_cat }}</option>
                                    {% endfor %}
                                    <option value="General">{{ _('General') }}</option>
                                </select>
                            </div>
                            <div class="row">
                                <div class="col-md-4 mb-3">
                                    <label for="stock" class="form-label">{{ _('Stock Quantity') }}</label>
                                    <input type="number" class="form-control" id="stock" name="stock" value="0" min="0" required>
                                </div>
                                <div class="col-md-4 mb-3">
                                    <label for="price" class="form-label">{{ _('Selling Price (RWF)') }}</label>
                                    <input type="number" class="form-control" id="price" name="price" value="0" min="0" step="0.01" required>
                                </div>
                                <div class="col-md-4 mb-3">
                                    <label for="purchase_price" class="form-label">{{ _('Purchase Price (RWF)') }}</label>
                                    <input type="number" class="form-control" id="purchase_price" name="purchase_price" value="0" min="0" step="0.01">
                                </div>
                            </div>
                            <button type="submit" class="btn btn-primary">{{ _('Add Product') }}</button>
                        </form>
                    </div>
                </div>
            </div>

            <!-- Bulk Add Tab -->
            <div class="tab-pane fade" id="bulk" role="tabpanel" aria-labelledby="bulk-tab">
                <div class="card">
                    <div class="card-header">
                        <h5>{{ _('Bulk Add Products') }}</h5>
                    </div>
                    <div class="card-body">
                        <form action="{{ url_for('bulk_add') }}" method="post">
                            <div class="mb-3">
                                <label for="bulk_text" class="form-label">{{ _('Enter Products (one per line)') }}</label>
                                <p class="text-muted">{{ _('Format: "Product Name:Quantity" or "Product Name Quantity"') }}</p>
                                <textarea class="form-control" id="bulk_text" name="bulk_text" rows="10" required></textarea>
                            </div>
                            <button type="submit" class="btn btn-primary">{{ _('Process Bulk Products') }}</button>
                        </form>
                    </div>
                </div>
            </div>

            <!-- Import CSV Tab -->
            <div class="tab-pane fade" id="import" role="tabpanel" aria-labelledby="import-tab">
                <div class="card">
                    <div class="card-header">
                        <h5>{{ _('Import from CSV') }}</h5>
                    </div>
                    <div class="card-body">
                        <form action="{{ url_for('import_csv') }}" method="post" enctype="multipart/form-data">
                            <div class="mb-3">
                                <label for="csv_file" class="form-label">{{ _('Select CSV File') }}</label>
                                <p class="text-muted">{{ _('CSV Format: Name,Stock,Price,PurchasePrice,Category') }}</p>
                                <input type="file" class="form-control" id="csv_file" name="csv_file" accept=".csv" required>
                            </div>
                            <button type="submit" class="btn btn-primary">{{ _('Import Products') }}</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Product search functionality
        document.getElementById('productSearch').addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const rows = document.querySelectorAll('#productTableBody .product-row');
            
            rows.forEach(row => {
                const name = row.querySelector('td:first-child').textContent.toLowerCase();
                if (name.includes(searchTerm)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
        
        // Category filter functionality
        document.getElementById('categoryFilter').addEventListener('change', function() {
            const category = this.value;
            const rows = document.querySelectorAll('#productTableBody .product-row');
            
            rows.forEach(row => {
                if (!category || row.dataset.category === category) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    </script>
</body>
</html>
            ''')

if __name__ == '__main__':
    with app.app_context():
        create_template()
        app.run(debug=True, port=5001)
