#!/usr/bin/env python3
"""
Fix syntax error in ui/pages.py by adding missing closing parenthesis.
"""

import os
import re

def fix_syntax_error():
    # Path to the file with the syntax error
    file_path = 'ui/pages.py'
    
    # Read the file content
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Look for the problematic section (Study Tips section in practice area)
    pattern = r'(<div style="background-color: #e3f2fd;.*?Review your incorrect answers to learn from mistakes.*?</ul>\s*</div>\s*)'
    
    # Replace with the corrected version (add missing closing parenthesis)
    fixed_content = re.sub(pattern, r'\1""", unsafe_allow_html=True)\n\n    # Completed Quizzes Section', content, flags=re.DOTALL)
    
    # Write the corrected content back to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(fixed_content)
    
    print(f"Fixed syntax error in {file_path}")

if __name__ == "__main__":
    fix_syntax_error() 