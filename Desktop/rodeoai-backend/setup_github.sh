#!/bin/bash

# RodeoAI Backend - GitHub Repository Setup Script
# This script initializes the backend repository and pushes to GitHub

echo "========================================="
echo "RodeoAI Backend - GitHub Setup"
echo "========================================="
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo "Initializing git repository..."
    git init
    git branch -M main
else
    echo "Git repository already initialized"
fi

# Check if remote exists
if git remote | grep -q origin; then
    echo "Remote 'origin' already exists"
    git remote -v
else
    echo ""
    echo "Please enter your GitHub repository URL:"
    echo "Example: https://github.com/YOUR_USERNAME/rodeoai-backend.git"
    read -p "Repository URL: " REPO_URL

    if [ -z "$REPO_URL" ]; then
        echo "Error: Repository URL cannot be empty"
        exit 1
    fi

    echo "Adding remote 'origin'..."
    git remote add origin "$REPO_URL"
fi

echo ""
echo "Checking git status..."
git status

echo ""
read -p "Do you want to commit and push all changes? (y/n): " CONFIRM

if [ "$CONFIRM" = "y" ] || [ "$CONFIRM" = "Y" ]; then
    echo "Staging all changes..."
    git add .

    echo "Creating commit..."
    git commit -m "feat: RodeoAI backend with TAURUS routing and Railway deployment config

- FastAPI backend with intelligent model routing
- Supabase authentication integration
- Railway deployment configuration
- PostgreSQL database with SQLAlchemy
- Contestant profile management
- Chat API with streaming responses
- Comprehensive test suite" || echo "No changes to commit or commit failed"

    echo ""
    echo "Pushing to GitHub..."
    git push -u origin main

    echo ""
    echo "========================================="
    echo "Setup complete!"
    echo "========================================="
    echo ""
    echo "Next steps:"
    echo "1. Go to https://railway.app/new"
    echo "2. Click 'Deploy from GitHub repo'"
    echo "3. Select 'rodeoai-backend' repository"
    echo "4. Configure environment variables (see RAILWAY_DEPLOYMENT.md)"
    echo ""
else
    echo "Skipping commit and push"
    echo "You can manually run:"
    echo "  git add ."
    echo "  git commit -m 'Your message'"
    echo "  git push -u origin main"
fi
