# 🛠️ Developer Workflow & Quickstart Guide

This document outlines the specific local development workflow, environment setup, and execution steps for the **Air-Gapped Hybrid RAG System**. 

For our universal engineering standards, infrastructure hygiene, and defensive coding rules, refer to the [AI Engineering Playbook](./PLAYBOOK.md).

---

## 🚀 1. Daily Development Routine

### Startup Sequence
1. **Start Infrastructure:** Spin up Docker containers (`docker compose up -d`) and verify PostgreSQL (`pgvector`) is active on port `5432`.
2. **Verify Local Services:** Ensure Ollama is running in the background for local LLM inference (`llama3.2`).
3. **Activate Environment:** Load your Python virtual environment (`.\venv\Scripts\Activate`).

### Day-End Shutdown Routine
1. **Commit Changes:** Stage and commit your work using conventional commit messages (`git add .` then `git commit -m "feat: [description]"`).
2. **Stop Containers:** Gracefully stop local databases while preserving persistent volumes (`docker compose down`).
3. **Free System RAM (Windows/WSL):** Clear background Linux VMs if necessary (`wsl --shutdown`).
4. **Deactivate:** Exit the active Python environment (`deactivate`).

---

## 💻 2. Local Setup & Installation

### Prerequisites
* Python 3.10+
* Docker & Docker Compose
* [Ollama](https://ollama.com/) (running locally)

### Clone & Configure
    # Clone the repository
    git clone https://github.com/your-username/ai-engineering-sprint.git
    cd ai-engineering-sprint

    # Copy environment configuration
    cp .env.example .env

### Python Virtual Environment
```bash
# Create and activate virtual environment (Windows PowerShell)
python -m venv venv
.\venv\Scripts\Activate

# Install project dependencies
pip install -r requirements.txt
```

---

## 🏃 3. Running the Application Services

### Initialize Infrastructure & Model
```bash
# 1. Start PostgreSQL with pgvector
docker compose up -d

# 2. Pull local model in Ollama
ollama pull llama3.2
```

### Run Services (Dual Terminal Setup)
```bash    
# Terminal 1: Launch FastAPI Backend (Docs at http://localhost:8000/docs)
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Launch Streamlit Frontend UI (Opens at http://localhost:8501)
streamlit run app_ui.py
```

---

## 🧪 4. Testing & Scientific Evaluation
```bash   
# To verify pipeline quality and check benchmark scores (Faithfulness, Answer Relevancy, Context Precision/Recall) using Ragas:
python evaluate_rag.py

# This executes the automated evaluation suite against your golden dataset and exports metrics to evaluation_report.csv.
```

---

## 🧹 5. Database Maintenance & Reset Procedures

### If your vector database encounters schema conflicts or requires a fresh ingestion run:
```bash
# Tear down containers and clear persistent volumes:
docker compose down -v
    
# Restart fresh container instances:
docker compose up -d

# Re-run document ingestion and embedding generation:
python pdf_ingest.py
```