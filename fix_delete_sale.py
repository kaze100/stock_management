#!/usr/bin/env python3
import os
import re

def fix_delete_sale_route():
    """Fix the delete_sale route in app.py to handle errors better."""
    app_path = 'app.py'
    
    if not os.path.exists(app_path):
        print(f"Error: {app_path} not found")
        return False
    
    with open(app_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Find the delete_sale route
    delete_sale_pattern = r'@app\.route\(\'/admin/sales/delete/.*?\'\).*?def delete_sale\(.*?\):.*?return redirect\(url_for\(\'view_sales\'\)\)'
    delete_sale_match = re.search(delete_sale_pattern, content, re.DOTALL)
    
    if not delete_sale_match:
        print("Could not find delete_sale route in app.py")
        return False
    
    # Replace with improved version
    improved_delete_sale = """
@app.route('/admin/sales/delete/<int:sale_id>', methods=['POST', 'GET'])
@login_required
def delete_sale(sale_id):
    try:
        if not current_user.is_admin:
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
    
    modified_content = content.replace(delete_sale_match.group(0), improved_delete_sale)
    
    with open(app_path, 'w', encoding='utf-8') as file:
        file.write(modified_content)
    
    print("Fixed delete_sale route in app.py")
    return True

if __name__ == "__main__":
    print("=== Smart Inventory System - Fix Delete Sale Function ===")
    
    if fix_delete_sale_route():
        print("\n=== Delete sale function fixed successfully ===")
        print("Please reload your web application to apply the changes.")
    else:
        print("\n=== Failed to fix delete sale function ===")
        print("You may need to manually edit the app.py file.")
        print("Check the error logs on PythonAnywhere for more details.")
