#!/usr/bin/env python3
import os

def add_delete_product_function():
    """Add a new delete_product function to app.py."""
    app_path = 'app.py'
    
    if not os.path.exists(app_path):
        print(f"Error: {app_path} not found")
        return False
    
    with open(app_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Check if delete_product function already exists
    if 'def delete_product(' in content:
        print("delete_product function already exists, but we'll add a new version with a different name")
    
    # Find a good place to add the function (after manage_products or at the end)
    insert_position = len(content)
    if 'def manage_products(' in content:
        manage_products_idx = content.find('def manage_products(')
        if manage_products_idx != -1:
            # Find the next route after manage_products
            next_route_idx = content.find('@app.route', manage_products_idx)
            if next_route_idx != -1:
                # Insert before the next route
                insert_position = next_route_idx
    
    # Insert the new function
    new_content = content[:insert_position] + delete_product_function + content[insert_position:]
    
    with open(app_path, 'w', encoding='utf-8') as file:
        file.write(new_content)
    
    print("Added new delete_product_v2 function to app.py")
    return True

# The delete_product function to add
delete_product_function = """
@app.route('/admin/products/delete/<int:product_id>', methods=['GET', 'POST'])
@login_required
def delete_product_v2(product_id):
    try:
        # Check if user has admin role
        if current_user.role != "admin":
            flash(_('You do not have permission to delete products.'), 'danger')
            return redirect(url_for('index'))
        
        product = Product.query.get_or_404(product_id)
        
        # Check if the product has associated sales
        sales = Sale.query.filter_by(product_id=product_id).first()
        if sales:
            flash(_('Cannot delete product with associated sales.'), 'warning')
            return redirect(url_for('manage_products'))
        
        # Delete the product
        db.session.delete(product)
        db.session.commit()
        
        flash(_('Product deleted successfully.'), 'success')
        return redirect(url_for('manage_products'))
    except Exception as e:
        db.session.rollback()
        flash(_('An error occurred while deleting the product.'), 'danger')
        return redirect(url_for('manage_products'))
"""

def update_manage_products_template():
    """Update the manage_products.html template to use the new delete_product_v2 route."""
    template_path = 'templates/manage_products.html'
    
    if not os.path.exists(template_path):
        print(f"Error: {template_path} not found")
        return False
    
    with open(template_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Update the delete product links/forms to point to the new route
    if 'delete_product' in content:
        # Replace all occurrences of delete_product with delete_product_v2
        modified_content = content.replace('delete_product', 'delete_product_v2')
        
        with open(template_path, 'w', encoding='utf-8') as file:
            file.write(modified_content)
        
        print(f"Updated {template_path} to use delete_product_v2")
        return True
    else:
        print(f"No delete_product references found in {template_path}")
        return False

if __name__ == "__main__":
    print("=== Smart Inventory System - Add Delete Product Function ===")
    
    added_function = add_delete_product_function()
    updated_template = update_manage_products_template()
    
    if added_function or updated_template:
        print("\n=== Delete product function added/updated successfully ===")
        print("Please reload your web application to apply the changes.")
    else:
        print("\n=== Failed to add/update delete product function ===")
        print("You may need to manually edit the app.py file.")
