#!/bin/bash
# Code quality and linting script
set -e

echo "========================================="
echo "Universal Corpus - Code Quality Check"
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

echo "🔍 Running Black (code formatter)..."
black --check src/ tests/ || {
    echo "   Run: black src/ tests/ to fix formatting"
}

echo ""
echo "🔍 Running Ruff (linter)..."
ruff check src/ tests/

echo ""
echo "🔍 Running MyPy (type checker)..."
mypy src/universal_corpus/ || true

echo ""
echo "✅ Code quality check complete!"

