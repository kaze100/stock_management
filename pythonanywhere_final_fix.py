#!/usr/bin/env python3
import os
import re
import sys

def fix_admin_dashboard():
    """Replace the admin_dashboard.html template with the fixed version."""
    template_path = 'templates/admin_dashboard.html'
    
    # The fixed template content
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

def add_delete_sale_route():
    """Add the delete_sale route to app.py."""
    app_path = 'app.py'
    
    with open(app_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Check if the route already exists
    if 'def delete_sale(' in content:
        print("delete_sale route already exists in app.py")
        return False
    
    # Find a good place to add the route (after view_sales function)
    view_sales_pattern = r'def view_sales\(\):[^@]*?return render_template\('
    view_sales_match = re.search(view_sales_pattern, content, re.DOTALL)
    
    if not view_sales_match:
        # Try to find another suitable location
        route_pattern = r'@app\.route\(.*?\)\s*@login_required\s*def .*?\(.*?\):.*?return .*?$'
        route_matches = list(re.finditer(route_pattern, content, re.DOTALL))
        
        if route_matches:
            # Use the last route as insertion point
            last_route = route_matches[-1]
            end_pos = last_route.end()
        else:
            # Just append to the end of the file
            end_pos = len(content)
    else:
        # Get the end position of the view_sales function
        end_pos = view_sales_match.end()
        
        # Find the next route or function definition
        next_route = content.find('@app.route', end_pos)
        if next_route != -1:
            end_pos = next_route
    
    # Insert the new route
    delete_sale_route = """

@app.route('/admin/sales/delete/<int:sale_id>', methods=['POST'])
@login_required
def delete_sale(sale_id):
    if not current_user.is_admin:
        flash(_('You do not have permission to delete sales.'), 'danger')
        return redirect(url_for('index'))
    
    sale = Sale.query.get_or_404(sale_id)
    
    # Restore the stock to the product
    product = Product.query.get(sale.product_id)
    if product:
        product.stock += sale.quantity
        db.session.add(product)
    
    db.session.delete(sale)
    db.session.commit()
    
    flash(_('Sale deleted successfully.'), 'success')
    return redirect(url_for('view_sales'))
"""
    
    modified_content = content[:end_pos] + delete_sale_route + content[end_pos:]
    
    with open(app_path, 'w', encoding='utf-8') as file:
        file.write(modified_content)
    
    print("Added delete_sale route to app.py")
    return True

def check_view_sales_template():
    """Check if the delete form in view_sales.html is already commented out."""
    template_path = 'templates/view_sales.html'
    
    with open(template_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Check if the delete form is already commented out
    if '<!-- Delete button removed until route is implemented' in content:
        print("Delete form is already commented out in view_sales.html")
        return True
    
    # Find and comment out the delete form
    pattern = r'<form action="\{\{ url_for\(\'delete_sale\', sale_id=sale\.id\) \}\}" method="POST".*?</form>'
    replacement = '<!-- Delete button removed until route is implemented\n\\g<0>\n-->'
    modified_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    if modified_content == content:
        print("No delete form found in view_sales.html")
        return False
    
    with open(template_path, 'w', encoding='utf-8') as file:
        file.write(modified_content)
    
    print("Fixed view_sales.html template by commenting out the delete form")
    return True

if __name__ == "__main__":
    print("=== Smart Inventory System - PythonAnywhere Final Fix ===")
    
    # Fix the admin_dashboard.html template
    admin_dashboard_fixed = fix_admin_dashboard()
    
    # Add the delete_sale route to app.py
    delete_sale_added = add_delete_sale_route()
    
    # Check the view_sales.html template
    view_sales_checked = check_view_sales_template()
    
    if admin_dashboard_fixed or delete_sale_added or view_sales_checked:
        print("\n=== All fixes applied successfully ===")
        print("Please reload your web application in PythonAnywhere.")
    else:
        print("\n=== No fixes were needed or applied ===")
        print("If you're still experiencing issues, please check the error logs again.")
