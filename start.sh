#!/bin/bash

# YiriAi Full Stack Quick Start
# Starts both backend and frontend

set -e

echo "🚀 YiriAi Full Stack Quick Start"
echo "=================================="
echo ""

# Check prerequisites
echo "🔍 Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed"
    exit 1
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    exit 1
fi

echo "✅ Prerequisites OK"
echo ""

# Start infrastructure (PostgreSQL + Redis)
echo "📦 Starting PostgreSQL and Redis..."
cd "$(dirname "$0")"

if ! docker ps | grep -q postgres; then
    docker-compose up -d
    echo "⏳ Waiting for databases to be ready..."
    sleep 5
fi

echo "✅ Infrastructure running"
echo ""

# Setup backend (if not done)
if [ ! -d "venv" ]; then
    echo "📦 Setting up backend..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -q -r requirements.txt
    python init_db.py
    echo "✅ Backend setup complete"
else
    source venv/bin/activate
    echo "✅ Backend already set up"
fi

echo ""

# Setup frontend (if not done)
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Setting up frontend..."
    cd frontend
    npm install --silent
    cd ..
    echo "✅ Frontend setup complete"
else
    echo "✅ Frontend already set up"
fi

echo ""
echo "🎯 Starting services..."
echo ""

# Start backend in background
echo "▶️  Starting backend API (port 8000)..."
python main.py > backend.log 2>&1 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"

# Wait for backend to be ready
echo "⏳ Waiting for backend..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Backend failed to start. Check backend.log"
        kill $BACKEND_PID 2>/dev/null || true
        exit 1
    fi
    sleep 1
done

echo ""

# Start frontend
echo "▶️  Starting frontend dev server (port 5173)..."
cd frontend
npm run dev &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"

cd ..

echo ""
echo "═══════════════════════════════════════════════════════"
echo "✨ YiriAi is running!"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "🌐 Frontend:  http://localhost:5173"
echo "🔌 Backend:   http://localhost:8000"
echo "📊 API Docs:  http://localhost:8000/docs"
echo "💾 Database:  PostgreSQL on port 5432"
echo "🗄️  Cache:     Redis on port 6379"
echo ""
echo "📝 Logs:"
echo "   Backend:  tail -f backend.log"
echo "   Frontend: Check terminal output"
echo ""
echo "🛑 To stop all services:"
echo "   Press Ctrl+C, then run: ./stop.sh"
echo ""
echo "═══════════════════════════════════════════════════════"
echo ""

# Create stop script
cat > stop.sh << 'EOF'
#!/bin/bash
echo "🛑 Stopping YiriAi services..."
kill $(lsof -ti:8000) 2>/dev/null || true
kill $(lsof -ti:5173) 2>/dev/null || true
docker-compose down
echo "✅ All services stopped"
EOF
chmod +x stop.sh

# Wait for user interrupt
trap "echo ''; echo '🛑 Shutting down...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; docker-compose down; echo '✅ Stopped'; exit 0" INT TERM

# Keep script running
wait
