# ThreatTrace AI — Production Deployment & Quickstart Guide

## 1. Prerequisites
- Python 3.9 or higher
- Node.js 18+ and npm
- Git

## 2. Running Locally

### Backend (FastAPI API Server)
```bash
# Navigate to backend directory
cd backend

# Create virtual environment (if not created)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI server on port 8000
PYTHONPATH=. venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Frontend (Next.js SOC Workspace)
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start Next.js development server on port 3002
npm run dev -- -p 3002
```

## 3. Running Automated Tests
```bash
# Run full PyTest test suite (Phases 1-8)
PYTHONPATH=backend backend/venv/bin/pytest backend/tests/ -v

# Run frontend build check
cd frontend && npm run build
```
