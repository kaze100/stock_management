#!/usr/bin/env python3
import os

def add_delete_sale_function():
    """Add the delete_sale function directly to app.py."""
    app_path = 'app.py'
    
    if not os.path.exists(app_path):
        print(f"Error: {app_path} not found")
        return False
    
    with open(app_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Check if delete_sale function already exists
    if 'def delete_sale(' in content:
        print("delete_sale function already exists, replacing it...")
        
        # Find the start of the function
        start_idx = content.find('@app.route(\'/admin/sales/delete/')
        if start_idx == -1:
            print("Could not find the start of the delete_sale function")
            return False
        
        # Find the end of the function (next route or end of file)
        end_idx = content.find('@app.route', start_idx + 1)
        if end_idx == -1:
            end_idx = len(content)
        
        # Replace the function
        content = content[:start_idx] + delete_sale_function + content[end_idx:]
    else:
        print("Adding new delete_sale function...")
        
        # Find a good place to add the function (after view_sales or at the end)
        if 'def view_sales(' in content:
            # Find the end of view_sales function
            view_sales_idx = content.find('def view_sales(')
            if view_sales_idx != -1:
                # Find the next route after view_sales
                next_route_idx = content.find('@app.route', view_sales_idx)
                if next_route_idx != -1:
                    # Insert before the next route
                    content = content[:next_route_idx] + delete_sale_function + content[next_route_idx:]
                else:
                    # Append to the end
                    content += delete_sale_function
            else:
                # Append to the end
                content += delete_sale_function
        else:
            # Append to the end
            content += delete_sale_function
    
    with open(app_path, 'w', encoding='utf-8') as file:
        file.write(content)
    
    print("Added/updated delete_sale function in app.py")
    return True

# The delete_sale function to add
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
        
        # Restore the stock to the product
        product = Product.query.get(sale.product_id)
        if product:
            product.stock += sale.quantity
            db.session.add(product)
        
        # Delete the sale
        db.session.delete(sale)
        db.session.commit()
        
        flash(_('Sale deleted successfully.'), 'success')
        return redirect(url_for('view_sales'))
    except Exception as e:
        db.session.rollback()
        flash(_('An error occurred while deleting the sale.'), 'danger')
        return redirect(url_for('view_sales'))
"""

if __name__ == "__main__":
    print("=== Smart Inventory System - Fix Delete Sale Function ===")
    
    if add_delete_sale_function():
        print("\n=== Delete sale function fixed successfully ===")
        print("Please reload your web application to apply the changes.")
    else:
        print("\n=== Failed to fix delete sale function ===")
        print("You may need to manually edit the app.py file.")
