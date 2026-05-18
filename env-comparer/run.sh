#!/bin/bash
# -----------------------------------------------------------------------------
#  EnvComparer Launcher - Crafted with ♥ by codesaksham
#  A premium developer utility to align, parse, and compare environment lists.
#  Copyright (c) 2026 codesaksham. All rights reserved.
# -----------------------------------------------------------------------------

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "🚀 Starting EnvComparer local setup..."

if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment (.venv)..."
    python3 -m venv .venv
fi

echo "🔄 Activating virtual environment and updating dependencies..."
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "✨ Starting EnvComparer on http://localhost:8090"
uvicorn app.main:app --host 127.0.0.1 --port 8090 --reload
