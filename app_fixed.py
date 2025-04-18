from flask import Flask, render_template, redirect, url_for, flash, request, session, g
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
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/inventory.db'
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
class User(db.Model):
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
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('cashier_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash(_('Invalid username or password'), 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash(_('You have been logged out.'), 'info')
    return redirect(url_for('login'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash(_('Access denied. Admin privileges required.'), 'danger')
        return redirect(url_for('index'))
    
    # Get today's date
    today = datetime.now().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())
    
    # Get counts
    total_products = Product.query.count()
    low_stock_products = Product.query.filter(Product.stock <= Product.low_stock_threshold).count()
    out_of_stock_products = Product.query.filter(Product.stock == 0).count()
    
    # Get today's sales
    today_sales = Sale.query.filter(Sale.date_sold.between(today_start, today_end)).all()
    today_sales_count = len(today_sales)
    total_revenue = sum(sale.total_price for sale in today_sales)
    total_profit = sum((sale.total_price - (sale.product.purchase_price * sale.quantity)) for sale in today_sales)
    
    # Get recent sales
    recent_sales = Sale.query.order_by(Sale.date_sold.desc()).limit(5).all()
    
    # Get low stock products
    low_stock_items = Product.query.filter(
        Product.stock <= Product.low_stock_threshold,
        Product.stock > 0
    ).all()
    
    return render_template('admin_dashboard.html', 
                           total_products=total_products,
                           low_stock_products=low_stock_products,
                           out_of_stock_products=out_of_stock_products,
                           today_sales_count=today_sales_count,
                           total_revenue=total_revenue,
                           total_profit=total_profit,
                           recent_sales=recent_sales,
                           low_stock_items=low_stock_items)

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
        purchase_price = float(request.form.get('purchase_price', 0))
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
        product.purchase_price = float(request.form.get('purchase_price', 0))
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
    
    # Check if product has associated sales
    if Sale.query.filter_by(product_id=product_id).first():
        flash(_('Cannot delete product "{0}" because it has associated sales records. Consider updating the product instead.', product.name), 'danger')
        return redirect(url_for('manage_products'))
    
    db.session.delete(product)
    db.session.commit()
    
    flash(_('Product deleted successfully!'), 'success')
    return redirect(url_for('manage_products'))

@app.route('/admin/sales')
@login_required
def view_sales():
    if current_user.role != 'admin':
        flash(_('Access denied. Admin privileges required.'), 'danger')
        return redirect(url_for('index'))
    
    # Get query parameters
    start_date_str = request.args.get('start_date', '')
    end_date_str = request.args.get('end_date', '')
    category = request.args.get('category', '')
    cashier_id = request.args.get('cashier_id', '')
    
    # Parse dates
    try:
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            start_datetime = datetime.combine(start_date, datetime.min.time())
        else:
            # Default to beginning of current month
            today = datetime.now().date()
            start_date = datetime(today.year, today.month, 1).date()
            start_datetime = datetime.combine(start_date, datetime.min.time())
            start_date_str = start_date.strftime('%Y-%m-%d')
            
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            end_datetime = datetime.combine(end_date, datetime.max.time())
        else:
            # Default to today
            end_date = datetime.now().date()
            end_datetime = datetime.combine(end_date, datetime.max.time())
            end_date_str = end_date.strftime('%Y-%m-%d')
    except ValueError:
        flash(_('Invalid date format. Please use YYYY-MM-DD.'), 'danger')
        return redirect(url_for('view_sales'))
    
    # Build query
    query = Sale.query.filter(Sale.date_sold.between(start_datetime, end_datetime))
    
    if category and category != 'all':
        query = query.join(Product).filter(Product.category == category)
        
    if cashier_id and cashier_id.isdigit():
        query = query.filter(Sale.cashier_id == int(cashier_id))
    
    # Execute query
    sales = query.order_by(Sale.date_sold.desc()).all()
    
    # Calculate total revenue
    total_revenue = sum(sale.total_price for sale in sales)
    
    # Calculate total profit
    total_profit = sum((sale.total_price - (sale.product.purchase_price * sale.quantity)) for sale in sales)
    
    # Get all cashiers for the filter dropdown
    cashiers = User.query.filter_by(role='cashier').all()
    
    # Get all product categories for the filter dropdown
    categories = db.session.query(Product.category).distinct().order_by(Product.category).all()
    categories = [c[0] for c in categories]
    
    # Calculate sales by category
    category_summary = {}
    for sale in sales:
        category = sale.product.category
        if category not in category_summary:
            category_summary[category] = {
                'count': 0,
                'revenue': 0,
                'profit': 0
            }
        category_summary[category]['count'] += sale.quantity
        category_summary[category]['revenue'] += sale.total_price
        category_summary[category]['profit'] += (sale.total_price - (sale.product.purchase_price * sale.quantity))
    
    return render_template('view_sales.html', 
                           sales=sales, 
                           total_revenue=total_revenue,
                           total_profit=total_profit,
                           categories=categories,
                           category_summary=category_summary,
                           selected_category=category,
                           cashiers=cashiers,
                           selected_cashier_id=cashier_id,
                           start_date=start_date_str,
                           end_date=end_date_str)

@app.route('/delete_sale/<int:sale_id>', methods=['POST'])
@login_required
def delete_sale(sale_id):
    if current_user.role != 'admin':
        flash(_('Access denied. Admin privileges required.'), 'danger')
        return redirect(url_for('index'))
    
    sale = Sale.query.get_or_404(sale_id)
    
    # Return the stock to the product
    product = sale.product
    product.stock += sale.quantity
    
    # Store sale info for flash message
    product_name = sale.product.name
    quantity = sale.quantity
    sale_date = sale.date_sold.strftime('%Y-%m-%d %H:%M')
    cashier_name = sale.cashier.username
    
    # Delete the sale
    db.session.delete(sale)
    db.session.commit()
    
    flash(_('Sale of %(quantity)d %(product)s by %(cashier)s on %(date)s has been deleted and stock has been restored.', 
            quantity=quantity, product=product_name, cashier=cashier_name, date=sale_date), 'success')
    
    return redirect(url_for('view_sales'))

@app.route('/cashier/dashboard')
@login_required
def cashier_dashboard():
    if current_user.role != 'cashier':
        flash(_('Access denied. Cashier privileges required.'), 'danger')
        return redirect(url_for('index'))
    
    # Get today's date
    today = datetime.now().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())
    
    # Get products in stock
    products = Product.query.filter(Product.stock > 0).all()
    
    # Get today's sales for this cashier
    today_sales = Sale.query.filter(
        Sale.date_sold.between(today_start, today_end),
        Sale.cashier_id == current_user.id
    ).all()
    
    # Calculate total revenue for today
    total_revenue = sum(sale.total_price for sale in today_sales)
    
    return render_template('cashier_dashboard.html', 
                           products=products,
                           today_sales=today_sales,
                           total_revenue=total_revenue)

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
            return redirect(url_for('sell_product'))
        
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
    
    # Get products with stock > 0
    products = Product.query.filter(Product.stock > 0).all()
    return render_template('sell_product.html', products=products)

@app.route('/cashier/sales')
@login_required
def view_cashier_sales():
    if current_user.role != 'cashier':
        flash(_('Access denied. Cashier privileges required.'), 'danger')
        return redirect(url_for('index'))
    
    # Get filter parameters
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    category = request.args.get('category')
    
    # Base query - only show sales by the current cashier
    query = Sale.query.filter(Sale.cashier_id == current_user.id)
    
    # Apply date filters if provided
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            query = query.filter(Sale.date_sold >= start_date)
        except ValueError:
            flash(_('Invalid start date format. Please use YYYY-MM-DD.'), 'warning')
    
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            # Add one day to include the end date
            end_date = datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59)
            query = query.filter(Sale.date_sold <= end_date)
        except ValueError:
            flash(_('Invalid end date format. Please use YYYY-MM-DD.'), 'warning')
    
    # Apply category filter if provided
    if category and category != 'all':
        query = query.join(Product).filter(Product.category == category)
    
    # Get all sales based on the filters
    sales = query.order_by(Sale.date_sold.desc()).all()
    
    # Calculate total revenue
    total_revenue = sum(sale.total_price for sale in sales)
    
    # Get unique categories for the filter dropdown
    categories = db.session.query(Product.category).distinct().all()
    categories = [cat[0] for cat in categories]
    
    # Group sales by category for the summary
    category_summary = {}
    for sale in sales:
        category = sale.product.category
        if category not in category_summary:
            category_summary[category] = {
                'count': 0,
                'revenue': 0
            }
        category_summary[category]['count'] += sale.quantity
        category_summary[category]['revenue'] += sale.total_price
    
    return render_template('cashier_sales.html', 
                           sales=sales, 
                           total_revenue=total_revenue,
                           categories=categories,
                           category_summary=category_summary,
                           selected_category=category,
                           start_date=start_date_str,
                           end_date=end_date_str)

# Initialize the database and create an admin user
def init_db_command():
    """Initialize the database and create admin and cashier users if they don't exist."""
    print("Creating database tables...")
    db.create_all()
    
    # Check if admin user exists
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        print("Created admin user with username 'admin' and password 'admin123'")
    else:
        print("Admin user already exists.")
    
    # Check if cashier user exists
    cashier = User.query.filter_by(username='cashier').first()
    if not cashier:
        cashier = User(username='cashier', role='cashier')
        cashier.set_password('cashier123')
        db.session.add(cashier)
        print("Created cashier user with username 'cashier' and password 'cashier123'")
    else:
        print("Cashier user already exists.")
    
    db.session.commit()
    print("Database initialization complete.")
    
    return True

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
