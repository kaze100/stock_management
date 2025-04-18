#!/usr/bin/env python
"""
Internationalization Fix for Smart Inventory System
This script fixes the translation function issue in the application
"""
import os
import sys
import logging
import shutil
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("i18n_fix.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("i18n_fix")

def fix_i18n():
    """Fix the internationalization issues in app.py"""
    logger.info("Fixing internationalization issues in app.py...")
    
    app_path = 'app.py'
    backup_path = f"{app_path}.i18n_fix_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        # Create backup
        if os.path.exists(app_path):
            shutil.copy2(app_path, backup_path)
            logger.info(f"Created backup: {backup_path}")
        
        # Read the current app.py
        with open(app_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the Flask app initialization
        app_init_start = content.find("app = Flask(__name__)")
        if app_init_start == -1:
            logger.warning("Could not find Flask app initialization")
            return False
        
        # Find the translation function
        translation_start = content.find("# Simple translation function")
        if translation_start == -1:
            logger.warning("Could not find translation function")
            return False
        
        translation_end = content.find("\n\n", translation_start)
        if translation_end == -1:
            logger.warning("Could not find end of translation function")
            return False
        
        # Replace the translation function with a proper implementation
        new_translation = """# Internationalization setup
try:
    from flask_babel import Babel, gettext as _

    def get_locale():
        return session.get('language', 'en')

    babel = Babel(app, locale_selector=get_locale)

    @app.route('/set_language/<language>')
    def set_language(language):
        session['language'] = language
        return redirect(request.referrer or url_for('index'))

    # Make the translation function available to templates
    @app.context_processor
    def inject_globals():
        return dict(_=_)

except ImportError:
    # Fallback translation function if Flask-Babel is not available
    def _(text, **variables):
        return text % variables if variables else text

    # Make the fallback translation function available to templates
    @app.context_processor
    def inject_globals():
        return dict(_=_)
"""
        
        # Replace the translation function
        updated_content = content[:translation_start] + new_translation + content[translation_end:]
        
        # Write the updated content back to app.py
        with open(app_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        logger.info("Successfully fixed internationalization issues in app.py")
        return True
    
    except Exception as e:
        logger.error(f"Error fixing internationalization: {e}")
        return False

if __name__ == "__main__":
    print("Running internationalization fix for Smart Inventory System...")
    
    if fix_i18n():
        print("Successfully fixed internationalization issues in app.py")
        print("\nInternationalization fix completed!")
        print("\nInstructions:")
        print("1. Stop any running Flask server")
        print("2. Make sure Flask-Babel is installed: pip install Flask-Babel")
        print("3. Run 'python app.py' to start the server again")
        print("4. Try accessing the site at http://127.0.0.1:5000")
        print("5. Login with:")
        print("   - Admin: username 'renoir01', password 'Renoir@654'")
        print("   - Cashier: username 'epi', password 'Epi@654'")
    else:
        print("Failed to fix internationalization issues in app.py")
