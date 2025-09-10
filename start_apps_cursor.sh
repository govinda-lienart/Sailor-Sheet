#!/bin/bash

# Sailor Sheet Apps Launcher for Cursor
# This script opens both apps in separate Cursor terminals

echo "🚀 Starting Sailor Sheet Apps in Cursor..."
echo "=========================================="

# Get the current directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "📁 Project directory: $PROJECT_DIR"
echo ""

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if conda is available
if command_exists conda; then
    echo "✅ Conda found"
else
    echo "❌ Conda not found. Please install Anaconda/Miniconda first."
    exit 1
fi

# Check if npm is available
if command_exists npm; then
    echo "✅ npm found"
else
    echo "❌ npm not found. Please install Node.js first."
    exit 1
fi

echo ""
echo "📱 Opening Flask App (Port 8000) in new terminal..."
echo "---------------------------------------------------"

# Open Flask app in new Cursor terminal
cursor --new-window --command "cd '$PROJECT_DIR/apps/sailor-sheet-form' && conda activate ngo-accounting && python app.py"

echo "✅ Flask app terminal opened"
echo ""

echo "🤖 Opening React Chatbot (Port 3000) in new terminal..."
echo "-------------------------------------------------------"

# Open React app in new Cursor terminal
cursor --new-window --command "cd '$PROJECT_DIR/apps/sailor-sheet-chat' && npm start"

echo "✅ React chatbot terminal opened"
echo ""

echo "🎉 Both apps are starting in separate terminals!"
echo "==============================================="
echo "📱 Main Form: http://localhost:8000"
echo "🤖 Chatbot:   http://localhost:3000"
echo ""
echo "Each app is running in its own terminal window"
echo "You can see the output and stop each app independently"
