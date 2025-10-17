#!/bin/bash

echo "🚀 Starting Full-Stack AI Application..."

echo "📦 Installing frontend dependencies..."
cd frontend
npm install

echo "🏗️  Building React frontend..."
npm run build

cd ..

echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo "🔥 Starting FastAPI server on port 5000..."
uvicorn main:app --host 0.0.0.0 --port 5000 --reload
