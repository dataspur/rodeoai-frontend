#!/bin/bash
# ===========================================
# RodeoAI Development Server Script
# ===========================================
# Quick start script for development
# Run with: ./scripts/run-dev.sh

set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Starting RodeoAI Backend (Development)${NC}"
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo -e "${YELLOW}Virtual environment activated${NC}"
fi

# Load environment variables
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
    echo -e "${YELLOW}Environment variables loaded${NC}"
fi

# Check for OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${YELLOW}Warning: OPENAI_API_KEY not set. Chat functionality will not work.${NC}"
fi

echo ""
echo "Starting server on http://localhost:${PORT:-8000}"
echo "API docs available at http://localhost:${PORT:-8000}/docs"
echo ""

# Run uvicorn with hot reload
uvicorn main:app \
    --host 0.0.0.0 \
    --port ${PORT:-8000} \
    --reload \
    --log-level ${LOG_LEVEL:-info}
