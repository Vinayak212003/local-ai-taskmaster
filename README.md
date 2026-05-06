# 🤖 LocalAI TaskMaster
![LocalAI TaskMaster Demo](screenshots/demo.png)

> **A production-ready, local-first multi-agent AI task automation system.**  
> Built with FastAPI · React · SQLite · Ollama · Mistral — fully offline, zero cloud dependency.

---

## 📸 What It Does

LocalAI TaskMaster accepts a natural language task and runs it through a **3-agent AI pipeline**:

```
Your Task → 🧠 Planner → ⚙️ Executor (per subtask) → 🔍 Validator → Final Result
```

| Agent | Role |
|---|---|
| 🧠 **Planner** | Decomposes your task into ordered subtasks |
| ⚙️ **Executor** | Runs each subtask with full LLM reasoning |
| 🔍 **Validator** | Scores output quality (0–100) + synthesizes result |

All output streams in real-time via **SSE** — you watch each agent think.

---

## 🧠 Architecture

```
┌─────────────────────────────────────────────────────┐
│                 React Frontend (Vite)                │
│  TaskForm → SSE Listener → AgentPanels → Result     │
└─────────────────┬───────────────────────────────────┘
                  │ REST + SSE
┌─────────────────▼───────────────────────────────────┐
│              FastAPI Backend                         │
│  /api/tasks  →  Orchestrator                        │
│                 ├── PlannerAgent                    │
│                 ├── ExecutorAgent (x N)             │
│                 └── ValidatorAgent                  │
│              SQLite (aiosqlite + SQLAlchemy)         │
└─────────────────┬───────────────────────────────────┘
                  │ HTTP /api/generate
┌─────────────────▼───────────────────────────────────┐
│         Ollama Server (localhost:11434)              │
│         Mistral / LLaMA3 / Phi3 (GGUF)              │
└─────────────────────────────────────────────────────┘
```

---

## ⚡ Tech Stack

| Layer | Technology | Reason |
|---|---|---|
| Frontend | React 18 + Vite | Fast dev server, minimal deps |
| Backend | FastAPI + Python 3.10+ | Async-first, fast, typed |
| Database | SQLite + aiosqlite | Zero-config, local, async |
| ORM | SQLAlchemy 2.0 | Async sessions |
| AI Runtime | Ollama | Local inference, easy model management |
| Models | Mistral 7B (default) | Best quality/RAM tradeoff at 8GB |
| Streaming | SSE (Server-Sent Events) | Real-time token streaming |
| Config | Pydantic Settings | Type-safe env config |

---

## 🖥️ Requirements

| Requirement | Minimum | Recommended |
|---|---|---|
| RAM | 8 GB | 16 GB |
| CPU | 4 cores | 6+ cores |
| Storage | 8 GB free | 15 GB free |
| Python | 3.10+ | 3.11+ |
| Node.js | 18+ | 20+ |
| OS | Windows 10 / macOS / Linux | Any |

---

## 🚀 Terminal Tutorial — Complete Setup & Run

### STEP 1: Install Ollama

**Linux / macOS:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
```
Download installer from: https://ollama.ai/download
Run the .exe installer, then restart your terminal.
```

Verify installation:
```bash
ollama --version
```

---

### STEP 2: Pull a Model

For 8GB RAM (recommended):
```bash
ollama pull mistral
```

For lower RAM (lighter options):
```bash
ollama pull phi3          # 2.3 GB — fast
ollama pull gemma2:2b     # 1.6 GB — smallest
```

Verify model is available:
```bash
ollama list
```

---

### STEP 3: Clone & Enter Project

```bash
git clone https://github.com/yourusername/local-ai-taskmaster.git
cd local-ai-taskmaster
```

---

### STEP 4: Configure Environment

```bash
cp .env.example .env
```

Edit `.env` if needed (optional — defaults work out of the box):
```bash
# Linux/macOS
nano .env

# Windows
notepad .env
```

---

### STEP 5: Setup Python Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows CMD)
venv\Scripts\activate.bat

# Activate (Windows PowerShell)
venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

---

### STEP 6: Start Ollama Server

Open a **new terminal tab/window**:
```bash
ollama serve
```

Keep this running. You should see:
```
Ollama is running at http://localhost:11434
```

---

### STEP 7: Start the Backend

Back in your backend terminal (with venv activated):
```bash
cd backend  # if not already there
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Database initialized at .../database/taskmaster.db
INFO:     🚀 LocalAI TaskMaster v1.0.0 started on http://0.0.0.0:8000
INFO:     Application startup complete.
```

Test the API:
```bash
curl http://localhost:8000/api/health
```

Expected output:
```json
{
  "status": "ok",
  "ollama_online": true,
  "available_models": ["mistral:latest"],
  "app_version": "1.0.0"
}
```

---

### STEP 8: Start the Frontend

Open another **new terminal tab/window**:
```bash
cd frontend
npm install
npm run dev
```

You should see:
```
  VITE v5.x.x  ready in 300ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://0.0.0.0:5173/
```

Open your browser: **http://localhost:5173**

---

### STEP 9: Run Your First Task

**Option A — Browser UI:**
1. Open http://localhost:5173
2. Enter a title: `Python Blog Post`
3. Enter description: `Write a comprehensive blog post about Python async/await with examples`
4. Click **🚀 Run Task Pipeline**
5. Watch agents stream in real-time!

