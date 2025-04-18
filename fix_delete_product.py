#!/usr/bin/env python3
import os
import re

def fix_delete_product_route():
    """Fix the delete_product route in app.py to accept both GET and POST methods."""
    app_path = 'app.py'
    
    if not os.path.exists(app_path):
        print(f"Error: {app_path} not found")
        return False
    
    with open(app_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Find the delete_product route
    delete_product_pattern = r'@app\.route\(\'/admin/products/delete/.*?\'\).*?def delete_product\(.*?\):.*?return redirect\(.*?\)'
    delete_product_match = re.search(delete_product_pattern, content, re.DOTALL)
    
    if not delete_product_match:
        print("Could not find delete_product route in app.py")
        return False
    
    # Get the current function
    current_function = delete_product_match.group(0)
    
    # Check if methods parameter is already present
    if "methods=['POST']" in current_function or "methods=['GET', 'POST']" in current_function:
        # Update to include both methods
        updated_function = current_function.replace("methods=['POST']", "methods=['GET', 'POST']")
        if updated_function == current_function:  # No change was made
            print("delete_product route already accepts both GET and POST methods")
            return True
    else:
        # Add methods parameter
        updated_function = current_function.replace(
            "@app.route('/admin/products/delete/<int:product_id>')",
            "@app.route('/admin/products/delete/<int:product_id>', methods=['GET', 'POST'])"
        )
    
    # Replace the function in the content
    content = content.replace(current_function, updated_function)
    
    with open(app_path, 'w', encoding='utf-8') as file:
        file.write(content)
    
    print("Fixed delete_product route in app.py")
    return True

if __name__ == "__main__":
    print("=== Smart Inventory System - Fix Delete Product Function ===")
    
    if fix_delete_product_route():
        print("\n=== Delete product function fixed successfully ===")
        print("Please reload your web application to apply the changes.")
    else:
        print("\n=== Failed to fix delete product function ===")
        print("You may need to manually edit the app.py file.")
