#!/bin/bash

# Setup script for Financial AI Agent

set -e

echo "🚀 Setting up Financial AI Agent..."

# Create virtual environment
python -m venv financial-agent
source financial-agent/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements_updated.txt

# Create necessary directories
mkdir -p logs
mkdir -p data
mkdir -p tests

# Copy environment template
if [ ! -f .env ]; then
    cp .env.template .env
    echo "📝 Created .env file from template. Please update with your API keys."
fi

# Run tests
echo "🧪 Running tests..."
python -m pytest tests/ -v

echo "✅ Setup completed successfully!"
echo "📖 Next steps:"
echo "   1. Update .env file with your API keys"
echo "   2. Run: streamlit run improved_main.py"