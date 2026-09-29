# 🚀 Production-Grade RAG & Agentic AI Sprint

A comprehensive, production-ready Retrieval-Augmented Generation (RAG) and AI engineering pipeline built from scratch[cite: 6]. This project showcases advanced workflows including containerized vector infrastructure, smart recursive chunking, metadata-backed citations, local transformer embeddings, document-scoped hybrid search, cross-encoder reranking, FastAPI backend services, backend health polling, dynamic file ingestion, automated pytest unit testing, continuous integration, and automated retrieval benchmarking.

---

## 🛠️ 1. Tech Stack & Architecture

* **Core Language:** Python 3.11
* **Infrastructure & Containerization:** Docker, Docker Compose
* **Database & Vector Search:** PostgreSQL 17 with `pgvector` (`aidb` database)
* **Backend & API:** FastAPI, Uvicorn (Asynchronous REST API with `/health`, `/upload`, `/files`, and `/query` endpoints)
* **Frontend UI:** Streamlit (Interactive Chat & Citation Interface with Document Scoping & Health Status Polling)
* **Orchestration & Processing:** LangChain, Sentence-Transformers (`all-MiniLM-L6-v2`)
* **Retrieval & Reranking:** BM25 (`rank_bm25`), Reciprocal Rank Fusion (RRF, $k=60$), Cross-Encoder (`ms-marco-MiniLM-L-6-v2`)
* **Local LLM Engine & Evaluation Judge:** Ollama (`llama3.2` running in a containerized service with volume persistence)
* **Document Parsing:** `PyPDFLoader` (Multi-page lineage & page-number tracking), `RecursiveCharacterTextSplitter`
* **Testing & Continuous Integration:** `pytest`, `pytest-cov`, GitHub Actions (`ci.yml`)
* **Evaluation Framework:** `evaluate_retrieval.py` (Hit-Rate@K, Mean Reciprocal Rank - MRR)

## 🗺️ 2. Sprint Roadmap & Progress

* **[Day 1] Infrastructure & Vector Storage:** Setting up Dockerized PostgreSQL with `pgvector`, provisioning schemas dynamically, and executing vector math (cosine distance via `psycopg2`).
* **[Day 2] Smart Chunking & Batch Embeddings:** Implementing LangChain's `RecursiveCharacterTextSplitter` (chunk size: 500, overlap: 50) and batch-generating local 384-dimensional dense embeddings.
* **[Day 3] Real PDF Ingestion & Metadata Tracking:** Parsing multi-page documentation with persistent source lineages (`source_file`, `page_number`) to eliminate hallucinations and enable verifiable citations.
* **[Day 4-5] Local Generative RAG & LLM Integration:** Air-gapped orchestration using containerized Ollama (`llama3.2`) and LangChain to synthesize grounded answers with end-to-end page-level citation.
* **[Day 6] Advanced Retrieval Architecture:** Hybrid Search combining dense vector embeddings with BM25 keyword matching via Reciprocal Rank Fusion (RRF, $k=60$), paired with a Cross-Encoder Reranker (`ms-marco-MiniLM-L-6-v2`).
* **[Day 7] Production REST API, Streamlit UI, & Dynamic Ingestion Architecture:** Exposing the hybrid RAG pipeline via FastAPI (`app.py`), building an interactive chat frontend (`app_ui.py`), and mapping out multi-document runtime ingestion.
* **[Day 8] Document Scoping & Context Isolation:** Implementing document-scoped filtering to prevent cross-PDF context bleeding and adding backend health-check polling (`/health`) for resilient UI initialization.
* **[Day 9] Dynamic File Ingestion Execution:** Building runtime file upload capabilities (`/upload` API + Streamlit file uploader) with auto-healing table schema creation and hot-reloading active file inventory.
* **[Day 10] Containerization & Multi-Service Architecture:** Orchestrating PostgreSQL/pgvector, FastAPI backend, Streamlit UI, and containerized Ollama via Docker Compose with environment-agnostic configuration (`os.getenv`).
* **[Day 11] Automated Testing, CI/CD Pipeline & Quantitative Evaluation:** Implementing a `pytest` unit testing suite with isolated mocks, creating an automated GitHub Actions CI workflow (`ci.yml`), and benchmarking retrieval performance (100.00% Hit-Rate@5 and 1.0000 MRR across ground-truth evaluation sets).

## 📂 3. Project Structure

