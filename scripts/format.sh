#!/bin/bash
# Auto-format code
set -e

echo "========================================="
echo "Universal Corpus - Code Formatter"
echo "========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "   Run: python -m venv venv && source venv/bin/activate && pip install -e .[dev]"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

echo "🎨 Formatting code with Black..."
black src/ tests/

echo ""
echo "🔧 Auto-fixing with Ruff..."
ruff check --fix src/ tests/ || true

echo ""
echo "✅ Code formatting complete!"

