#!/bin/bash
set -e

echo "==========================================="
echo "Universal Corpus Pattern API - Starting"
echo "==========================================="

# Initialize database
echo "📦 Initializing database..."
python3 -c "from database import init_db; init_db(); print('✓ Database schema ready')" || {
    echo "⚠️  Warning: Database initialization failed"
}

# Check if export file exists for restoration
EXPORT_FILE="/app/output/master_data_final.csv"
if [ -f "$EXPORT_FILE" ]; then
    echo "📂 Master data export found - restoring patterns..."
    
    # Wait a moment for database to be ready
    sleep 1
    
    # Restore patterns from export via API
    python3 restore_from_export.py 2>&1 | grep -E "^(✓|✗|=|  )" || {
        echo "⚠️  Warning: Pattern restoration failed. Starting with empty database..."
    }
    
    echo "✅ Database ready with restored data"
else
    echo "⚠️  No master data export found at $EXPORT_FILE"
    echo "   Starting with empty database"
    echo ""
    echo "   To restore patterns:"
    echo "   1. Ensure master_data_final.csv exists in /app/output/"
    echo "   2. Run: python3 restore_from_export.py"
    echo "   Or use the API to create patterns interactively"
fi

echo ""
echo "🚀 Starting FastAPI server..."
echo "==========================================="

# Start the API server
exec uvicorn api:app --host 0.0.0.0 --port 8000

