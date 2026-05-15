#!/bin/bash

# Quick setup script for the project

echo "🚀 AI Smart Road Damage Detection - Setup Script"
echo "================================================="

# Check dependencies
echo ""
echo "Checking dependencies..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.10+"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo "⚠️  Docker not found. Using local Python environment"
    DOCKER_AVAILABLE=false
else
    echo "✓ Docker found"
    DOCKER_AVAILABLE=true
fi

echo "✓ All checks passed"

# Create output directories
echo ""
echo "Creating output directories..."
mkdir -p outputs/models outputs/weights outputs/analysis
mkdir -p logs
mkdir -p frontend/node_modules

echo "✓ Directories created"

# Download YOLOv8 model
echo ""
echo "Downloading YOLOv8 Nano model..."
python3 -c "from ultralytics import YOLO; YOLO('yolov8n.pt')" 2>&1 | tail -1

echo "✓ Model downloaded"

# Install backend dependencies
if [ "$DOCKER_AVAILABLE" = false ]; then
    echo ""
    echo "Installing Python dependencies..."
    cd backend
    python3 -m pip install -q -r ../requirements.txt
    cd ..
    echo "✓ Dependencies installed"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
if [ "$DOCKER_AVAILABLE" = true ]; then
    echo "1. Run: docker-compose up --build"
else
    echo "1. Backend: cd backend && python -m uvicorn main:app --reload"
    echo "2. Frontend: cd frontend && npm install && npm start"
fi

echo ""
echo "📖 Documentation: See README.md"
