# Created: 2025-09-04 16:37:37
# Status: ✅ WORKING - Ready for GitHub commit
# Purpose: Add timestamp comments to all Python files for GitHub commits
# Version: 1.0.0 - Working Version
# =============================================================================

import os
import glob
from datetime import datetime

# =============================================================================
# CONFIGURATION
# =============================================================================

# Files and directories to EXCLUDE from timestamp updates
EXCLUDED_FILES = {
    '.env',
    '.gitignore',
    'requirements.txt'  # Usually don't need timestamps in requirements
}

EXCLUDED_DIRECTORIES = {
    'Debug',
    'Context',
    '.git',
    '__pycache__',
    '.pytest_cache',
    'node_modules'
}

# File extensions we can handle (text files only)
SUPPORTED_EXTENSIONS = {
    '.py': 'python',
    '.html': 'html',
    '.htm': 'html',
    '.json': 'json',
    '.css': 'css',
    '.js': 'javascript',
    '.md': 'markdown',
    '.txt': 'text'
}

# Binary file extensions to skip (but log)
BINARY_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.svg',  # Images
    '.pdf', '.doc', '.docx', '.xls', '.xlsx',  # Documents
    '.zip', '.tar', '.gz', '.rar',  # Archives
    '.exe', '.dll', '.so', '.dylib',  # Executables
    '.mp3', '.mp4', '.avi', '.mov', '.wav',  # Media
    '.ttf', '.otf', '.woff', '.woff2'  # Fonts
}

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
        
        # Look for existing timestamp lines
        timestamp_found = False
        current_time = get_current_timestamp()
        
        # Find and replace all existing timestamp lines
        for i, line in enumerate(lines):
            if line.strip().startswith('# Created:') and 'Status:' not in line:
                # Found a Created line, update it
                lines[i] = f'# Created: {current_time}'
                # Look for the next Status line and update it too
                for j in range(i+1, min(i+3, len(lines))):
                    if lines[j].strip().startswith('# Status:'):
                        lines[j] = f'# Status: ✅ WORKING - Ready for GitHub commit'
                        break
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

