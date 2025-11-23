#!/bin/bash
# ===========================================
# RodeoAI Backend Setup Script
# ===========================================
# One-command setup for the RodeoAI backend
# Run with: ./scripts/setup.sh

set -e

echo "============================================"
echo "  RodeoAI Backend Setup"
echo "============================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

info() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Check Python version
check_python() {
    info "Checking Python version..."

    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        error "Python not found. Please install Python 3.9 or higher."
    fi

    PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    info "Python version: $PYTHON_VERSION"

    # Check minimum version (3.9)
    if [[ $(echo "$PYTHON_VERSION < 3.9" | bc -l) -eq 1 ]]; then
        error "Python 3.9 or higher is required. Found: $PYTHON_VERSION"
    fi
}

# Create virtual environment
setup_venv() {
    info "Setting up virtual environment..."

    if [ -d "venv" ]; then
        warn "Virtual environment already exists. Skipping creation."
    else
        $PYTHON_CMD -m venv venv
        info "Virtual environment created."
    fi

    # Activate virtual environment
    source venv/bin/activate
    info "Virtual environment activated."

    # Upgrade pip
    pip install --upgrade pip
}

# Install dependencies
install_deps() {
    info "Installing Python dependencies..."
    pip install -r requirements.txt
    info "Dependencies installed."
}

# Setup environment file
setup_env() {
    info "Setting up environment configuration..."

    if [ -f ".env" ]; then
        warn ".env file already exists. Skipping."
    else
        cp .env.example .env
        info "Created .env file from template."
        echo ""
        warn "IMPORTANT: Edit .env and add your OPENAI_API_KEY"
        echo "  nano .env"
        echo "  or"
        echo "  vim .env"
        echo ""
    fi
}

# Install browsers
install_browsers() {
    info "Installing Playwright browsers..."

    # Install Playwright
    pip install playwright

    # Install Chromium only (faster)
    playwright install chromium

    # Try to install dependencies (may need sudo)
    info "Installing browser dependencies..."
    playwright install-deps chromium 2>/dev/null || {
        warn "Could not install browser deps automatically."
        warn "You may need to run: sudo playwright install-deps chromium"
    }

    info "Browsers installed."
}

# Create necessary directories
create_dirs() {
    info "Creating necessary directories..."

    mkdir -p logs
    mkdir -p data
    mkdir -p screenshots

    info "Directories created."
}

# Verify setup
verify_setup() {
    info "Verifying setup..."

    echo ""
    echo "Checking imports..."

    python -c "import fastapi; print(f'  FastAPI: {fastapi.__version__}')"
    python -c "import uvicorn; print(f'  Uvicorn: OK')"
    python -c "import bs4; print(f'  BeautifulSoup: OK')"
    python -c "import selenium; print(f'  Selenium: {selenium.__version__}')"
    python -c "import playwright; print(f'  Playwright: OK')"

    echo ""
    info "All dependencies verified!"
}

# Print next steps
print_next_steps() {
    echo ""
    echo "============================================"
    echo -e "${GREEN}  Setup Complete!${NC}"
    echo "============================================"
    echo ""
    echo "Next steps:"
    echo ""
    echo "  1. Edit your environment configuration:"
    echo "     nano .env"
    echo ""
    echo "  2. Add your OpenAI API key to .env:"
    echo "     OPENAI_API_KEY=sk-your-key-here"
    echo ""
    echo "  3. Start the development server:"
    echo "     source venv/bin/activate"
    echo "     uvicorn main:app --reload"
    echo ""
    echo "  4. Or use Docker:"
    echo "     docker-compose up -d"
    echo ""
    echo "  API will be available at: http://localhost:8000"
    echo "  API docs at: http://localhost:8000/docs"
    echo ""
}

# Main function
main() {
    check_python
    setup_venv
    install_deps
    setup_env
    install_browsers
    create_dirs
    verify_setup
    print_next_steps
}

# Run
main "$@"
