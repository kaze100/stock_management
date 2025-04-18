# Smart Inventory System - Deployment Guide

This guide provides step-by-step instructions for deploying the Smart Inventory System to PythonAnywhere.

## Prerequisites

- A PythonAnywhere account (free tier is sufficient for testing)
- Your Smart Inventory System code (already prepared with wsgi.py and updated requirements.txt)

## Deployment Steps

### 1. Sign Up for PythonAnywhere

1. Go to [PythonAnywhere.com](https://www.pythonanywhere.com/)
2. Create a new account or log in to your existing account

### 2. Create a New Web App

1. Once logged in, navigate to the **Web** tab
2. Click on **Add a new web app**
3. Choose your domain name (e.g., yourusername.pythonanywhere.com)
4. Select **Flask** as your web framework
5. Choose **Python 3.10** (or the latest available version)
6. Select **Flask** for the project type

### 3. Upload Your Files

1. Go to the **Files** tab in PythonAnywhere
2. Use your existing project directory:
   ```
   /home/renoir0/SmartInventory
   ```
3. Upload your project files:
   - Navigate to your directory
   - Click **Upload a file** for each file, or
   - Use the Bash console to upload multiple files

### 4. Set Up Your Virtual Environment

1. Go to the **Consoles** tab
2. Start a new **Bash console**
3. Navigate to your project directory:
   ```bash
   cd ~/SmartInventory
   ```
4. Your virtual environment is already set up as:
   ```bash
   smartinventory-env
   ```
5. Activate the virtual environment (if not already activated):
   ```bash
   workon smartinventory-env
   ```
6. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

### 5. Initialize Your Database

1. In the Bash console, with your virtual environment activated, run:
   ```bash
   python init_db.py
   ```
2. This will create the database tables and set up the default admin user

### 6. Configure the WSGI File

1. Go back to the **Web** tab
2. Click on the WSGI configuration file link (e.g., `/var/www/renoir0_pythonanywhere_com_wsgi.py`)
3. Replace the content with:
   ```python
   import sys
   import os
   
   # Add your project directory to the path
   path = '/home/renoir0/SmartInventory'
   if path not in sys.path:
       sys.path.append(path)
   
   # Set environment variables
   os.environ['FLASK_APP'] = 'app.py'
   
   # Import your app
   from app import app as application
   ```
4. Click **Save**

### 7. Configure Static Files

1. In the **Web** tab, under "Static files"
2. Add a new mapping:
   - URL: `/static/`
   - Directory: `/home/renoir0/SmartInventory/static/`
3. Click **Save**

### 8. Configure Virtual Environment

1. In the **Web** tab, under "Virtualenv"
2. Enter the path to your virtual environment:
   ```
   /home/renoir0/.virtualenvs/smartinventory-env
   ```
3. Click **Save**

### 9. Reload Your Web App

1. Click the **Reload** button for your web app
2. Wait for the reload to complete

### 10. Access Your Application

1. Click on the link to your web app (e.g., renoir0.pythonanywhere.com)
2. Log in with the default admin credentials:
   - Username: `renoir01`
   - Password: `Renoir@654`

## Troubleshooting

If you encounter any issues:

1. Check the **Error log** in the Web tab
2. Make sure all required packages are installed in your virtual environment
3. Verify that the paths in your WSGI file are correct
4. Ensure your database was initialized properly

## Security Considerations

1. Change the default admin password after your first login
2. Consider setting up environment variables for sensitive information
3. Regularly back up your database

## Maintenance

1. To update your application, upload the new files and reload the web app
2. For database changes, you may need to run migration scripts
3. Monitor your application's resource usage in the PythonAnywhere dashboard

---

For more information, refer to the [PythonAnywhere documentation](https://help.pythonanywhere.com/pages/Flask/).