# Add Timestamp To JSON File
# ---------------------------
def add_timestamp_to_json_file(filepath):
    """Add or update timestamp comment in a JSON file"""
    try:
        import json
        
        # Read the JSON file
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Parse JSON to add metadata
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            print(f"⚠️  Invalid JSON in {filepath}, skipping timestamp update")
            return False
        
        # Add or update timestamp metadata
        current_time = get_current_timestamp()
        data['_metadata'] = {
            'updated': current_time,
            'status': 'Ready for GitHub commit',
            'version': '1.0.0'
        }
        
        # Write back to file with proper formatting
        with open(filepath, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
        
        print(f"✅ Updated JSON: {filepath}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating {filepath}: {e}")
        return False

# Add Timestamp To CSS File
# --------------------------
def add_timestamp_to_css_file(filepath):
    """Add or update timestamp comment in a CSS file"""
    try:
        # Read the file
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
        
        lines = content.split('\n')
        current_time = get_current_timestamp()
        
        # Look for existing CSS timestamp comment
        timestamp_found = False
        for i, line in enumerate(lines):
            if 'Updated:' in line and '/*' in line and '*/' in line:
                # Update existing timestamp
                lines[i] = f'/* Updated: {current_time} - Ready for GitHub commit */'
                timestamp_found = True
                break
        
        if not timestamp_found:
            # Add timestamp at the beginning
            timestamp_comment = f'/* Updated: {current_time} - Ready for GitHub commit */'
            lines.insert(0, timestamp_comment)
            lines.insert(1, '')  # Add empty line for readability
        
        # Write back to file
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write('\n'.join(lines))
        
        print(f"✅ Updated CSS: {filepath}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating {filepath}: {e}")
        return False

# Add Timestamp To JS File
# -------------------------
def add_timestamp_to_js_file(filepath):
    """Add or update timestamp comment in a JavaScript file"""
    try:
        # Read the file
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
        
        lines = content.split('\n')
        current_time = get_current_timestamp()
        
        # Look for existing JS timestamp comment
        timestamp_found = False
        for i, line in enumerate(lines):
            if 'Updated:' in line and ('//' in line or '/*' in line):
                # Update existing timestamp
                if '//' in line:
                    lines[i] = f'// Updated: {current_time} - Ready for GitHub commit'
                else:
                    lines[i] = f'/* Updated: {current_time} - Ready for GitHub commit */'
                timestamp_found = True
                break
        
        if not timestamp_found:
            # Add timestamp at the beginning
            timestamp_comment = f'// Updated: {current_time} - Ready for GitHub commit'
            lines.insert(0, timestamp_comment)
            lines.insert(1, '')  # Add empty line for readability
        
        # Write back to file
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write('\n'.join(lines))
        
        print(f"✅ Updated JS: {filepath}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating {filepath}: {e}")
        return False

# Add Timestamp To Markdown File
# -------------------------------
def add_timestamp_to_markdown_file(filepath):
    """Add or update timestamp comment in a Markdown file"""
    try:
        # Read the file
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
        
        lines = content.split('\n')
        current_time = get_current_timestamp()
        
        # Look for existing markdown timestamp comment
        timestamp_found = False
        for i, line in enumerate(lines):
            if 'Updated:' in line and ('<!--' in line or line.startswith('>')):
                # Update existing timestamp
                if '<!--' in line:
                    lines[i] = f'<!-- Updated: {current_time} - Ready for GitHub commit -->'
                else:
                    lines[i] = f'> Updated: {current_time} - Ready for GitHub commit'
                timestamp_found = True
                break
        
        if not timestamp_found:
            # Add timestamp at the beginning
            timestamp_comment = f'<!-- Updated: {current_time} - Ready for GitHub commit -->'
            lines.insert(0, timestamp_comment)
            lines.insert(1, '')  # Add empty line for readability
        
        # Write back to file
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write('\n'.join(lines))
        
        print(f"✅ Updated Markdown: {filepath}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating {filepath}: {e}")
        return False

# Add Timestamp To Text File
# ---------------------------
def add_timestamp_to_text_file(filepath):
    """Add or update timestamp comment in a text file"""
    try:
        # Read the file
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
        
        lines = content.split('\n')
        current_time = get_current_timestamp()
        
        # Look for existing text timestamp comment
        timestamp_found = False
        for i, line in enumerate(lines):
            if 'Updated:' in line and ('#' in line or line.startswith('//') or line.startswith('--')):
                # Update existing timestamp
                lines[i] = f'# Updated: {current_time} - Ready for GitHub commit'
                timestamp_found = True
                break
        
        if not timestamp_found:
            # Add timestamp at the beginning
            timestamp_comment = f'# Updated: {current_time} - Ready for GitHub commit'
            lines.insert(0, timestamp_comment)
            lines.insert(1, '')  # Add empty line for readability
        
        # Write back to file
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write('\n'.join(lines))
        
        print(f"✅ Updated Text: {filepath}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating {filepath}: {e}")
        return False

# Find All Files To Update
# -------------------------
def find_all_files():
    """Find all files in the project that should be updated with timestamps"""
    files_to_update = []
    binary_files_found = []
    unsupported_files = []
    
    # Walk through all files and directories
    for root, dirs, files in os.walk('.'):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRECTORIES]
        
        # Skip files in excluded directories (additional check)
        if any(excluded_dir in root for excluded_dir in EXCLUDED_DIRECTORIES):
            continue
            
        for file in files:
            # Skip excluded files
            if file in EXCLUDED_FILES:
                continue
            
            # Get file extension
            file_ext = os.path.splitext(file)[1].lower()
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, '.')
            
            if file_ext in SUPPORTED_EXTENSIONS:
                # Text file we can update
                files_to_update.append((rel_path, SUPPORTED_EXTENSIONS[file_ext]))
            elif file_ext in BINARY_EXTENSIONS:
                # Binary file to skip but log
                binary_files_found.append(rel_path)
            elif file_ext:  # Has extension but not supported
                unsupported_files.append(rel_path)
            # Files without extensions are ignored silently
    
    return sorted(files_to_update), sorted(binary_files_found), sorted(unsupported_files)

# Update File By Type
# -------------------
def update_file_by_type(filepath, file_type):
    """Update a file with timestamp based on its type"""
    try:
        if file_type == 'python':
            return add_timestamp_to_python_file(filepath)
        elif file_type == 'html':
            return add_timestamp_to_html_file(filepath)
        elif file_type == 'json':
            return add_timestamp_to_json_file(filepath)
        elif file_type == 'css':
            return add_timestamp_to_css_file(filepath)
        elif file_type == 'javascript':
            return add_timestamp_to_js_file(filepath)
        elif file_type == 'markdown':
            return add_timestamp_to_markdown_file(filepath)
        elif file_type == 'text':
            return add_timestamp_to_text_file(filepath)
        else:
            print(f"⚠️  Unsupported file type: {file_type} for {filepath}")
            return False
    except Exception as e:
        print(f"❌ Error updating {filepath}: {e}")
        return False

