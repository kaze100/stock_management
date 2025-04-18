#!/usr/bin/env python3
import os

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
    print("=== Smart Inventory System - Enable Delete Sales Function ===")
    
    if enable_delete_button():
        print("\n=== Delete sales function enabled successfully ===")
        print("Please reload your web application to apply the changes.")
    else:
        print("\n=== Failed to enable delete sales function ===")
        print("You may need to manually edit the view_sales.html template.")
        print("Look for the commented out delete button form and uncomment it.")
