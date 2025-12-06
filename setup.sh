#!/bin/bash
# Setup script for YiriAi production deployment

set -e

echo "🚀 YiriAi Production Setup"
echo "=========================="

# Check Python version
python_version=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo "✓ Dependencies installed"

# Check for .env file
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your configuration"
else
    echo "✓ .env file exists"
fi

# Check if Docker is available for database services
if command -v docker &> /dev/null; then
    echo ""
    echo "Docker detected. You can run database services with:"
    echo "  docker-compose up -d"
else
    echo ""
    echo "⚠️  Docker not found. Install Docker to run database services easily."
fi

echo ""
echo "Setup complete! Next steps:"
echo ""
echo "1. Edit .env file with your configuration"
echo "2. Start database services (PostgreSQL and Redis)"
echo "   - Using Docker: docker-compose up -d"
echo "   - Or install locally"
echo "3. Initialize database: python init_db.py"
echo "4. Start the application: python main.py"
echo ""
echo "For development with auto-reload:"
echo "  uvicorn main:app --reload --host 0.0.0.0 --port 8000"
echo ""
