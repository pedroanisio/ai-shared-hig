# Multi-stage build for Universal Corpus Pattern API
# Stage 1: Build stage with all dependencies
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt


# Stage 2: Production runtime image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/data && \
    chown -R appuser:appuser /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY --chown=appuser:appuser *.py ./

# Copy entrypoint script
COPY --chown=appuser:appuser docker-entrypoint.sh ./
RUN chmod +x docker-entrypoint.sh

# Create output directory structure and copy CSV data for seeding
RUN mkdir -p ./output/csv_master

# Copy CSV master data for database seeding (if it exists)
# This will include all CSV files from output/csv_master/ directory
COPY --chown=appuser:appuser output/csv_master/ ./output/csv_master/

# Set PATH to include user's local bin
ENV PATH=/home/appuser/.local/bin:$PATH

# Switch to non-root user
USER appuser

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=5)" || exit 1

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV SQLALCHEMY_DATABASE_URL=sqlite:////app/data/patterns.db

# Run the API with entrypoint script
ENTRYPOINT ["./docker-entrypoint.sh"]

