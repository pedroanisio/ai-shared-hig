#!/bin/bash
# Development server script for Universal Corpus Pattern API
set -e

echo "========================================="
echo "Universal Corpus - Development Server"
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

# Initialize database
echo "📦 Initializing database..."
python -c "from universal_corpus.database import init_db; init_db(); print('✓ Database ready')"

echo ""
echo "🚀 Starting development server..."
echo "   API: http://localhost:8000"
echo "   Docs: http://localhost:8000/docs"
echo "   ReDoc: http://localhost:8000/redoc"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Run with auto-reload
uvicorn universal_corpus.api:app --reload --host 0.0.0.0 --port 8000

