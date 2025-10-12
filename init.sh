#!/bin/bash

# JLPT Test Manager - Initialization Script

echo "🎌 JLPT Test Manager - Setup Script"
echo "===================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

echo ""
echo "🔄 Activating virtual environment..."
source venv/bin/activate

echo ""
echo "📥 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "🗄️  Initializing database..."
flask init-db

echo ""
echo "===================================="
echo "✨ Setup complete!"
echo ""
echo "To create an admin user, run:"
echo "  source venv/bin/activate"
echo "  flask create-admin"
echo ""
echo "To start the application, run:"
echo "  source venv/bin/activate"
echo "  flask run"
echo ""
echo "Then visit: http://localhost:5000"
echo "===================================="