# Update All Files
# ----------------
def update_all_files():
    """Automatically find and update ALL files in the project with timestamps"""
    print("🚀 Auto-discovering and updating ALL project files with timestamps...")
    print("=" * 80)
    
    current_time = get_current_timestamp()
    print(f"📅 Current time: {current_time}")
    print()
    
    # Find all files to update
    print("🔍 Scanning project for files to update...")
    files_to_update, binary_files, unsupported_files = find_all_files()
    
    print(f"📁 Found {len(files_to_update)} text files to update")
    if binary_files:
        print(f"🖼️  Found {len(binary_files)} binary files (images, etc.) - skipped")
    if unsupported_files:
        print(f"❓ Found {len(unsupported_files)} unsupported file types - skipped")
    print()
    
    if not files_to_update:
        print("⚠️  No supported text files found to update!")
        if binary_files or unsupported_files:
            print("💡 Note: Binary and unsupported files were found but skipped")
        return
    
    # Group files by type for organized output
    files_by_type = {}
    for filepath, file_type in files_to_update:
        if file_type not in files_by_type:
            files_by_type[file_type] = []
        files_by_type[file_type].append(filepath)
    
    # Update files by type
    total_success = 0
    updated_files = []
    
    type_icons = {
        'python': '🐍',
        'html': '🌐', 
        'json': '📄',
        'css': '🎨',
        'javascript': '⚡',
        'markdown': '📝',
        'text': '📃'
    }
    
    for file_type in sorted(files_by_type.keys()):
        files = files_by_type[file_type]
        icon = type_icons.get(file_type, '📄')
        print(f"{icon} Updating {file_type.title()} files ({len(files)} found):")
        
        type_success = 0
        for filepath in files:
            if update_file_by_type(filepath, file_type):
                type_success += 1
                updated_files.append(filepath)
            
        print(f"   ✅ {type_success}/{len(files)} {file_type} files updated")
        print()
        total_success += type_success
    
    # Final summary
    print("=" * 80)
    print("📊 FINAL SUMMARY:")
    print(f"   ✅ Successfully updated: {total_success}/{len(files_to_update)} files")
    print(f"   📅 Timestamp applied: {current_time}")
    print()
    
    # List all updated files
    if updated_files:
        print("📋 FILES UPDATED WITH TIMESTAMPS:")
        print("-" * 40)
        for i, filepath in enumerate(sorted(updated_files), 1):
            file_ext = os.path.splitext(filepath)[1]
            file_type = SUPPORTED_EXTENSIONS.get(file_ext, 'unknown')
            icon = type_icons.get(file_type, '📄')
            print(f"   {i:2d}. {icon} {filepath}")
        print()
    
    # Show binary files that were skipped
    if binary_files:
        print("🖼️  BINARY FILES FOUND (SKIPPED - NO TIMESTAMPS NEEDED):")
        print("-" * 50)
        for i, filepath in enumerate(sorted(binary_files), 1):
            file_ext = os.path.splitext(filepath)[1].lower()
            if file_ext in {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.svg'}:
                icon = '🖼️'
            elif file_ext in {'.pdf', '.doc', '.docx'}:
                icon = '📄'
            elif file_ext in {'.zip', '.tar', '.gz', '.rar'}:
                icon = '📦'
            else:
                icon = '📁'
            print(f"   {i:2d}. {icon} {filepath}")
        print()
    
    # Show unsupported files
    if unsupported_files:
        print("❓ UNSUPPORTED FILE TYPES (SKIPPED):")
        print("-" * 35)
        for i, filepath in enumerate(sorted(unsupported_files), 1):
            print(f"   {i:2d}. ❓ {filepath}")
        print()
    
    if total_success > 0:
        print("🎉 All files are now timestamped and ready for GitHub commit!")
        print("💡 Run: git add . && git commit -m 'Update all file timestamps'")
    else:
        print("⚠️  No files were successfully updated!")
    
    print("=" * 80)

# =============================================================================
# RUN THE UPDATER
# =============================================================================

if __name__ == "__main__":
    update_all_files()

