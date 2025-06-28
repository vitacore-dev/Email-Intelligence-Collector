# Multi-stage Dockerfile for Email Intelligence Backend with Comprehensive Analysis
# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Additional dependencies for comprehensive analysis
RUN pip install --no-cache-dir --user \
    lxml \
    beautifulsoup4 \
    fake-useragent \
    tldextract \
    url-normalize \
    PyPDF2 \
    pdfplumber \
    gunicorn

# Stage 2: Development
FROM python:3.11-slim as development

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Environment variables for development
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PATH=/root/.local/bin:$PATH \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBUG=True \
    MAX_PROCESSING_TIME=300 \
    ENABLE_COMPREHENSIVE_ANALYSIS=True

# Copy application code
COPY . .

# Create directories
RUN mkdir -p logs data uploads temp

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Development command with reload
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Stage 3: Production
FROM python:3.11-slim as production

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r appuser && useradd -r -g appuser appuser

# Copy Python packages from builder
COPY --from=builder /root/.local /home/appuser/.local

# Environment variables for production
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PATH=/home/appuser/.local/bin:$PATH \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBUG=False \
    MAX_PROCESSING_TIME=300 \
    ENABLE_COMPREHENSIVE_ANALYSIS=True

# Copy application code
COPY --chown=appuser:appuser . .

# Create directories and set permissions
RUN mkdir -p logs data uploads temp /home/appuser/.cache && \
    chown -R appuser:appuser /app /home/appuser/.cache

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Production command with gunicorn
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--access-logfile", "-", "--error-logfile", "-"]

