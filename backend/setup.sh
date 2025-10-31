#!/bin/bash

# Setup script for Fake News Detection System
# This script ensures all dependencies are properly installed

set -e  # Exit on error

echo "🔧 Setting up Fake News Detection System..."
echo ""

# Create logs directory
echo "📁 Creating logs directory..."
mkdir -p logs
echo "✅ Logs directory created"
echo ""

# Check Python version
echo "🐍 Checking Python version..."
python3 --version
echo ""

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt
echo "✅ Python dependencies installed"
echo ""

# Download spaCy model
echo "📚 Downloading spaCy English model..."
python3 -m spacy download en_core_web_sm
echo "✅ spaCy model downloaded"
echo ""

# Download NLTK data (if needed)
echo "📚 Downloading NLTK data..."
python3 <<EOF
import nltk
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
    print("✅ NLTK data downloaded")
except Exception as e:
    print(f"⚠️ NLTK download had issues: {e}")
EOF
echo ""

# Check .env file
echo "🔑 Checking environment variables..."
if [ ! -f .env ]; then
    echo "⚠️  WARNING: .env file not found!"
    echo "   Please create .env file with the following content:"
    echo "   OPENAI_API_KEY=your_api_key_here"
    echo "   TAVILY_API_KEY=your_tavily_key_here (optional)"
    echo ""
    echo "   You can copy from .env.example if it exists"
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ Created .env from .env.example (please update with your API keys)"
    else
        echo "   Creating a template .env file..."
        cat > .env <<ENVEOF
# OpenAI API Key (Required)
OPENAI_API_KEY=your_openai_api_key_here

# Tavily API Key (Optional, for fact verification)
TAVILY_API_KEY=your_tavily_api_key_here

# MongoDB Configuration (Optional)
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=fakenews_db

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/fakenews.log
ENVEOF
        echo "✅ Created template .env file (please update with your API keys)"
    fi
else
    echo "✅ .env file found"
fi
echo ""

# Check if MongoDB is needed
echo "🗄️  MongoDB check..."
if python3 <<EOF
import pymongo
try:
    client = pymongo.MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=2000)
    client.server_info()
    print("✅ MongoDB is running")
except:
    print("⚠️  MongoDB is not running (optional, may affect some features)")
EOF
then
    echo ""
else
    echo ""
fi

echo "🎉 Setup completed!"
echo ""
echo "📝 Next steps:"
echo "   1. Update .env file with your API keys"
echo "   2. Run: python3 main.py"
echo "   3. Open: http://localhost:8000"
echo ""

