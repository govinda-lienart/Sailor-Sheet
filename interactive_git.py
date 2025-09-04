#!/usr/bin/env python3
"""
Interactive Git Operations
Shows a list of files and lets you select which ones to commit
"""
import os
from datetime import datetime
from git import Repo

def show_file_selection():
    """Show interactive file selection menu"""
    try:
        repo = Repo('.')
        
        print("📁 Files Available for Commit:")
        print("=" * 50)
        
        # Get all changed files
        staged_files = [item.a_path for item in repo.index.diff("HEAD")]
        unstaged_files = [item.a_path for item in repo.index.diff(None)]
        untracked_files = repo.untracked_files
        
        all_files = list(set(staged_files + unstaged_files + untracked_files))
        
        if not all_files:
            print("✅ No files to commit - working directory is clean!")
            return []
        
        # Show files with numbers
        for i, file in enumerate(sorted(all_files), 1):
            status = "🟢" if file in staged_files else "🟡" if file in unstaged_files else "🔴"
            print(f"   {i:2d}. {status} {file}")
        
        print("\n💡 Usage:")
        print("   python interactive_git.py commit 1,3,5    - Commit files 1, 3, and 5")
        print("   python interactive_git.py commit all      - Commit all files")
        print("   python interactive_git.py commit 1-5      - Commit files 1 through 5")
        
        return sorted(all_files)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def commit_selected_files(file_indices, message=None):
    """Commit selected files by their numbers"""
    try:
        repo = Repo('.')
        all_files = list(set(
            [item.a_path for item in repo.index.diff("HEAD")] +
            [item.a_path for item in repo.index.diff(None)] +
            repo.untracked_files
        ))
        
        if not all_files:
            print("✅ No files to commit!")
            return False
        
        # Parse file selection
        selected_files = []
        
        if file_indices.lower() == 'all':
            selected_files = sorted(all_files)
        else:
            # Parse comma-separated or range
            for part in file_indices.split(','):
                part = part.strip()
                if '-' in part:
                    # Range like "1-5"
                    start, end = map(int, part.split('-'))
                    for i in range(start, end + 1):
                        if 1 <= i <= len(all_files):
                            selected_files.append(sorted(all_files)[i-1])
                else:
                    # Single number
                    try:
                        i = int(part)
                        if 1 <= i <= len(all_files):
                            selected_files.append(sorted(all_files)[i-1])
                    except ValueError:
                        print(f"⚠️  Invalid number: {part}")
        
        if not selected_files:
            print("❌ No valid files selected!")
            return False
        
        # Stage selected files
        print(f"📁 Staging {len(selected_files)} files:")
        for file in selected_files:
            repo.git.add(file)
            print(f"   ✅ {file}")
        
        # Create commit message
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if not message:
            message = f'Update {len(selected_files)} files: {timestamp}'
        else:
            message = f'{message} - {timestamp}'
        
        # Commit
        commit = repo.index.commit(message)
        print(f"\n✅ Committed: {commit.hexsha[:8]} - {message}")
        
        # Push
        try:
            origin = repo.remote('origin')
            origin.push()
            print("🚀 Pushed to GitHub successfully!")
        except Exception as e:
            print(f"⚠️  Push failed: {e}")
            print("💡 You can push manually later with: git push")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "status" or command == "list":
            show_file_selection()
        elif command == "commit":
            if len(sys.argv) > 2:
                file_selection = sys.argv[2]
                message = sys.argv[3] if len(sys.argv) > 3 else None
                commit_selected_files(file_selection, message)
            else:
                print("Usage: python interactive_git.py commit <file_numbers> [message]")
                print("Example: python interactive_git.py commit 1,3,5 'Fix bugs'")
        else:
            print("Available commands:")
            print("  python interactive_git.py list          - Show files to commit")
            print("  python interactive_git.py commit 1,3,5  - Commit specific files")
            print("  python interactive_git.py commit all    - Commit all files")
    else:
        # Default: show file selection
        show_file_selection()
