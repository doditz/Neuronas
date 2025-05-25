
#!/usr/bin/env python3
import os
import re

# License header for Python files
PYTHON_LICENSE_HEADER = '''"""
This work is licensed under CC BY-NC 4.0 International.
Commercial use requires prior written consent and compensation.
Contact: sebastienbrulotte@gmail.com
Attribution: Sebastien Brulotte aka [ Doditz ]

This document is part of the NEURONAS cognitive system.
Core modules referenced: BRONAS (Ethical Reflex Filter) and QRONAS (Probabilistic Symbolic Vector Engine).
All outputs are subject to integrity validation and ethical compliance enforced by BRONAS.
"""

'''

# License footer for HTML files
HTML_LICENSE_FOOTER = '''
<!-- 
This work is licensed under CC BY-NC 4.0 International.
Commercial use requires prior written consent and compensation.
Contact: sebastienbrulotte@gmail.com
Attribution: Sebastien Brulotte aka [ Doditz ]

This document is part of the NEURONAS cognitive system.
Core modules referenced: BRONAS (Ethical Reflex Filter) and QRONAS (Probabilistic Symbolic Vector Engine).
All outputs are subject to integrity validation and ethical compliance enforced by BRONAS.
-->
'''

# License header for JS/CSS files
JS_CSS_LICENSE_HEADER = '''/**
 * This work is licensed under CC BY-NC 4.0 International.
 * Commercial use requires prior written consent and compensation.
 * Contact: sebastienbrulotte@gmail.com
 * Attribution: Sebastien Brulotte aka [ Doditz ]
 *
 * This document is part of the NEURONAS cognitive system.
 * Core modules referenced: BRONAS (Ethical Reflex Filter) and QRONAS (Probabilistic Symbolic Vector Engine).
 * All outputs are subject to integrity validation and ethical compliance enforced by BRONAS.
 */

'''

def has_license(content, file_type):
    """Check if the file already has a license header/footer"""
    if file_type == 'py':
        return 'This work is licensed under CC BY-NC 4.0 International' in content
    elif file_type == 'html':
        return 'This work is licensed under CC BY-NC 4.0 International' in content
    elif file_type in ['js', 'css']:
        return 'This work is licensed under CC BY-NC 4.0 International' in content
    return False

def add_python_license(file_path):
    """Add license header to Python files"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if has_license(content, 'py'):
        print(f"License already present in {file_path}")
        return
    
    # Check if there's a shebang or encoding comment at the top
    lines = content.split('\n')
    insert_at = 0
    
    if lines and (lines[0].startswith('#!') or lines[0].startswith('# -*- coding')):
        insert_at = 1
        while insert_at < len(lines) and (not lines[insert_at].strip() or lines[insert_at].startswith('#')):
            insert_at += 1
        
        new_content = '\n'.join(lines[:insert_at]) + '\n' + PYTHON_LICENSE_HEADER + '\n'.join(lines[insert_at:])
    else:
        new_content = PYTHON_LICENSE_HEADER + content
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Added license header to {file_path}")

def add_html_license(file_path):
    """Add license footer to HTML files"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if has_license(content, 'html'):
        print(f"License already present in {file_path}")
        return
    
    # Insert before closing body or html tag
    if '</body>' in content:
        new_content = content.replace('</body>', HTML_LICENSE_FOOTER + '\n</body>')
    elif '</html>' in content:
        new_content = content.replace('</html>', HTML_LICENSE_FOOTER + '\n</html>')
    else:
        new_content = content + '\n' + HTML_LICENSE_FOOTER
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Added license footer to {file_path}")

def add_js_css_license(file_path, file_type):
    """Add license header to JS/CSS files"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if has_license(content, file_type):
        print(f"License already present in {file_path}")
        return
    
    new_content = JS_CSS_LICENSE_HEADER + content
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Added license header to {file_path}")

def process_directory(directory):
    """Process all files in a directory recursively"""
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            
            # Skip files in .git directory and non-text files
            if '.git' in file_path:
                continue
                
            # Process based on file extension
            if file.endswith('.py'):
                add_python_license(file_path)
            elif file.endswith('.html'):
                add_html_license(file_path)
            elif file.endswith('.js'):
                add_js_css_license(file_path, 'js')
            elif file.endswith('.css'):
                add_js_css_license(file_path, 'css')

if __name__ == "__main__":
    # Process main directories
    print("Adding license headers to files...")
    
    # Process Python files in the root directory
    for file in os.listdir('.'):
        if file.endswith('.py'):
            add_python_license(os.path.join('.', file))
    
    # Process subdirectories
    process_directory('core_modules')
    process_directory('templates')
    process_directory('static')
    
    print("License headers added successfully!")
