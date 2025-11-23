#!/bin/bash
# Test runner script for Universal Corpus Pattern API
set -e

echo "========================================="
echo "Universal Corpus - Test Suite"
echo "========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "   Run: python -m venv venv && source venv/bin/activate && pip install -e .[dev,test]"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Run tests with coverage
echo "🧪 Running tests with coverage..."
pytest tests/ -v --cov=universal_corpus --cov-report=term-missing --cov-report=html

echo ""
echo "✅ Tests complete!"
echo "   Coverage report: htmlcov/index.html"

