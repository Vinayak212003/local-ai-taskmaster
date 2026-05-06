#!/usr/bin/env bash
# scripts/start.sh — Start the full LocalAI TaskMaster stack
# Usage: bash scripts/start.sh

set -e

BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo -e "${BOLD}${BLUE}🤖 LocalAI TaskMaster — Startup${NC}"
echo "============================================"

# ── Check Python ──────────────────────────────────────────────────────────────
if ! command -v python3 &> /dev/null; then
  echo -e "${RED}❌ Python 3 not found. Install Python 3.10+${NC}"
  exit 1
fi
PY_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo -e "${GREEN}✓ Python ${PY_VER}${NC}"

# ── Check Ollama ──────────────────────────────────────────────────────────────
if ! command -v ollama &> /dev/null; then
  echo -e "${YELLOW}⚠ Ollama not found.${NC}"
  echo "  Install from: https://ollama.ai"
  echo "  Then run: ollama pull mistral"
  echo ""
fi

# ── Check if Ollama is running ─────────────────────────────────────────────────
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
  echo -e "${GREEN}✓ Ollama is running${NC}"
else
  echo -e "${YELLOW}⚠ Ollama not running. Starting it...${NC}"
  ollama serve &
  sleep 3
  if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Ollama started${NC}"
  else
    echo -e "${YELLOW}  Ollama may still be starting. Continue anyway.${NC}"
  fi
fi

# ── Setup .env ────────────────────────────────────────────────────────────────
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [ ! -f "${ROOT_DIR}/.env" ]; then
  cp "${ROOT_DIR}/.env.example" "${ROOT_DIR}/.env"
  echo -e "${GREEN}✓ Created .env from .env.example${NC}"
fi

# ── Install Python dependencies ───────────────────────────────────────────────
echo ""
echo -e "${BOLD}Installing backend dependencies...${NC}"
cd "${ROOT_DIR}/backend"
if [ ! -d "venv" ]; then
  python3 -m venv venv
  echo -e "${GREEN}✓ Created virtual environment${NC}"
fi
source venv/bin/activate
pip install -q -r requirements.txt
echo -e "${GREEN}✓ Backend dependencies installed${NC}"

# ── Create database directory ─────────────────────────────────────────────────
mkdir -p "${ROOT_DIR}/database"

# ── Start backend ─────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}Starting backend...${NC}"
cd "${ROOT_DIR}/backend"
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
echo -e "${GREEN}✓ Backend started (PID: ${BACKEND_PID})${NC}"

sleep 2

# ── Install + start frontend ──────────────────────────────────────────────────
if command -v node &> /dev/null; then
  echo ""
  echo -e "${BOLD}Starting frontend...${NC}"
  cd "${ROOT_DIR}/frontend"
  if [ ! -d "node_modules" ]; then
    npm install -q
    echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
  fi
  npm run dev &
  FRONTEND_PID=$!
  echo -e "${GREEN}✓ Frontend started (PID: ${FRONTEND_PID})${NC}"
  FRONTEND_URL="http://localhost:5173"
else
  echo -e "${YELLOW}⚠ Node.js not found — skipping frontend. Use API directly.${NC}"
  FRONTEND_URL="N/A"
fi

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}${GREEN}============================================"
echo "  🚀 LocalAI TaskMaster is running!"
echo "============================================${NC}"
echo -e "  🌐 Frontend:  ${BLUE}${FRONTEND_URL}${NC}"
echo -e "  🔧 API:       ${BLUE}http://localhost:8000${NC}"
echo -e "  📄 API Docs:  ${BLUE}http://localhost:8000/docs${NC}"
echo ""
echo -e "  Press ${BOLD}Ctrl+C${NC} to stop all services."
echo ""

# Wait for Ctrl+C
trap "echo ''; echo 'Stopping...'; kill $BACKEND_PID 2>/dev/null; kill $FRONTEND_PID 2>/dev/null; exit 0" SIGINT
wait
