#!/bin/bash
# Quick start script for the Road Damage Detection System
# Usage: bash start.sh

echo "🚗 Starting Road Damage Detection System..."
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found at .venv"
    echo "Please run: python -m venv .venv"
    exit 1
fi

echo "✅ Virtual environment found"

# Windows specific: use .venv\Scripts\python.exe
# Unix specific: use .venv/bin/python

if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    PYTHON=".venv/Scripts/python.exe"
else
    PYTHON=".venv/bin/python"
fi

# Start backend
echo ""
echo "Starting Backend API on port 8000..."
echo "Command: $PYTHON project/backend/main.py"
echo ""

$PYTHON project/backend/main.py &
BACKEND_PID=$!

# Give backend time to start
sleep 3

echo "Backend started with PID: $BACKEND_PID"
echo ""
echo "✅ Backend is running at http://localhost:8000"
echo "✅ API documentation at http://localhost:8000/docs"
echo ""
echo "To start the frontend in another terminal:"
echo "  cd project/frontend"
echo "  npm start"
echo ""
echo "Then visit: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop the backend"
echo ""

wait $BACKEND_PID
