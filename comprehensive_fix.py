#!/usr/bin/env python3
import os
import re

def fix_admin_dashboard_template():
    """Fix the admin_dashboard.html template syntax errors."""
    template_path = 'templates/admin_dashboard.html'
    
    if not os.path.exists(template_path):
        print(f"Error: {template_path} not found")
        return False
    
    # Use the fixed template from earlier
    fixed_template = """{% extends 'base.html' %}

{% block title %}{{ _('Admin Dashboard') }} - {{ _('Smart Inventory') }}{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/dashboard.css') }}">
{% endblock %}

{% block content %}
<div class="dashboard-header">
    <h1>{{ _('Admin Dashboard') }}</h1>
    <p class="dashboard-subtitle">{{ _('Overview of your inventory and sales') }}</p>
</div>

<div class="row">
    <div class="col col-md-3">
        <div class="widget widget-primary">
            <i class="fas fa-box-open widget-icon"></i>
            <h3 class="widget-title">{{ _('Total Products') }}</h3>
            <div class="widget-value">{{ total_products }}</div>
            <p class="widget-description">{{ _('Total products in inventory') }}</p>
            <a href="{{ url_for('manage_products') }}" class="widget-link">{{ _('View all products') }} <i class="fas fa-arrow-right"></i></a>
        </div>
    </div>
    
    <div class="col col-md-3">
        <div class="widget widget-danger">
            <i class="fas fa-exclamation-triangle widget-icon"></i>
            <h3 class="widget-title">{{ _('Low Stock Items') }}</h3>
            <div class="widget-value {% if low_stock_products|length > 0 %}text-danger{% endif %}">
                {{ low_stock_products|length }}
            </div>
            <p class="widget-description">{{ _('Products that need restocking') }}</p>
            {% if low_stock_products|length > 0 %}
            <a href="#low-stock-section" class="widget-link">{{ _('View details') }} <i class="fas fa-arrow-right"></i></a>
            {% endif %}
        </div>
    </div>
    
    <div class="col col-md-3">
        <div class="widget widget-info">
            <i class="fas fa-shopping-cart widget-icon"></i>
            <h3 class="widget-title">{{ _('Today\\'s Sales') }}</h3>
            <div class="widget-value">{{ total_sales }}</div>
            <p class="widget-description">{{ _('Total sales made today') }}</p>
            <a href="{{ url_for('view_sales') }}" class="widget-link">{{ _('View all sales') }} <i class="fas fa-arrow-right"></i></a>
        </div>
    </div>
    
    <div class="col col-md-3">
        <div class="widget widget-success">
            <i class="fas fa-money-bill-wave widget-icon"></i>
            <h3 class="widget-title">{{ _('Today\\'s Revenue') }}</h3>
            <div class="widget-value">RWF {{ "%.0f"|format(total_revenue) }}</div>
            <p class="widget-description">{{ _('Total revenue generated today') }}</p>
            <a href="{{ url_for('view_sales') }}" class="widget-link">{{ _('View sales report') }} <i class="fas fa-arrow-right"></i></a>
        </div>
    </div>
</div>

<div class="row mt-4">
    <div class="col col-md-3">
        <div class="widget widget-warning">
            <i class="fas fa-chart-line widget-icon"></i>
            <h3 class="widget-title">{{ _('Today\\'s Profit') }}</h3>
            <div class="widget-value">RWF {{ "%.0f"|format(total_profit) }}</div>
            <p class="widget-description">{{ _('Total profit generated today') }}</p>
            <a href="{{ url_for('view_sales') }}" class="widget-link">{{ _('View profit report') }} <i class="fas fa-arrow-right"></i></a>
        </div>
    </div>
    
    <div class="col col-md-9">
        <div class="card" id="low-stock-section">
            <div class="card-header">
                <h2><i class="fas fa-exclamation-circle"></i> {{ _('Low Stock Products') }}</h2>
            </div>
            <div class="card-body">
                {% if low_stock_products|length > 0 %}
                <div class="table-responsive">
                    <table class="table">
                        <thead>
                            <tr>
                                <th>{{ _('Product') }}</th>
                                <th>{{ _('Category') }}</th>
                                <th>{{ _('Current Stock') }}</th>
                                <th>{{ _('Threshold') }}</th>
                                <th>{{ _('Action') }}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for product in low_stock_products %}
                            <tr>
                                <td>{{ product.name }}</td>
                                <td><span class="badge category-badge">{{ product.category }}</span></td>
                                <td class="text-danger">{{ product.stock }}</td>
                                <td>{{ product.low_stock_threshold }}</td>
                                <td>
                                    <a href="{{ url_for('edit_product', product_id=product.id) }}" class="btn btn-sm btn-primary">
                                        <i class="fas fa-edit"></i> {{ _('Update') }}
                                    </a>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% else %}
                <div class="alert alert-success">
                    <i class="fas fa-check-circle"></i> {{ _('All products are well stocked!') }}
                </div>
                {% endif %}
            </div>
        </div>
    </div>
</div>

<div class="row mt-4">
    <div class="col col-md-6">
        <div class="card">
            <div class="card-header">
                <h2><i class="fas fa-chart-pie"></i> {{ _('Inventory by Category') }}</h2>
            </div>
            <div class="card-body">
                {% set categories = {} %}
                {% for product in products %}
                    {% if product.category in categories %}
                        {% set _ = categories.update({product.category: categories[product.category] + 1}) %}
                    {% else %}
                        {% set _ = categories.update({product.category: 1}) %}
                    {% endif %}
                {% endfor %}
                
                <div class="category-stats">
                    {% for category, count in categories.items() %}
                    <div class="category-stat-item">
                        <div class="category-header">
                            <h4>{{ category }}</h4>
                        </div>
                        <div class="category-body">
                            <div class="category-count">{{ count }}</div>
                            <div class="category-bar">
                                <div class="category-progress" data-width="{{ (count / total_products * 100)|round }}"></div>
                            </div>
                            <div class="category-percent">{{ (count / total_products * 100)|round }}%</div>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>
    
    <div class="col col-md-6">
        <div class="card">
            <div class="card-header">
                <h2><i class="fas fa-tasks"></i> {{ _('Quick Actions') }}</h2>
            </div>
            <div class="card-body">
                <div class="quick-actions">
                    <a href="{{ url_for('add_product') }}" class="quick-action-btn">
                        <i class="fas fa-plus-circle"></i>
                        <span>{{ _('Add New Product') }}</span>
                    </a>
                    <a href="{{ url_for('view_sales') }}" class="quick-action-btn">
                        <i class="fas fa-chart-line"></i>
                        <span>{{ _('View Sales Report') }}</span>
                    </a>
                    <a href="{{ url_for('manage_products') }}" class="quick-action-btn">
                        <i class="fas fa-boxes"></i>
                        <span>{{ _('Manage Products') }}</span>
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}"""
    
    # Write the fixed template
    with open(template_path, 'w', encoding='utf-8') as file:
        file.write(fixed_template)
    
    print(f"Fixed {template_path}")
    return True

