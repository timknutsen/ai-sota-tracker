#!/bin/bash
# ============================================================
# AI SOTA Tracker — Launch Script
# Double-click this file or run: ./launch.command
# ============================================================

cd "$(dirname "$0")"

# Load API key from .env file if it exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Check for API key
if [ -z "$GEMINI_API_KEY" ] && [ -z "$DEEPSEEK_API_KEY" ] && [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ No API key found."
    echo ""
    echo "Create a .env file in this folder with:"
    echo "  GEMINI_API_KEY=your-key-here"
    echo ""
    echo "Or export it in your ~/.zshrc"
    read -p "Press Enter to exit..."
    exit 1
fi

echo "🔄 Running pipeline..."
python3 run.py

echo ""
echo "🌐 Starting server at http://localhost:8000"
echo "   Press Ctrl+C to stop"
echo ""

# Open browser after a short delay
(sleep 1 && open http://localhost:8000) &

python3 server.py
