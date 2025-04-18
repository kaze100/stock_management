#!/usr/bin/env python
"""
Emergency Restore Script for Smart Inventory System
This script restores the app.py file to a known working state
"""
import os
import sys
import logging
import shutil
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("emergency_restore.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("emergency_restore")

def restore_app_py():
    """Restore app.py to a known working state"""
    logger.info("Restoring app.py to a known working state...")
    
    app_path = 'app.py'
    backup_path = f'app.py.emergency_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    
    try:
        # Create backup of current file
        if os.path.exists(app_path):
            shutil.copy2(app_path, backup_path)
            logger.info(f"Created backup: {backup_path}")
        
        # Write the known working version
        with open(app_path, 'w') as f:
            f.write(WORKING_APP_PY)
        
        logger.info("Successfully restored app.py")
        return True
    
    except Exception as e:
        logger.error(f"Error restoring app.py: {e}")
        return False

# Known working version of app.py
WORKING_APP_PY = '''from flask import Flask, render_template, redirect, url_for, flash, request, session, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///new_inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'locale'

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Initialize LoginManager
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Helper function for translations
def _(text, **variables):
    return text % variables if variables else text

# Try to initialize Babel with error handling
try:
    from flask_babel import Babel
    
    @app.route('/set_language/<language>')
    def set_language(language):
        session['language'] = language
        return redirect(request.referrer or url_for('index'))
    
    def get_locale():
        return session.get('language', 'en')
    
    # Initialize Babel with the locale selector
    babel = Babel(app, locale_selector=get_locale)
    
    # Import gettext after Babel is initialized
    from flask_babel import gettext as flask_gettext
    _ = flask_gettext
    
    @app.before_request
    def before_request():
        g._ = _
    
    has_babel = True
    logger.info("Flask-Babel initialized successfully")
    
except Exception as e:
    logger.warning(f"Flask-Babel initialization failed: {str(e)}")
    has_babel = False
    # Use the fallback translation function defined above

# Database models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'admin' or 'cashier'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

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

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product = db.relationship('Product', backref=db.backref('sales', lazy=True))
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    cashier_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    cashier = db.relationship('User', backref=db.backref('sales', lazy=True))
    date_sold = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    try:
        if current_user.is_authenticated:
            if current_user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('cashier_dashboard'))
        return redirect(url_for('login'))
    except Exception as e:
        logger.error(f"Error in index route: {str(e)}")
        flash(_('An error occurred. Please try again.'), 'danger')
        return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        # If user is already logged in, redirect to appropriate dashboard
        if current_user.is_authenticated:
            if current_user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('cashier_dashboard'))
        
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            user = User.query.filter_by(username=username).first()
            
            if user and user.check_password(password):
                login_user(user)
                
                if user.role == 'admin':
                    return redirect(url_for('admin_dashboard'))
                else:
                    return redirect(url_for('cashier_dashboard'))
            else:
                flash(_('Invalid username or password'), 'danger')
        
        return render_template('login.html')
    except Exception as e:
        logger.error(f"Error in login route: {str(e)}")
        flash(_('An error occurred. Please try again.'), 'danger')
        return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash(_('You have been logged out'), 'info')
    return redirect(url_for('login'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    try:
        if current_user.role != 'admin':
            flash(_('Access denied. Admin privileges required.'), 'danger')
            return redirect(url_for('index'))
        
        # Get total products
        total_products = Product.query.count()
        
        # Get low stock products
        low_stock_products = Product.query.filter(Product.stock <= Product.low_stock_threshold).all()
        
        # Get total sales
        total_sales = Sale.query.count()
        
        # Get total revenue
        total_revenue = db.session.query(db.func.sum(Sale.total_price)).scalar() or 0
        
        # Get sales for today
        today = datetime.utcnow().date()
        today_sales = Sale.query.filter(
            db.func.date(Sale.date_sold) == today
        ).all()
        
        today_revenue = sum(sale.total_price for sale in today_sales)
        
        # Get sales by category
        sales_by_category = {}
        for sale in Sale.query.all():
            category = sale.product.category
            if category not in sales_by_category:
                sales_by_category[category] = {
                    'count': 0,
                    'revenue': 0
                }
            sales_by_category[category]['count'] += sale.quantity
            sales_by_category[category]['revenue'] += sale.total_price
        
        # Calculate percentage for each category
        total_count = sum(data['count'] for data in sales_by_category.values())
        if total_count > 0:
            for category in sales_by_category:
                sales_by_category[category]['percentage'] = (sales_by_category[category]['count'] / total_count) * 100
        
        # Sort categories by count
        sorted_categories = sorted(
            sales_by_category.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )
        
        # Get top selling products
        top_products = db.session.query(
            Product,
            db.func.sum(Sale.quantity).label('total_quantity'),
            db.func.sum(Sale.total_price).label('total_revenue')
        ).join(Sale).group_by(Product.id).order_by(
            db.func.sum(Sale.quantity).desc()
        ).limit(5).all()
        
        return render_template(
            'admin_dashboard.html',
            total_products=total_products,
            low_stock_products=low_stock_products,
            total_sales=total_sales,
            total_revenue=total_revenue,
            today_sales=len(today_sales),
            today_revenue=today_revenue,
            sales_by_category=sorted_categories,
            top_products=top_products
        )
    except Exception as e:
        logger.error(f"Error in admin_dashboard route: {str(e)}")
        flash(_('An error occurred while loading the dashboard.'), 'danger')
        return redirect(url_for('index'))

@app.route('/admin/products')
@login_required
def manage_products():
    if current_user.role != 'admin':
        flash(_('Access denied. Admin privileges required.'), 'danger')
        return redirect(url_for('index'))
    
    products = Product.query.all()
    return render_template('manage_products.html', products=products)

@app.route('/admin/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if current_user.role != 'admin':
        flash(_('Access denied. Admin privileges required.'), 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        category = request.form.get('category')
        purchase_price = float(request.form.get('purchase_price'))
        price = float(request.form.get('price'))
        stock = int(request.form.get('stock'))
        low_stock_threshold = int(request.form.get('low_stock_threshold'))
        
        product = Product(
            name=name,
            description=description,
            category=category,
            purchase_price=purchase_price,
            price=price,
            stock=stock,
            low_stock_threshold=low_stock_threshold
        )
        
        db.session.add(product)
        db.session.commit()
        
        flash(_('Product added successfully!'), 'success')
        return redirect(url_for('manage_products'))
    
    return render_template('add_product.html')

@app.route('/admin/products/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    if current_user.role != 'admin':
        flash(_('Access denied. Admin privileges required.'), 'danger')
        return redirect(url_for('index'))
    
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.category = request.form.get('category')
        product.purchase_price = float(request.form.get('purchase_price'))
        product.price = float(request.form.get('price'))
        product.stock = int(request.form.get('stock'))
        product.low_stock_threshold = int(request.form.get('low_stock_threshold'))
        
        db.session.commit()
        
        flash(_('Product updated successfully!'), 'success')
        return redirect(url_for('manage_products'))
    
    return render_template('edit_product.html', product=product)

@app.route('/admin/products/delete/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    if current_user.role != 'admin':
        flash(_('Access denied. Admin privileges required.'), 'danger')
        return redirect(url_for('index'))
    
    product = Product.query.get_or_404(product_id)
    
    # Check if the product has any sales
    if Sale.query.filter_by(product_id=product_id).first():
        flash(_('Cannot delete product with sales records.'), 'danger')
        return redirect(url_for('manage_products'))
    
    db.session.delete(product)
    db.session.commit()
    
    flash(_('Product deleted successfully!'), 'success')
    return redirect(url_for('manage_products'))

@app.route('/admin/sales')
@login_required
def view_sales():
    try:
        if current_user.role != 'admin':
            flash(_('Access denied. Admin privileges required.'), 'danger')
            return redirect(url_for('index'))
        
        # Get filter parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        cashier_id = request.args.get('cashier_id')
        category = request.args.get('category')
        
        # Base query
        query = Sale.query
        
        # Apply filters
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(Sale.date_sold >= start_date)
        
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            # Add one day to include the end date
            end_date = datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59)
            query = query.filter(Sale.date_sold <= end_date)
        
        if cashier_id and cashier_id != 'all':
            query = query.filter(Sale.cashier_id == cashier_id)
        
        if category and category != 'all':
            query = query.join(Product).filter(Product.category == category)
        
        # Get sales with filters applied
        sales = query.order_by(Sale.date_sold.desc()).all()
        
        # Calculate total revenue
        total_revenue = sum(sale.total_price for sale in sales)
        
        # Get all cashiers for the filter dropdown
        cashiers = User.query.filter_by(role='cashier').all()
        
        # Get all categories for the filter dropdown
        categories = db.session.query(Product.category).distinct().all()
        categories = [category[0] for category in categories]
        
        return render_template(
            'view_sales.html',
            sales=sales,
            total_revenue=total_revenue,
            cashiers=cashiers,
            categories=categories,
            start_date=start_date,
            end_date=end_date,
            selected_cashier_id=cashier_id,
            selected_category=category
        )
    except Exception as e:
        logger.error(f"Error in view_sales route: {str(e)}")
        flash(_('An error occurred while loading sales data.'), 'danger')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/sales/delete/<int:sale_id>', methods=['POST'])
@login_required
def delete_sale(sale_id):
    try:
        if current_user.role != 'admin':
            flash(_('Access denied. Admin privileges required.'), 'danger')
            return redirect(url_for('index'))
        
        sale = Sale.query.get_or_404(sale_id)
        
        # Return the product to inventory
        product = Product.query.get(sale.product_id)
        if product:
            product.stock += sale.quantity
        
        db.session.delete(sale)
        db.session.commit()
        
        flash(_('Sale deleted and product returned to inventory.'), 'success')
        return redirect(url_for('view_sales'))
    except Exception as e:
        logger.error(f"Error in delete_sale route: {str(e)}")
        flash(_('An error occurred while deleting the sale.'), 'danger')
        return redirect(url_for('view_sales'))

@app.route('/cashier/dashboard')
@login_required
def cashier_dashboard():
    try:
        if current_user.role != 'cashier':
            flash(_('Access denied. Cashier privileges required.'), 'danger')
            return redirect(url_for('index'))
        
        # Get search query
        search_query = request.args.get('search', '')
        
        # Get products with stock > 0
        if search_query:
            products = Product.query.filter(
                Product.stock > 0,
                Product.name.ilike(f'%{search_query}%')
            ).all()
        else:
            products = Product.query.filter(Product.stock > 0).all()
        
        # Get today's sales for this cashier
        today = datetime.utcnow().date()
        today_sales = Sale.query.filter(
            Sale.cashier_id == current_user.id,
            db.func.date(Sale.date_sold) == today
        ).order_by(Sale.date_sold.desc()).all()
        
        # Calculate total revenue for today
        total_revenue = sum(sale.total_price for sale in today_sales)
        
        return render_template(
            'cashier_dashboard.html',
            products=products,
            today_sales=today_sales,
            total_revenue=total_revenue,
            search_query=search_query
        )
    except Exception as e:
        logger.error(f"Error in cashier_dashboard route: {str(e)}")
        flash(_('An error occurred while loading the dashboard.'), 'danger')
        return redirect(url_for('index'))

@app.route('/cashier/sell', methods=['GET', 'POST'])
@login_required
def sell_product():
    if current_user.role != 'cashier':
        flash(_('Access denied. Cashier privileges required.'), 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        quantity = int(request.form.get('quantity'))
        
        product = Product.query.get_or_404(product_id)
        
        # Check if enough stock is available
        if product.stock < quantity:
            flash(_('Not enough stock available. Only {0} units left.', product.stock), 'danger')
            return redirect(url_for('cashier_dashboard'))
        
        # Calculate total price
        total_price = product.price * quantity
        
        # Create sale record
        sale = Sale(
            product_id=product_id,
            quantity=quantity,
            total_price=total_price,
            cashier_id=current_user.id
        )
        
        # Update product stock
        product.stock -= quantity
        
        db.session.add(sale)
        db.session.commit()
        
        flash(_('Sale recorded successfully!'), 'success')
        return redirect(url_for('cashier_dashboard'))
    
    # If GET request, redirect to cashier dashboard
    return redirect(url_for('cashier_dashboard'))

@app.route('/cashier/sales')
@login_required
def view_cashier_sales():
    try:
        if current_user.role != 'cashier':
            flash(_('Access denied. Cashier privileges required.'), 'danger')
            return redirect(url_for('index'))
        
        # Get filter parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        category = request.args.get('category')
        
        # Base query - only show this cashier's sales
        query = Sale.query.filter(Sale.cashier_id == current_user.id)
        
        # Apply filters
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(Sale.date_sold >= start_date)
        
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            # Add one day to include the end date
            end_date = datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59)
            query = query.filter(Sale.date_sold <= end_date)
        
        if category and category != 'all':
            query = query.join(Product).filter(Product.category == category)
        
        # Get sales with filters applied
        sales = query.order_by(Sale.date_sold.desc()).all()
        
        # Calculate total revenue
        total_revenue = sum(sale.total_price for sale in sales)
        
        # Get all categories for the filter dropdown
        categories = db.session.query(Product.category).distinct().all()
        categories = [category[0] for category in categories]
        
        return render_template(
            'view_cashier_sales.html',
            sales=sales,
            total_revenue=total_revenue,
            categories=categories,
            start_date=start_date,
            end_date=end_date,
            selected_category=category
        )
    except Exception as e:
        logger.error(f"Error in view_cashier_sales route: {str(e)}")
        flash(_('An error occurred while loading sales data.'), 'danger')
        return redirect(url_for('cashier_dashboard'))

# Initialize the database and create admin and cashier users if they don't exist.
def init_db_command():
    """Initialize the database and create admin and cashier users if they don't exist."""
    with app.app_context():
        db.create_all()
        
        # Check if admin user exists
        admin = User.query.filter_by(username='renoir01').first()
        if not admin:
            admin = User(username='renoir01', role='admin')
            admin.set_password('Renoir@654')
            db.session.add(admin)
            print('Admin user created.')
        
        # Check if cashier user exists
        cashier = User.query.filter_by(username='epi').first()
        if not cashier:
            cashier = User(username='epi', role='cashier')
            cashier.set_password('Epi@654')
            db.session.add(cashier)
            print('Cashier user created.')
        
        db.session.commit()
        print('Database initialized.')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
'''

if __name__ == "__main__":
    print("Running emergency restore for Smart Inventory System...")
    
    if restore_app_py():
        print("\nEmergency restore completed successfully!")
        print("\nInstructions:")
        print("1. Reload your web app from the PythonAnywhere Web tab")
        print("2. Your system should now be working again with all your existing data")
        print("3. The packaged products feature has been temporarily removed to restore functionality")
    else:
        print("\nEmergency restore failed. Please check the logs for details.")
