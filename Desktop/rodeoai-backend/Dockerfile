# RodeoAI Backend Dockerfile
# Multi-stage build for optimized production image

FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# -------------------------------------------
# Development stage
# -------------------------------------------
FROM base as development

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright and browsers
RUN pip install playwright && \
    playwright install chromium && \
    playwright install-deps chromium

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run with hot reload for development
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# -------------------------------------------
# Production stage
# -------------------------------------------
FROM base as production

# Create non-root user for security
RUN groupadd -r rodeoai && useradd -r -g rodeoai rodeoai

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright and browsers
RUN pip install playwright && \
    playwright install chromium && \
    playwright install-deps chromium

# Copy application code
COPY . .

# Change ownership to non-root user
RUN chown -R rodeoai:rodeoai /app

# Switch to non-root user
USER rodeoai

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Run production server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
