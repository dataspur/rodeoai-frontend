#!/bin/bash
# ===========================================
# RodeoAI Browser Installation Script
# ===========================================
# This script installs browsers for Playwright and Selenium
# Run with: ./scripts/install-browsers.sh

set -e

echo "============================================"
echo "  RodeoAI Browser Installation Script"
echo "============================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
info() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check if running as root (needed for system deps)
check_root() {
    if [ "$EUID" -eq 0 ]; then
        warn "Running as root. Some operations may behave differently."
    fi
}

# Detect OS
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
        VERSION=$VERSION_ID
    elif [ -f /etc/debian_version ]; then
        OS="debian"
    elif [ -f /etc/redhat-release ]; then
        OS="rhel"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    else
        OS="unknown"
    fi
    info "Detected OS: $OS"
}

# Install system dependencies for Debian/Ubuntu
install_deps_debian() {
    info "Installing system dependencies for Debian/Ubuntu..."

    sudo apt-get update
    sudo apt-get install -y \
        libnss3 \
        libnspr4 \
        libatk1.0-0 \
        libatk-bridge2.0-0 \
        libcups2 \
        libdrm2 \
        libxkbcommon0 \
        libxcomposite1 \
        libxdamage1 \
        libxfixes3 \
        libxrandr2 \
        libgbm1 \
        libasound2 \
        libpango-1.0-0 \
        libcairo2 \
        libatspi2.0-0 \
        libgtk-3-0 \
        wget \
        curl \
        unzip \
        xvfb
}

# Install system dependencies for RHEL/CentOS/Fedora
install_deps_rhel() {
    info "Installing system dependencies for RHEL/CentOS/Fedora..."

    sudo yum install -y \
        nss \
        nspr \
        atk \
        at-spi2-atk \
        cups-libs \
        libdrm \
        libxkbcommon \
        libXcomposite \
        libXdamage \
        libXfixes \
        libXrandr \
        mesa-libgbm \
        alsa-lib \
        pango \
        cairo \
        at-spi2-core \
        gtk3 \
        wget \
        curl \
        unzip \
        xorg-x11-server-Xvfb
}

# Install Playwright browsers
install_playwright() {
    info "Installing Playwright browsers..."

    # Check if playwright is installed
    if ! python -c "import playwright" 2>/dev/null; then
        info "Installing Playwright Python package..."
        pip install playwright
    fi

    # Install browsers
    info "Installing Chromium browser..."
    playwright install chromium

    # Install system dependencies
    info "Installing Playwright system dependencies..."
    playwright install-deps chromium

    # Optionally install Firefox and WebKit
    read -p "Install Firefox browser? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        playwright install firefox
        playwright install-deps firefox
    fi

    read -p "Install WebKit browser? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        playwright install webkit
        playwright install-deps webkit
    fi

    info "Playwright browsers installed successfully!"
}

# Install Chrome for Selenium
install_chrome_selenium() {
    info "Installing Chrome for Selenium..."

    if [[ "$OS" == "ubuntu" ]] || [[ "$OS" == "debian" ]]; then
        # Download and install Chrome
        wget -q -O /tmp/google-chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
        sudo dpkg -i /tmp/google-chrome.deb || sudo apt-get install -f -y
        rm /tmp/google-chrome.deb

    elif [[ "$OS" == "macos" ]]; then
        if command -v brew &> /dev/null; then
            brew install --cask google-chrome
        else
            warn "Homebrew not found. Please install Chrome manually."
        fi
    else
        warn "Please install Google Chrome manually for your OS."
    fi

    # Install ChromeDriver via webdriver-manager
    info "ChromeDriver will be managed automatically by webdriver-manager."
    pip install webdriver-manager

    info "Chrome for Selenium setup complete!"
}

# Verify installation
verify_installation() {
    info "Verifying browser installation..."

    echo ""
    echo "Playwright browsers:"
    playwright --version

    echo ""
    echo "Checking Chromium..."
    python -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://example.com')
    print(f'  Chromium OK - Page title: {page.title()}')
    browser.close()
" 2>/dev/null && info "Playwright Chromium: OK" || error "Playwright Chromium: FAILED"

    echo ""
    echo "Checking Chrome/Selenium..."
    python -c "
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

try:
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.get('https://example.com')
    print(f'  Selenium OK - Page title: {driver.title}')
    driver.quit()
except Exception as e:
    print(f'  Selenium test skipped: {e}')
" 2>/dev/null && info "Selenium Chrome: OK" || warn "Selenium Chrome: Not configured (optional)"
}

# Main installation function
main() {
    check_root
    detect_os

    echo ""
    echo "This script will install:"
    echo "  1. System dependencies for headless browsers"
    echo "  2. Playwright with Chromium browser"
    echo "  3. Chrome + ChromeDriver for Selenium (optional)"
    echo ""

    read -p "Continue with installation? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 0
    fi

    # Install system dependencies based on OS
    case $OS in
        ubuntu|debian)
            install_deps_debian
            ;;
        rhel|centos|fedora)
            install_deps_rhel
            ;;
        macos)
            info "macOS detected. System dependencies handled by Playwright."
            ;;
        *)
            warn "Unknown OS. Skipping system dependency installation."
            ;;
    esac

    # Install Playwright
    install_playwright

    # Optionally install Chrome for Selenium
    read -p "Install Chrome for Selenium? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        install_chrome_selenium
    fi

    # Verify installation
    echo ""
    verify_installation

    echo ""
    echo "============================================"
    info "Browser installation complete!"
    echo "============================================"
    echo ""
    echo "You can now run the scraping services."
    echo "Start the server with: uvicorn main:app --reload"
    echo ""
}

# Run main function
main "$@"
