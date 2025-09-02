# =============================================================================
# UPDATE TIMESTAMPS - Add Version Control Comments
# Purpose: Add timestamp comments to all Python files for GitHub commits
# Version: 1.0.0 - Working Version
# Created: 2025-01-27 19:30:00
# Status: ✅ WORKING - Add timestamps to all files
# =============================================================================

import os
import glob
from datetime import datetime

# =============================================================================
# CONFIGURATION
# =============================================================================

# Files to update (Python files only)
PYTHON_FILES = [
    'app.py',
    'config.py', 
    'sheets_manager.py',
    'file_upload_manager.py'
]

# HTML files to update (templates)
HTML_FILES = [
    'templates/index.html',
    'templates/thank_you.html'
]

# =============================================================================
# TIMESTAMP FUNCTIONS
# =============================================================================

# Get Current Timestamp
# ---------------------
def get_current_timestamp():
    """Get current timestamp in the format used in your files"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Add Timestamp To Python File
# -----------------------------
def add_timestamp_to_python_file(filepath):
    """Add or update timestamp comment in a Python file"""
    try:
        # Read the file
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Check if file already has timestamp comment
        lines = content.split('\n')
        
        # Look for existing timestamp line (usually line 6)
        timestamp_found = False
        for i, line in enumerate(lines):
            if 'Created:' in line and 'Status:' in line:
                # Update existing timestamp
                current_time = get_current_timestamp()
                lines[i] = f'# Created: {current_time}'
                lines[i+1] = f'# Status: ✅ WORKING - Ready for GitHub commit'
                timestamp_found = True
                break
        
        if not timestamp_found:
            # Add new timestamp after the header
            current_time = get_current_timestamp()
            new_lines = []
            header_added = False
            
            for i, line in enumerate(lines):
                new_lines.append(line)
                
                # Add timestamp after the header block
                if line.startswith('# =============================================================================') and not header_added:
                    if i > 0 and lines[i-1].startswith('# Status:'):
                        # Update the status line
                        new_lines[i-1] = f'# Status: ✅ WORKING - Ready for GitHub commit'
                    else:
                        # Add timestamp and status
                        new_lines.append(f'# Created: {current_time}')
                        new_lines.append(f'# Status: ✅ WORKING - Ready for GitHub commit')
                    header_added = True
            
            lines = new_lines
        
        # Write back to file
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write('\n'.join(lines))
        
        print(f"✅ Updated Python: {filepath}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating {filepath}: {e}")
        return False

# Add Timestamp To HTML File
# ---------------------------
def add_timestamp_to_html_file(filepath):
    """Add or update timestamp comment in an HTML file"""
    try:
        # Read the file
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
        
        lines = content.split('\n')
        current_time = get_current_timestamp()
        
        # Look for existing HTML timestamp comment
        timestamp_found = False
        for i, line in enumerate(lines):
            if 'Updated:' in line and '<!--' in line:
                # Update existing timestamp
                lines[i] = f'<!-- Updated: {current_time} - Ready for GitHub commit -->'
                timestamp_found = True
                break
        
        if not timestamp_found:
            # Add timestamp at the beginning (after DOCTYPE if present)
            new_lines = []
            inserted = False
            
            for i, line in enumerate(lines):
                if not inserted and (line.strip().startswith('<!DOCTYPE') or line.strip().startswith('<html')):
                    new_lines.append(line)
                    new_lines.append(f'<!-- Updated: {current_time} - Ready for GitHub commit -->')
                    inserted = True
                else:
                    new_lines.append(line)
            
            # If no DOCTYPE or html tag found, add at the very beginning
            if not inserted and new_lines:
                new_lines.insert(0, f'<!-- Updated: {current_time} - Ready for GitHub commit -->')
            
            lines = new_lines
        
        # Write back to file
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write('\n'.join(lines))
        
        print(f"✅ Updated HTML: {filepath}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating {filepath}: {e}")
        return False

# Update All Files
# ----------------
def update_all_files():
    """Update timestamps in all Python and HTML files"""
    print("🚀 Updating timestamps in all Python and HTML files...")
    print("=" * 70)
    
    current_time = get_current_timestamp()
    print(f"📅 Current time: {current_time}")
    print()
    
    # Update Python files
    python_success = 0
    print("🐍 Updating Python files:")
    for filename in PYTHON_FILES:
        if os.path.exists(filename):
            if add_timestamp_to_python_file(filename):
                python_success += 1
        else:
            print(f"⚠️  Python file not found: {filename}")
    
    print()
    
    # Update HTML files
    html_success = 0
    print("🌐 Updating HTML files:")
    for filename in HTML_FILES:
        if os.path.exists(filename):
            if add_timestamp_to_html_file(filename):
                html_success += 1
        else:
            print(f"⚠️  HTML file not found: {filename}")
    
    total_success = python_success + html_success
    total_files = len(PYTHON_FILES) + len(HTML_FILES)
    
    print("\n" + "=" * 70)
    print("📊 Update Summary:")
    print(f"   🐍 Python files: {python_success}/{len(PYTHON_FILES)} updated")
    print(f"   🌐 HTML files: {html_success}/{len(HTML_FILES)} updated")
    print(f"   ✅ Total: {total_success}/{total_files} files updated")
    print(f"   📅 Timestamp: {current_time}")
    print()
    print("🎉 All files are now ready for GitHub commit!")
    print("💡 Run: git add . && git commit -m 'Update timestamps'")

# =============================================================================
# RUN THE UPDATER
# =============================================================================

if __name__ == "__main__":
    update_all_files()