* `.github/workflows/ci.yml` — Continuous Integration workflow (service containers, schema init, sample seeding, pytest, evaluation)
* `docker-compose.yml` — Containerized multi-service PostgreSQL, FastAPI, Streamlit, and Ollama stack
* `Dockerfile.backend` — Docker build recipe for FastAPI backend service & heavy ML models
* `Dockerfile.frontend` — Docker build recipe for Streamlit web interface
* `app.py` — FastAPI backend service with self-healing DB schema, hybrid search (Vector + BM25), RRF, document scoping, and Cross-Encoder reranking
* `app_ui.py` — Streamlit interactive chat UI with backend health polling, document scoping selector, and dynamic file inventory
* `test_app.py` — Automated `pytest` suite for backend REST endpoints using isolated ML and database mocks
* `evaluate_retrieval.py` — Quantitative retrieval evaluation harness measuring Hit-Rate@K and MRR with mismatch diagnostics
* `requirements.txt` — Python dependencies for backend, frontend, testing, and CI services
* `uploaded_docs/` — Directory storing dynamically ingested PDF files
* `ARCHITECTURE.md` — System data flow, component interactions, and architectural trade-offs
* `DEV_WORKFLOW.md` — Project-specific quickstart, operational workflow, and unit testing guidelines
* `SESSION_JOURNEY.md` — Chronological sprint diary & interview soundbites
* `PLAYBOOK.md` — Universal AI engineering standards & best practices
* `GLOSSARY.md` — Beginner-friendly AI dictionary & technical reference

## 🚀 4. Getting Started

### Clone & Configure Environment
```bash
git clone https://github.com/NishV1/ai-engineering-sprint.git
cd ai-engineering-sprint
cp .env.example .env
```
### Python Virtual Environment & Dependencies
```bash
python -m venv venv

# On Windows PowerShell:
.\venv\Scripts\Activate
# On Linux/macOS:
source venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pytest pytest-cov
```
## 🐳 5. Running Options

### Option A: Fully Containerized Stack (Production Mode)
Spin up the entire multi-service ecosystem using Docker Compose:
```bash
# 1. Build and launch containers
docker compose up --build -d

# 2. Pull Llama 3.2 model inside the Ollama container (One-time setup)
docker exec -it rag_ollama ollama pull llama3.2
```
* Streamlit UI: http://localhost:8501
* FastAPI Docs: http://localhost:8000/docs
* Backend Health Endpoint: http://localhost:8000/health

### Option B: Local Hybrid Development (Dual Terminal Setup)
```bash
# 1. Start PostgreSQL vector database container
docker compose up -d postgres_vector

# Terminal 1: Launch FastAPI Backend (with auto-reload)
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Launch Streamlit UI
streamlit run app_ui.py
```

## 🧪 6. Automated Testing & Evaluation
```bash
# Run Automated Unit & Route Test Suite (pytest)
pytest test_app.py -v --cov=app --cov-report=term-missing

# Run Quantitative Retrieval Evaluation
python evaluate_retrieval.py

# Run Automated Pipeline Quality Evaluation (Ragas)
python evaluate_rag.py
```

### Benchmark Performance Output

=============================================
📈 RETRIEVAL PERFORMANCE RESULTS
=============================================
Total Test Queries : 2
Hit-Rate@5         : 100.00%
MRR                : 1.0000
=============================================

### Continuous Integration (GitHub Actions)

The repository automatically executes `.github/workflows/ci.yml` on every push or pull request to `master` or `main`:

1. Launches PostgreSQL 17 + `pgvector` container (`aidb`).
2. Initializes vector extension and `document_chunks` table schema.
3. Executes `pytest test_app.py` with mock isolation and code coverage calculation.
4. Seeds benchmark embeddings using `SentenceTransformer('all-MiniLM-L6-v2')`.
5. Runs `evaluate_retrieval.py` against live vector indices.
6. Uploads `evaluation_report.csv` as a downloadable build artifact.

## 📖 7. Documentation & Playbooks

For a deeper dive into our architectural choices, engineering decisions, and daily study notes, check out:
* [System Architecture](./ARCHITECTURE.md)
* [Quickstart & Dev Workflow](./DEV_WORKFLOW.md)
* [Universal Engineering Playbook](./PLAYBOOK.md)
* [Sprint Journey & Engineering Log](./SESSION_JOURNEY.md)
* [Living Glossary](./GLOSSARY.md)