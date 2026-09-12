# 🛠️ Developer Workflow & Quickstart Guide

This document outlines the specific local development workflow, environment setup, and execution steps for the **Air-Gapped Hybrid RAG System**. 

For our universal engineering standards, infrastructure hygiene, and defensive coding rules, refer to the [AI Engineering Playbook](./PLAYBOOK.md).

---

## 🚀 1. Daily Development Routine

### Startup Sequence
1. **Start Infrastructure Stack:** Spin up your multi-service stack via Docker Compose (`docker compose up --build -d`). Verify container health via `docker ps` to ensure ports (`5432`, `8000`, `8501`) are active.
2. **Verify LLM Container & Model:** Ensure containerized Ollama is active on port `11434`. Pull or verify model weights inside the container:
```bash
docker exec -it rag_ollama ollama pull llama3.2
```
3. **Activate Virtual Environment:** Load your local Python virtual environment (.\venv\Scripts\Activate on Windows or source venv/bin/activate on Linux/macOS) for local hybrid development.
4. **Verify Health:** Confirm backend readiness via http://localhost:8000/health or observe the Streamlit UI status loader (st.status).

### Day-End Shutdown Routine
1. **Update Living Documentation:** Record daily architectural decisions, benchmark scores, and updates in SESSION_JOURNEY.md, README.md, and GLOSSARY.md.
2. **Commit Changes:** Stage and commit your work using conventional commit messages (git add . then git commit -m "feat: [description]").
3. **Stop Stack:** Gracefully stop local services while preserving persistent Docker volumes (docker compose down).
4. **Free System RAM (Windows/WSL):** Clear background Linux VMs if necessary (wsl --shutdown).
5. **Deactivate Environment:** Exit the active Python virtual environment (deactivate).

---

## 💻 2. Local Setup & Installation

### Prerequisites
* Python 3.11+
* Docker & Docker Compose
* Git

### Clone & Configure
```bash
    # Clone the repository
    git clone https://github.com/your-username/ai-engineering-sprint.git
    cd ai-engineering-sprint

    # Copy environment configuration
    cp .env.example .env
```
### Python Virtual Environment Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate
# (On Linux/macOS: source venv/bin/activate)

# Install project dependencies
pip install -r requirements.txt
```

---

## 🏃 3. Running the Application Services

You can run the application using either the Fully Containerized Stack (recommended for production parity) or the Local Hybrid Workflow (recommended for active code iteration).

### Option A: Fully Containerized Stack (Production Mode)
Spin up the entire multi-service ecosystem (PostgreSQL + pgvector, FastAPI Backend, Streamlit UI, and containerized Ollama) using Docker Compose:
```bash
# 1. Build and launch all services in detached mode
docker compose up --build -d

# 2. Pull Llama 3.2 model inside Ollama container (One-time setup)
docker exec -it rag_ollama ollama pull llama3.2
```
* Streamlit UI: http://localhost:8501
* FastAPI Docs: http://localhost:8000/docs

### Option B: Local Hybrid Development (Dual Terminal Setup)
If you are actively modifying backend or frontend Python code and require hot-reloading:
```bash
# 1. Start only the PostgreSQL vector database container
docker compose up -d postgres_vector

# 2. Ensure local Ollama is active and model is pulled
ollama pull llama3.2

# Terminal 1: Launch FastAPI Backend (with auto-reload)
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Launch Streamlit Frontend UI
streamlit run app_ui.py
```

---

## 🧪 4. Automated Testing & Quantitative Evaluation

### Run Unit & Endpoint Test Suite (pytest)
Execute backend unit and endpoint tests with isolated ML model and database mocks:
```bash
pytest test_app.py -v --cov=app
```
### Run Automated Pipeline Evaluation (Ragas)
To verify pipeline quality and check benchmark scores (Faithfulness, Answer Relevancy, Context Precision/Recall) using Ragas:
```bash
python evaluate_rag.py
# This executes the automated evaluation suite against your golden dataset and exports metrics to evaluation_report.csv.
```
### Run Automated Retrieval Benchmark (evaluate_retrieval.py)
Benchmark Hit-Rate@K and Mean Reciprocal Rank (MRR) against ground-truth query sets:
```bash
python evaluate_retrieval.py
```

---

## 🧹 5. Database Maintenance & Reset Procedures

If your vector database encounters schema conflicts or requires a complete reset:
```bash
# Tear down containers and remove persistent volumes:
docker compose down -v

# Restart fresh container instances:
docker compose up --build -d

# Re-pull model weights inside container:
docker exec -it rag_ollama ollama pull llama3.2
```