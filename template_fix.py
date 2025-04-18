#!/usr/bin/env python
"""
Template Fix for Smart Inventory System
This script updates all templates to properly handle internationalization
"""
import os
import sys
import logging
import shutil
import glob
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("template_fix.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("template_fix")

def fix_templates():
    """Update all templates to properly handle internationalization"""
    logger.info("Updating templates for proper internationalization...")
    
    # Get all template files
    template_dir = 'templates'
    template_files = glob.glob(os.path.join(template_dir, '*.html'))
    
    if not template_files:
        logger.warning("No template files found")
        return False
    
    success_count = 0
    
    for template_file in template_files:
        try:
            logger.info(f"Processing template: {template_file}")
            
            # Create backup
            backup_path = f"{template_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(template_file, backup_path)
            
            # Read the template file
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if the template already uses the translation function
            if '{{ _(' not in content and '{% trans' not in content:
                # Replace hardcoded strings with translation function calls
                # This is a simplified approach - in a real project, you would use a proper i18n extraction tool
                
                # Common UI strings to translate
                translations = {
                    '<title>Smart Inventory</title>': '<title>{{ _("Smart Inventory") }}</title>',
                    '<h1>Smart Inventory</h1>': '<h1>{{ _("Smart Inventory") }}</h1>',
                    '<h2>Smart Inventory</h2>': '<h2>{{ _("Smart Inventory") }}</h2>',
                    '<h3>Smart Inventory</h3>': '<h3>{{ _("Smart Inventory") }}</h3>',
                    'Login': '{{ _("Login") }}',
                    'Username': '{{ _("Username") }}',
                    'Password': '{{ _("Password") }}',
                    'Submit': '{{ _("Submit") }}',
                    'Logout': '{{ _("Logout") }}',
                    'Dashboard': '{{ _("Dashboard") }}',
                    'Products': '{{ _("Products") }}',
                    'Sales': '{{ _("Sales") }}',
                    'Add Product': '{{ _("Add Product") }}',
                    'Edit Product': '{{ _("Edit Product") }}',
                    'Delete': '{{ _("Delete") }}',
                    'Name': '{{ _("Name") }}',
                    'Description': '{{ _("Description") }}',
                    'Category': '{{ _("Category") }}',
                    'Price': '{{ _("Price") }}',
                    'Stock': '{{ _("Stock") }}',
                    'Actions': '{{ _("Actions") }}',
                    'Search': '{{ _("Search") }}',
                    'Quantity': '{{ _("Quantity") }}',
                    'Total': '{{ _("Total") }}',
                    'Date': '{{ _("Date") }}',
                    'No products found': '{{ _("No products found") }}',
                    'No sales found': '{{ _("No sales found") }}',
                    'Low Stock Alert': '{{ _("Low Stock Alert") }}',
                    'Today\'s Sales': '{{ _("Today\'s Sales") }}',
                    'Total Revenue': '{{ _("Total Revenue") }}',
                }
                
                # Apply translations
                for original, translated in translations.items():
                    content = content.replace(original, translated)
                
                logger.info(f"Applied translations to {template_file}")
            else:
                logger.info(f"Template {template_file} already uses translation functions")
            
            # Add language selector if it's the base template and doesn't already have one
            if template_file.endswith('base.html') and '<select name="language"' not in content:
                # Find the navigation section
                nav_start = content.find('<nav')
                if nav_start != -1:
                    nav_end = content.find('</nav>', nav_start)
                    if nav_end != -1:
                        # Add language selector before the end of the navigation
                        language_selector = '''
                        <div class="language-selector">
                            <form action="{{ url_for('set_language', language='en') }}" method="GET" style="display: inline;">
                                <button type="submit" class="btn btn-sm btn-outline-secondary">English</button>
                            </form>
                            <form action="{{ url_for('set_language', language='rw') }}" method="GET" style="display: inline;">
                                <button type="submit" class="btn btn-sm btn-outline-secondary">Kinyarwanda</button>
                            </form>
                        </div>
                        '''
                        content = content[:nav_end] + language_selector + content[nav_end:]
                        logger.info("Added language selector to base template")
            
            # Write the updated content back to the template file
            with open(template_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            success_count += 1
            logger.info(f"Successfully updated template: {template_file}")
        
        except Exception as e:
            logger.error(f"Error updating template {template_file}: {e}")
    
    logger.info(f"Successfully updated {success_count} out of {len(template_files)} templates")
    return success_count > 0

if __name__ == "__main__":
    print("Running template fix for Smart Inventory System...")
    
    if fix_templates():
        print("Successfully updated templates for proper internationalization")
        print("\nTemplate fix completed!")
        print("\nInstructions:")
        print("1. Restart the Flask server if it's running")
        print("2. Try accessing the site at http://127.0.0.1:5000")
        print("3. Test the language selector to switch between English and Kinyarwanda")
    else:
        print("Failed to update templates")
