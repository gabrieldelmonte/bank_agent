#!/bin/bash

# Bank Agent Setup Script

echo "Bank Agent System Setup"
echo "=========================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.10+"
    exit 1
fi

echo "Python 3 found"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv bank_venv

# Activate virtual environment
echo "Activating virtual environment..."
source bank_venv/bin/activate

# Installing uv
pip install uv

# Upgrade pip
echo "Upgrading pip..."
uv pip install --upgrade pip

# Install requirements
echo "Installing dependencies..."
uv pip install -r requirements.txt

# Check for .env file
if [ ! -f .env ]; then
    echo ""
    echo ".env file not found!"
    echo "Please create a .env file with your Google API key:"
    echo ""
    echo "   cp .env.example .env"
    echo "   nano .env  # or your preferred editor"
    echo ""
    echo "   Then add your GOOGLE_API_KEY"
fi

echo ""
echo "Setup complete!"
echo ""
echo "To run the application:"
echo ""
echo "   source bank_venv/bin/activate"
echo "   streamlit run src/ui/app.py"
echo ""
