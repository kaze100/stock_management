#!/usr/bin/env python3
"""
Script to compile .po translation files to .mo files
"""
import os
import subprocess
import sys
import polib

def compile_po_files():
    """Compile all .po files to .mo files using polib."""
    print("Compiling translation files...")
    
    # Path to the locale directory
    locale_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'locale')
    
    if not os.path.exists(locale_dir):
        print(f"Error: Locale directory not found at {locale_dir}")
        return False
    
    success = True
    
    # Try using polib first (pure Python solution)
    try:
        for root, dirs, files in os.walk(locale_dir):
            for file in files:
                if file.endswith('.po'):
                    po_path = os.path.join(root, file)
                    mo_path = po_path.replace('.po', '.mo')
                    
                    try:
                        print(f"Compiling {po_path} to {mo_path}")
                        po = polib.pofile(po_path)
                        po.save_as_mofile(mo_path)
                        print(f"Successfully compiled {po_path}")
                    except Exception as e:
                        print(f"Error compiling {po_path}: {str(e)}")
                        success = False
        
        if success:
            print("All translation files compiled successfully using polib!")
            return True
    except ImportError:
        print("polib not found, trying alternative method...")
    
    # If polib is not available or failed, try using msgfmt command
    try:
        for root, dirs, files in os.walk(locale_dir):
            for file in files:
                if file.endswith('.po'):
                    po_path = os.path.join(root, file)
                    mo_dir = os.path.dirname(po_path)
                    mo_path = os.path.join(mo_dir, os.path.splitext(file)[0] + '.mo')
                    
                    try:
                        print(f"Compiling {po_path} to {mo_path} using msgfmt")
                        subprocess.run(['msgfmt', po_path, '-o', mo_path], check=True)
                        print(f"Successfully compiled {po_path}")
                    except subprocess.CalledProcessError as e:
                        print(f"Error compiling {po_path}: {str(e)}")
                        success = False
                    except FileNotFoundError:
                        print("msgfmt command not found. Please install gettext tools.")
                        return False
        
        if success:
            print("All translation files compiled successfully using msgfmt!")
            return True
    except Exception as e:
        print(f"Error during compilation: {str(e)}")
    
    return False

if __name__ == "__main__":
    if not compile_po_files():
        sys.exit(1)
    sys.exit(0)
