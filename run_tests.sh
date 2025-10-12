#!/bin/bash

# JLPT Test Manager - Test Runner Script

echo "🧪 JLPT Test Manager - Test Suite"
echo "=================================="
echo ""

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
elif command -v pyenv &> /dev/null; then
    pyenv activate nihongo 2>/dev/null || true
fi

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "📦 Installing test dependencies..."
    pip install -r requirements-dev.txt
fi

echo ""
echo "Running tests..."
echo ""

# Run tests based on argument
case "$1" in
    "models")
        echo "🗄️  Running model tests..."
        pytest tests/test_models.py -v
        ;;
    "routes")
        echo "🛣️  Running route tests..."
        pytest tests/test_routes.py -v
        ;;
    "import")
        echo "📥 Running import tests..."
        pytest tests/test_import.py -v -m exam_import
        ;;
    "admin")
        echo "⚙️  Running admin tests..."
        pytest tests/test_admin.py -v
        ;;
    "integration")
        echo "🔗 Running integration tests..."
        pytest tests/test_integration.py -v
        ;;
    "coverage")
        echo "📊 Running tests with coverage..."
        pytest tests/ --cov=. --cov-report=html --cov-report=term
        echo ""
        echo "Coverage report generated in htmlcov/index.html"
        ;;
    "fast")
        echo "⚡ Running fast tests (no integration)..."
        pytest tests/ -v -m "not integration"
        ;;
    *)
        echo "🎯 Running all tests..."
        pytest tests/ -v
        ;;
esac

echo ""
echo "=================================="
echo "✅ Tests completed!"

