#!/bin/bash

# This script prepares and starts the Flask backend server for the VectorDB UI.

echo "🚀 Starting Web UI setup..."

# 1. Check for Python and pip
if ! command -v python3 &> /dev/null || ! command -v pip3 &> /dev/null; then
    echo "❌ Python 3 and/or pip3 is not installed. Please install them to continue."
    exit 1
fi

# 2. Install required Python packages
echo "📦 Installing/updating required Python packages..."
echo "   (Flask, LangChain, OpenAI, VectorDB clients, and more...)"

# Thêm langchain, openai và các client vector db vào danh sách cài đặt
pip3 install -q --upgrade \
    Flask \
    Flask-Cors \
    requests \
    beautifulsoup4 \
    pypdf \
    python-docx \
    openpyxl \
    python-pptx \
    langchain \
    openai \
    qdrant-client \
    sentence-transformers \
    chromadb \
    mcp

if [ $? -ne 0 ]; then
    echo "❌ Failed to install Python packages. Please check your pip installation."
    exit 1
fi

echo "✅ Dependencies are ready."

# 3. Start the Flask server
echo "🔥 Launching the Flask backend server on http://127.0.0.1:5001..."
echo "   (Press CTRL+C to stop the server)"
echo ""
PYTHONPATH=$PYTHONPATH:./src/:./web_ui python3 web_ui/server.py