**Option B — API directly:**
```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Async Blog Post",
    "description": "Write a comprehensive blog post about Python async/await with practical examples",
    "model": "mistral"
  }'
```

Response:
```json
{
  "id": "abc123...",
  "title": "Python Async Blog Post",
  "status": "pending",
  ...
}
```

Stream the result:
```bash
# Replace abc123 with your task ID
curl -N http://localhost:8000/api/tasks/abc123/stream
```

---

### STEP 10: Run Tests

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
pytest ../tests/ -v
```

---

## 🔧 One-Command Startup (Linux/macOS)

```bash
chmod +x scripts/start.sh
bash scripts/start.sh
```

**Windows:**
```cmd
scripts\start.bat
```

---

## 📡 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | System + Ollama status |
| `POST` | `/api/tasks` | Create and launch a task |
| `GET` | `/api/tasks` | List all tasks |
| `GET` | `/api/tasks/{id}` | Get single task |
| `DELETE` | `/api/tasks/{id}` | Delete task |
| `GET` | `/api/tasks/{id}/stream` | SSE real-time stream |
| `GET` | `/api/prompts` | List prompt templates |
| `GET` | `/api/prompts/{name}` | Get a prompt template |
| `POST` | `/api/prompts/reload` | Reload prompt cache |
| `GET` | `/docs` | Swagger UI |
| `GET` | `/redoc` | ReDoc UI |

---

## 🧪 Example Tasks

```
Write a technical README for a FastAPI project with JWT authentication

Create a Python script that monitors CPU/RAM usage and logs alerts to a file

Plan a 30-day learning roadmap for becoming a backend engineer

Write a detailed code review for a REST API with common security vulnerabilities
```

---

## 🔧 Customizing Agent Behavior

Edit prompt templates in `backend/config/prompts/`:

| File | Controls |
|---|---|
| `planner.yaml` | How tasks are broken into subtasks |
| `executor.yaml` | How each subtask is executed |
| `validator.yaml` | Quality scoring criteria |

After editing, reload without restarting:
```bash
curl -X POST http://localhost:8000/api/prompts/reload
```

---

## 🐛 Troubleshooting

**Ollama not connecting:**
```bash
# Check if running
curl http://localhost:11434/api/tags

# Start if not running
ollama serve
```

**Model too slow / runs out of RAM:**
```bash
# Use a lighter model
ollama pull phi3
# Update .env: OLLAMA_MODEL=phi3
```

**Port already in use:**
```bash
# Change backend port
uvicorn main:app --port 8001
# Update .env: PORT=8001
```

**SQLite errors:**
```bash
mkdir -p database
# Database is auto-created on first start
```

---

## 📁 Project Structure

```
local-ai-taskmaster/
├── backend/
│   ├── main.py                  # FastAPI app factory
│   ├── requirements.txt
│   ├── config/
│   │   └── prompts/             # YAML prompt templates
│   │       ├── planner.yaml
│   │       ├── executor.yaml
│   │       └── validator.yaml
│   └── app/
│       ├── api/                 # Route handlers
│       │   ├── tasks.py
│       │   ├── health.py
│       │   └── prompts.py
│       ├── agents/              # AI agent logic
│       │   ├── orchestrator.py  # Pipeline controller
│       │   ├── planner.py
│       │   ├── executor.py
│       │   └── validator.py
│       ├── core/
│       │   ├── config.py        # Settings (env-based)
│       │   ├── database.py      # SQLite async engine
│       │   └── logger.py
│       ├── models/
│       │   └── task.py          # SQLAlchemy ORM
│       ├── services/
│       │   ├── ollama_client.py # Async Ollama HTTP client
│       │   ├── task_service.py  # Task CRUD
│       │   ├── stream_service.py # SSE queue manager
│       │   └── prompt_service.py
│       └── utils/
│           └── schemas.py       # Pydantic request/response
├── frontend/
│   ├── index.html
│   ├── vite.config.js
│   ├── package.json
│   └── src/
│       ├── main.jsx
│       ├── App.jsx              # Root layout
│       ├── components/
│       │   ├── TaskForm.jsx
│       │   ├── TaskDetail.jsx   # Live stream view
│       │   ├── TaskHistory.jsx
│       │   ├── AgentPanel.jsx   # Per-agent stream display
│       │   └── StatusBadge.jsx
│       ├── hooks/
│       │   └── useTaskStream.js # SSE React hook
│       ├── utils/
│       │   └── api.js
│       └── styles/
│           └── global.css
├── tests/
│   ├── test_api.py
│   └── test_agents.py
├── diagrams/
│   └── architecture.puml        # PlantUML diagrams
├── database/                    # Auto-created SQLite DB
├── scripts/
│   ├── start.sh                 # Linux/macOS one-click start
│   ├── start.bat                # Windows one-click start
│   └── pull_models.sh           # Pull Ollama models
├── BRD.md                       # Business Requirements Document
├── .env.example
├── .gitignore
└── LICENSE
```

---

## 🤝 Contributing

PRs welcome. Please:
1. Fork the repo
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Run tests: `pytest tests/ -v`
4. Submit a PR

---

## 📄 License

MIT — see [LICENSE](LICENSE)

---

*Built for AI engineers who want full control over their automation stack.*
