import os
import polib

def compile_translations():
    """Compile .po files to .mo files for use with Flask-Babel."""
    print("Compiling translation files...")
    
    # Path to the locale directory
    locale_dir = os.path.join(os.path.dirname(__file__), 'locale')
    
    # Walk through all subdirectories
    for root, dirs, files in os.walk(locale_dir):
        for file in files:
            if file.endswith('.po'):
                po_file = os.path.join(root, file)
                mo_file = os.path.splitext(po_file)[0] + '.mo'
                
                print(f"Compiling {po_file} to {mo_file}")
                
                try:
                    po = polib.pofile(po_file)
                    po.save_as_mofile(mo_file)
                    print(f"Successfully compiled {mo_file}")
                except Exception as e:
                    print(f"Error compiling {po_file}: {e}")

if __name__ == "__main__":
    compile_translations()
    print("Translation compilation complete.")
