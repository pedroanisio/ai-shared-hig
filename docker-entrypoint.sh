#!/bin/bash
set -e

echo "==========================================="
echo "Universal Corpus Pattern API - Starting"
echo "==========================================="

# Initialize database
echo "📦 Initializing database..."
python3 init_db.py

# Check if CSV data exists
CSV_DIR="/app/output/csv_export"
if [ -d "$CSV_DIR" ] && [ -f "$CSV_DIR/patterns_summary.csv" ]; then
    echo "📂 CSV data found - seeding database..."
    
    # Run seeding script (skip existing patterns)
    python3 seed_from_csv.py --quiet || {
        echo "⚠️  Warning: Database seeding failed. Starting API anyway..."
    }
    
    echo "✅ Database ready with data"
else
    echo "⚠️  No CSV data found at $CSV_DIR"
    echo "   Starting with empty database"
    echo "   To seed data, mount CSV files to /app/output/csv_export"
fi

echo "🚀 Starting FastAPI server..."
echo "==========================================="

# Start the API server
exec uvicorn api:app --host 0.0.0.0 --port 8000

