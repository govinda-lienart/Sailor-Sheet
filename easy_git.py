# COMMANDS

# python easy_git.py stage --force app.py config.py sheets_manager.py file_upload_manager.py templates/index.html templates/thank_you.html static/css/style.css data/

#one

#!/usr/bin/env python3
"""
Easy Git Operations with Python
Simple script to stage, commit, and push files with timestamps
"""
import os
from datetime import datetime
from git import Repo

def easy_commit(message=None, push=True):
    """
    Easy commit function with automatic timestamping
    
    Args:
        message: Custom commit message (optional)
        push: Whether to push to GitHub (default: True)
    """
    try:
        # Initialize repository
        repo = Repo('.')
        
        # Get current timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Check if there are any changes
        if repo.is_dirty(untracked_files=True):
            # Stage all changes
            repo.git.add('.')
            
            # Create commit message
            if not message:
                message = f'Update: {timestamp}'
            else:
                message = f'{message} - {timestamp}'
            
            # Commit changes
            commit = repo.index.commit(message)
            print(f"✅ Committed: {commit.hexsha[:8]} - {message}")
            
            # Push to GitHub if requested
            if push:
                try:
                    origin = repo.remote('origin')
                    origin.push()
                    print("🚀 Pushed to GitHub successfully!")
                except Exception as e:
                    print(f"⚠️  Push failed: {e}")
                    print("💡 You can push manually later with: git push")
            
            return True
        else:
            print("ℹ️  No changes to commit")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def stage_files(file_patterns, force=False):
    """
    Stage specific files or patterns
    
    Args:
        file_patterns: List of file paths or patterns
        force: If True, stage files even if they have no changes
    """
    try:
        repo = Repo('.')
        
        for pattern in file_patterns:
            if force:
                # Force stage files even if no changes
                repo.git.add(pattern, force=True)
                print(f"📁 Force staged: {pattern}")
            else:
                # Normal staging (only files with changes)
                repo.git.add(pattern)
                print(f"📁 Staged: {pattern}")
        
        print("✅ Files staged successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error staging files: {e}")
        return False

def show_status():
    """Show current Git status"""
    try:
        repo = Repo('.')
        
        print("📊 Git Status:")
        print("-" * 40)
        
        # Show staged files
        staged = repo.index.diff("HEAD")
        if staged:
            print("🟢 Staged files:")
            for item in staged:
                print(f"   + {item.a_path}")
        
        # Show unstaged files
        unstaged = repo.index.diff(None)
        if unstaged:
            print("🟡 Modified files:")
            for item in unstaged:
                print(f"   ~ {item.a_path}")
        
        # Show untracked files
        untracked = repo.untracked_files
        if untracked:
            print("🔴 Untracked files:")
            for file in untracked:
                print(f"   ? {file}")
        
        if not staged and not unstaged and not untracked:
            print("✅ Working directory clean")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "status":
            show_status()
        elif command == "stage":
            if len(sys.argv) > 2:
                # Check for --force option
                force = False
                files = []
                
                for arg in sys.argv[2:]:
                    if arg == "--force":
                        force = True
                    else:
                        files.append(arg)
                
                if files:
                    stage_files(files, force=force)
                else:
                    print("Usage: python easy_git.py stage [--force] file1 file2 ...")
            else:
                print("Usage: python easy_git.py stage [--force] file1 file2 ...")
        elif command == "commit":
            message = sys.argv[2] if len(sys.argv) > 2 else None
            easy_commit(message)
        else:
            print("Available commands:")
            print("  python easy_git.py status          - Show Git status")
            print("  python easy_git.py stage file1     - Stage specific files")
            print("  python easy_git.py stage --force file1 - Force stage files (even without changes)")
            print("  python easy_git.py commit [msg]    - Commit with message")
    else:
        # Default: show status and ask what to do
        show_status()
        print("\n💡 Usage examples:")
        print("  python easy_git.py commit 'Fix bug'   - Commit with message")
        print("  python easy_git.py stage app.py       - Stage specific file")
        print("  python easy_git.py stage --force data/ - Force stage directory (even without changes)")
        print("  python easy_git.py status             - Show current status")
