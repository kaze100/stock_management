#!/usr/bin/env python3
import os
import sys
import re

def fix_admin_dashboard_template():
    """Fix the admin_dashboard.html template syntax errors completely."""
    template_path = 'templates/admin_dashboard.html'
    if not os.path.exists(template_path):
        print(f"Error: {template_path} not found")
        return False
    
    with open(template_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Create a completely new low stock products section
    # Find the low stock products table
    low_stock_section_pattern = r'<div class="card-body">\s*<h5 class="card-title">.*?{{ _\("Low Stock Products"\) }}.*?</h5>.*?<div class="table-responsive">.*?<table class="table">.*?<thead>.*?</thead>.*?<tbody>(.*?)</tbody>.*?</table>'
    low_stock_match = re.search(low_stock_section_pattern, content, re.DOTALL)
    
    if not low_stock_match:
        print("Could not find the low stock products table in admin_dashboard.html")
        return False
    
    # Extract the table body content
    table_body = low_stock_match.group(1)
    
    # Create a properly structured table body with correct Jinja syntax
    new_table_body = """
                <tbody>
                  {% if low_stock_products %}
                    {% for product in low_stock_products %}
                    <tr>
                      <td>{{ product.name }}</td>
                      <td>{{ product.category }}</td>
                      <td>{{ product.stock }}</td>
                      <td>{{ product.low_stock_threshold }}</td>
                      <td>
                        <a href="{{ url_for('edit_product', product_id=product.id) }}" class="btn btn-sm btn-primary">
                          <i class="fas fa-edit"></i> {{ _("Edit") }}
                        </a>
                      </td>
                    </tr>
                    {% endfor %}
                  {% else %}
                    <tr><td colspan="5">{{ _("No low stock products") }}</td></tr>
                  {% endif %}
                </tbody>"""
    
    # Replace the old table body with the new one
    modified_content = re.sub(low_stock_section_pattern, 
                             lambda m: m.group(0).replace(table_body, new_table_body), 
                             content, 
                             flags=re.DOTALL)
    
    # Check for any other potential nesting issues with blocks
    # Make sure all blocks are properly closed
    block_pattern = r'{%\s*block\s+(\w+)\s*%}(.*?){%\s*endblock\s*%}'
    blocks = re.findall(block_pattern, modified_content, re.DOTALL)
    
    # Check if there are any unclosed if statements within blocks
    for block_name, block_content in blocks:
        if_count = len(re.findall(r'{%\s*if\s+', block_content))
        endif_count = len(re.findall(r'{%\s*endif\s*%}', block_content))
        
        if if_count != endif_count:
            print(f"Warning: Block '{block_name}' has {if_count} 'if' tags but {endif_count} 'endif' tags")
    
    with open(template_path, 'w', encoding='utf-8') as file:
        file.write(modified_content)
    
    print("Fixed admin_dashboard.html template syntax errors")
    return True

def fix_view_sales_template():
    """Fix the view_sales.html template by removing or commenting out the delete button form."""
    template_path = 'templates/view_sales.html'
    if not os.path.exists(template_path):
        print(f"Error: {template_path} not found")
        return False
    
    with open(template_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Find and comment out the delete form
    pattern = r'<form action="\{\{ url_for\(\'delete_sale\', sale_id=sale\.id\) \}\}" method="POST".*?</form>'
    replacement = '<!-- Delete button removed until route is implemented\n\\g<0>\n-->'
    modified_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    if modified_content == content:
        print("No delete form found in view_sales.html or already fixed")
        return False
    
    with open(template_path, 'w', encoding='utf-8') as file:
        file.write(modified_content)
    
    print("Fixed view_sales.html template by commenting out the delete form")
    return True

def add_delete_sale_route():
    """Add the missing delete_sale route to app.py."""
    app_path = 'app.py'
    if not os.path.exists(app_path):
        print(f"Error: {app_path} not found")
        return False
    
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
        print("Could not find view_sales function in app.py")
        return False
    
    # Get the end position of the view_sales function
    end_pos = view_sales_match.end()
    
    # Find the next route or function definition
    next_route = content.find('@app.route', end_pos)
    if next_route == -1:
        next_route = len(content)
    
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
    
    modified_content = content[:next_route] + delete_sale_route + content[next_route:]
    
    with open(app_path, 'w', encoding='utf-8') as file:
        file.write(modified_content)
    
    print("Added delete_sale route to app.py")
    return True

if __name__ == "__main__":
    print("=== Smart Inventory System - PythonAnywhere Fix Script v3 ===")
    
    # Fix the templates
    admin_dashboard_fixed = fix_admin_dashboard_template()
    view_sales_fixed = fix_view_sales_template()
    
    # Add the missing route
    delete_sale_added = add_delete_sale_route()
    
    if admin_dashboard_fixed or view_sales_fixed or delete_sale_added:
        print("\n=== Fixes applied successfully ===")
        print("Please reload your web application in PythonAnywhere.")
    else:
        print("\n=== No fixes were needed or applied ===")
        print("If you're still experiencing issues, please check the error logs again.")
