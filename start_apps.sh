#!/bin/bash ./start_apps.sh

# Sailor Sheet Apps Launcher
# This script starts both the Flask app and React chatbot

echo "🚀 Starting Sailor Sheet Apps..."
echo "=================================="

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
echo "📱 Starting Flask App (Port 8000)..."
echo "------------------------------------"

# Start Flask app in background
cd apps/sailor-sheet-form
conda run -n ngo-accounting python app.py &
FLASK_PID=$!

echo "✅ Flask app started (PID: $FLASK_PID)"
echo ""

echo "🤖 Starting React Chatbot (Port 3000)..."
echo "----------------------------------------"

# Start React app in background
cd ../sailor-sheet-chat
npm start &
REACT_PID=$!

echo "✅ React chatbot started (PID: $REACT_PID)"
echo ""

echo "🎉 Both apps are starting up!"
echo "=============================="
echo "📱 Main Form: http://localhost:8000"
echo "🤖 Chatbot:   http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both apps"
echo ""

# Wait for user to stop
wait
