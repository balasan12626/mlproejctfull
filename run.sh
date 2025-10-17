#!/bin/bash
set -e

echo "🚀 Starting Full-Stack AI Application..."

cd frontend

if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install --legacy-peer-deps
else
    echo "✅ Frontend dependencies already installed"
fi

echo "🏗️  Building React frontend..."
npm run build

cd ..

echo "📦 Installing Python dependencies..."
pip install -q -r requirements.txt 2>&1 | grep -v "already satisfied" || true

echo "🔥 Starting FastAPI server on port 5000..."
uvicorn main:app --host 0.0.0.0 --port 5000
