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
    'file_upload_manager.py',
    'drive_test.py',
    'list_folders.py'
]

# =============================================================================
# TIMESTAMP FUNCTIONS
# =============================================================================

def get_current_timestamp():
    """Get current timestamp in the format used in your files"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def add_timestamp_to_file(filepath):
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
        
        print(f"✅ Updated: {filepath}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating {filepath}: {e}")
        return False

def update_all_files():
    """Update timestamps in all Python files"""
    print("🚀 Updating timestamps in all Python files...")
    print("=" * 60)
    
    current_time = get_current_timestamp()
    print(f"📅 Current time: {current_time}")
    print()
    
    success_count = 0
    total_count = len(PYTHON_FILES)
    
    for filename in PYTHON_FILES:
        if os.path.exists(filename):
            if add_timestamp_to_file(filename):
                success_count += 1
        else:
            print(f"⚠️  File not found: {filename}")
    
    print("\n" + "=" * 60)
    print("📊 Update Summary:")
    print(f"   ✅ Successfully updated: {success_count}/{total_count} files")
    print(f"   📅 Timestamp: {current_time}")
    print()
    print("🎉 All files are now ready for GitHub commit!")
    print("💡 Run: git add . && git commit -m 'Update timestamps'")

# =============================================================================
# RUN THE UPDATER
# =============================================================================

if __name__ == "__main__":
    update_all_files()
