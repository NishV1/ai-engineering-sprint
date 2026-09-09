# 🚀 Production-Grade RAG & Agentic AI Sprint

A comprehensive, production-ready Retrieval-Augmented Generation (RAG) and AI engineering pipeline built from scratch. This project showcases advanced workflows including containerized vector infrastructure, smart recursive chunking, metadata-backed citations, local transformer embeddings, hybrid search, cross-encoder reranking, FastAPI backend services, automated pipeline evaluation, and scalable architecture design.

---

## 🛠️ 1. Tech Stack & Architecture

* **Core Language:** Python
* **Infrastructure:** Docker, Docker Compose
* **Database & Vector Search:** PostgreSQL with `pgvector`
* **Backend & API:** FastAPI, Uvicorn (Asynchronous REST API)
* **Frontend UI:** Streamlit (Interactive Chat & Citation Interface)
* **Orchestration & Processing:** LangChain, Sentence-Transformers (`all-MiniLM-L6-v2`)
* **Retrieval & Reranking:** BM25 (`rank_bm25`), Reciprocal Rank Fusion (RRF), Cross-Encoder (`ms-marco-MiniLM-L-6-v2`)
* **Local LLM Engine & Evaluation Judge:** Ollama (`llama3.2`)
* **Document Parsing:** `PyPDFLoader` (Multi-page lineage & metadata extraction)
* **Evaluation Framework:** Ragas (Faithfulness, Answer Relevancy, Context Precision/Recall)

## 🗺️ 2. Sprint Roadmap & Progress

* **[Day 1] Infrastructure & Vector Storage:** Setting up Dockerized PostgreSQL, configuring native vector types, and running vector math (`pgvector`, `psycopg2`, cosine distance).
* **[Day 2] Smart Chunking & Batch Embeddings:** Implementing LangChain's `RecursiveCharacterTextSplitter` and generating local 384-dimensional dense embeddings in batches.
* **[Day 3] Real PDF Ingestion & Metadata Tracking:** Parsing multi-page documentation with persistent source lineages (`source_file`, `page_number`) to eliminate hallucinations and enable verifiable citations.
* **[Day 4-5] Local Generative RAG & LLM Integration:** Air-gapped orchestration using Ollama (`llama3.2`) and LangChain to synthesize grounded answers with end-to-end page-level citations.
* **[Day 6] Advanced Retrieval Architecture:** Hybrid Search combining dense vector embeddings with BM25 keyword matching via Reciprocal Rank Fusion (RRF), paired with a Cross-Encoder Reranker (`ms-marco-MiniLM-L-6-v2`).
* **[Day 7] Production REST API, Streamlit UI, & Dynamic Ingestion Architecture:** Exposing the hybrid RAG pipeline via FastAPI (`app.py`), building an interactive chat frontend (`app_ui.py`), and mapping out multi-document runtime ingestion.
* **[Day 8] Scientific Rigor & Automated Evaluation (Ragas):** Implementing automated pipeline benchmarking for faithfulness, answer relevancy, and context recall running completely air-gapped via a local Ollama judge.
* **[Day 9] Dynamic File Ingestion Execution:** Building runtime file upload capabilities (`/upload` API + Streamlit file uploader) for multi-document scaling.
* **[Future Days] Advanced Features:** Agentic Workflows via LangGraph.

## 📂 3. Project Structure

* `docker-compose.yml` — Containerized PostgreSQL service
* `db_test.py` — Day 1: Vector storage & basic database checks
* `chunking_test.py` — Day 2: Semantic text splitting & embedding generation
* `pdf_ingest.py` — Day 3: Multi-page PDF parser & metadata injector
* `generative_rag.py` — Day 5: Offline generative RAG pipeline with Ollama
* `hybrid_rag.py` — Day 6: Hybrid search (BM25 + Vector) & Cross-Encoder reranking
* `app.py` — Day 7: FastAPI backend service for hybrid RAG
* `app_ui.py` — Day 7: Streamlit interactive chat UI
* `evaluate_rag.py` — Day 8: Automated Ragas evaluation harness & benchmarking script
* `evaluation_report.csv` — Day 8: Exported benchmark metrics report
* `ARCHITECTURE.md` — System data flow and architectural trade-offs
* `DEV_WORKFLOW.md` — Project-specific quickstart & operational workflow
* `SESSION_JOURNEY.md` — Chronological sprint diary & interview soundbites
* `PLAYBOOK.md` — Universal AI engineering standards & best practices
* `GLOSSARY.md` — Beginner-friendly AI dictionary & technical reference

## 🚀 4. Getting Started

### Clone & Configure Environment
```bash
git clone [https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git)
cd YOUR_REPOSITORY_NAME
cp .env.example .env
```
### Spin Up Infrastructure
```bash
docker compose up -d
```
### Python Virtual Environment & Dependencies
```bash
python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\Activate
pip install -r requirements.txt
```
### Run Application Services
```bash
# Terminal 1: Launch FastAPI Backend
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Launch Streamlit Frontend UI
streamlit run app_ui.py
```
### Run Automated Evaluation
```bash
python evaluate_rag.py
```

## 📖 5. Documentation & Playbooks

For a deeper dive into our architectural choices, engineering decisions, and daily study notes, check out:
* [System Architecture](./ARCHITECTURE.md)
* [Quickstart Workflow](./DEV_WORKFLOW.md)
* [Universal Engineering Playbook](./PLAYBOOK.md)
* [Sprint Journey & Engineering Log](./SESSION_JOURNEY.md)
* [Living Glossary](./GLOSSARY.md)