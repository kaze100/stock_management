"""
Script to check for errors in the PythonAnywhere environment.
This will print detailed error information to help diagnose 500 Internal Server Errors.
"""
import os
import sys
import traceback
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("error_check.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def check_app_imports():
    """Test importing the app and its components to check for import errors."""
    try:
        logger.info("Checking app imports...")
        from app import app, db, Product, User, Sale
        logger.info("✓ Basic app imports successful")
        
        # Check SQLAlchemy functionality
        logger.info("Testing SQLAlchemy query...")
        with app.app_context():
            # Try a simple query
            products = Product.query.limit(5).all()
            logger.info(f"✓ Successfully queried products: {len(products)} found")
            
            # Try the search functionality
            search_term = "%test%"
            search_query = Product.query.filter(Product.name.like(search_term)).limit(5)
            search_results = search_query.all()
            logger.info(f"✓ Search query successful: {len(search_results)} results for 'test'")
            
            # Check if the database has the expected structure
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            logger.info(f"Database tables: {tables}")
            
            # Check Product table columns
            columns = [column['name'] for column in inspector.get_columns('product')]
            logger.info(f"Product table columns: {columns}")
            
        return True
    except Exception as e:
        logger.error(f"Error in app imports or database: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def check_template_rendering():
    """Test rendering templates to check for template errors."""
    try:
        logger.info("Checking template rendering...")
        from app import app
        from flask import render_template
        
        with app.test_request_context():
            # Try rendering a simple template
            rendered = render_template('login.html')
            logger.info("✓ Successfully rendered login.html")
            
            # Try rendering the cashier dashboard template
            try:
                rendered = render_template('cashier_dashboard.html', 
                                          products=[], 
                                          today_sales=[], 
                                          total_revenue=0,
                                          search_query='')
                logger.info("✓ Successfully rendered cashier_dashboard.html")
            except Exception as e:
                logger.error(f"Error rendering cashier_dashboard.html: {str(e)}")
                logger.error(traceback.format_exc())
        
        return True
    except Exception as e:
        logger.error(f"Error in template rendering: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def check_error_logs():
    """Check PythonAnywhere error logs."""
    try:
        logger.info("Checking for error logs...")
        error_log_path = os.path.expanduser('~/error.log')
        
        if os.path.exists(error_log_path):
            with open(error_log_path, 'r') as f:
                # Get the last 20 lines of the error log
                lines = f.readlines()
                last_lines = lines[-20:] if len(lines) > 20 else lines
                
                logger.info("Last few lines from error.log:")
                for line in last_lines:
                    logger.info(line.strip())
        else:
            logger.info("No error.log file found")
        
        return True
    except Exception as e:
        logger.error(f"Error checking error logs: {str(e)}")
        return False

def run_diagnostics():
    """Run all diagnostic checks."""
    logger.info("Starting error diagnostics...")
    
    checks = [
        check_app_imports,
        check_template_rendering,
        check_error_logs
    ]
    
    results = []
    for check in checks:
        results.append(check())
    
    if all(results):
        logger.info("All checks completed. See above for any issues.")
    else:
        logger.error("Some checks failed. See above for details.")
    
    logger.info("Error diagnostics complete.")
    logger.info("Results saved to error_check.log")

if __name__ == "__main__":
    run_diagnostics()