def fix_delete_sale_function():
    """Fix the delete_sale function in app.py."""
    app_path = 'app.py'
    
    if not os.path.exists(app_path):
        print(f"Error: {app_path} not found")
        return False
    
    with open(app_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # First, check if we need to add the is_admin property to the User model
    user_model_pattern = r'class User\(.*?\):.*?def __repr__\(self\):'
    user_model_match = re.search(user_model_pattern, content, re.DOTALL)
    
    if not user_model_match:
        print("Could not find User model in app.py")
        return False
    
    user_model = user_model_match.group(0)
    
    # Check if is_admin property already exists
    if 'def is_admin(self):' not in user_model:
        # Add is_admin property to User model
        modified_user_model = user_model.replace(
            'def __repr__(self):',
            '@property\n    def is_admin(self):\n        return self.role == "admin"\n\n    def __repr__(self):'
        )
        content = content.replace(user_model, modified_user_model)
    
    # Now add or replace the delete_sale function
    delete_sale_pattern = r'@app\.route\(\'/admin/sales/delete/.*?\'\).*?def delete_sale\(.*?\):.*?return redirect\(.*?\)'
    delete_sale_match = re.search(delete_sale_pattern, content, re.DOTALL)
    
    delete_sale_function = """
@app.route('/admin/sales/delete/<int:sale_id>', methods=['POST', 'GET'])
@login_required
def delete_sale(sale_id):
    try:
        # Check if user has admin role
        if current_user.role != "admin":
            flash(_('You do not have permission to delete sales.'), 'danger')
            return redirect(url_for('index'))
        
        sale = Sale.query.get_or_404(sale_id)
        logger.info(f"Deleting sale ID {sale_id} for product {sale.product_id} with quantity {sale.quantity}")
        
        # Restore the stock to the product
        product = Product.query.get(sale.product_id)
        if product:
            logger.info(f"Restoring stock: {product.name} current stock {product.stock}, adding {sale.quantity}")
            product.stock += sale.quantity
            db.session.add(product)
            logger.info(f"New stock level: {product.stock}")
        else:
            logger.warning(f"Product ID {sale.product_id} not found when deleting sale {sale_id}")
        
        # Delete the sale
        db.session.delete(sale)
        db.session.commit()
        
        flash(_('Sale deleted successfully.'), 'success')
        return redirect(url_for('view_sales'))
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting sale {sale_id}: {str(e)}")
        flash(_('An error occurred while deleting the sale.'), 'danger')
        return redirect(url_for('view_sales'))
"""
    
    if delete_sale_match:
        # Replace existing function
        content = content.replace(delete_sale_match.group(0), delete_sale_function)
    else:
        # Add new function after view_sales
        view_sales_pattern = r'def view_sales\(\):.*?return render_template\('
        view_sales_match = re.search(view_sales_pattern, content, re.DOTALL)
        
        if view_sales_match:
            end_pos = view_sales_match.end()
            next_route = content.find('@app.route', end_pos)
            if next_route != -1:
                content = content[:next_route] + delete_sale_function + content[next_route:]
            else:
                content += delete_sale_function
        else:
            # Append to the end of the file
            content += delete_sale_function
    
    with open(app_path, 'w', encoding='utf-8') as file:
        file.write(content)
    
    print("Fixed delete_sale function in app.py")
    return True

def enable_delete_button():
    """Uncomment the delete button in the view_sales.html template."""
    template_path = 'templates/view_sales.html'
    
    if not os.path.exists(template_path):
        print(f"Error: {template_path} not found")
        return False
    
    with open(template_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Check if the delete form is commented out
    if '<!-- Delete button removed until route is implemented' in content:
        # Uncomment the delete form
        modified_content = content.replace(
            '<!-- Delete button removed until route is implemented\n', ''
        ).replace(
            '\n-->', ''
        )
        
        with open(template_path, 'w', encoding='utf-8') as file:
            file.write(modified_content)
        
        print(f"Enabled delete button in {template_path}")
        return True
    else:
        print(f"Delete button is not commented out in {template_path} or has a different comment format")
        return False

if __name__ == "__main__":
    print("=== Smart Inventory System - Comprehensive Fix ===")
    
    # Fix the admin_dashboard.html template
    admin_dashboard_fixed = fix_admin_dashboard_template()
    
    # Fix the delete_sale function
    delete_sale_fixed = fix_delete_sale_function()
    
    # Enable the delete button
    delete_button_enabled = enable_delete_button()
    
    if admin_dashboard_fixed or delete_sale_fixed or delete_button_enabled:
        print("\n=== All fixes applied successfully ===")
        print("Please reload your web application to apply the changes.")
    else:
        print("\n=== No fixes were needed or applied ===")
        print("If you're still experiencing issues, please check the error logs again.")
