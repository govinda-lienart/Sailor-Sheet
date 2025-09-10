#!/usr/bin/env python3
"""
Sailor Sheet Apps Launcher
This script starts both the Flask app and React chatbot automatically
"""

import subprocess
import sys
import os
import time
import signal
from pathlib import Path

def run_command(command, cwd=None, shell=True):
    """Run a command and return the process"""
    print(f"🚀 Running: {command}")
    return subprocess.Popen(command, cwd=cwd, shell=shell)

def main():
    print("🚀 Starting Sailor Sheet Apps...")
    print("==================================")
    
    # Get the project root directory
    project_root = Path(__file__).parent
    
    processes = []
    
    try:
        # Start Flask app
        print("\n📱 Starting Flask App (Port 8000)...")
        print("------------------------------------")
        
        flask_cmd = "conda run -n ngo-accounting python app.py"
        flask_dir = project_root / "apps" / "sailor-sheet-form"
        
        flask_process = run_command(flask_cmd, cwd=flask_dir)
        processes.append(flask_process)
        
        print("✅ Flask app started")
        
        # Wait a moment for Flask to start
        time.sleep(3)
        
        # Start React app
        print("\n🤖 Starting React Chatbot (Port 3000)...")
        print("----------------------------------------")
        
        react_cmd = "npm start"
        react_dir = project_root / "apps" / "sailor-sheet-chat"
        
        react_process = run_command(react_cmd, cwd=react_dir)
        processes.append(react_process)
        
        print("✅ React chatbot started")
        
        print("\n🎉 Both apps are running!")
        print("=========================")
        print("📱 Main Form: http://localhost:8000")
        print("🤖 Chatbot:   http://localhost:3000")
        print("\nPress Ctrl+C to stop both apps")
        
        # Wait for processes
        for process in processes:
            process.wait()
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping all apps...")
        for process in processes:
            process.terminate()
        print("✅ All apps stopped")

if __name__ == "__main__":
    main()