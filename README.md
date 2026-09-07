# 🚀 Production-Grade RAG & Agentic AI Sprint

A comprehensive, production-ready Retrieval-Augmented Generation (RAG) and AI engineering pipeline built from scratch. This project showcases advanced workflows including containerized vector infrastructure, smart recursive chunking, metadata-backed citations, local transformer embeddings, and scalable architecture design.

---

## 🛠️ Tech Stack & Architecture

* **Core Language:** Python
* **Infrastructure:** Docker, Docker Compose
* **Database & Vector Search:** PostgreSQL with `pgvector`
* **Orchestration & Processing:** LangChain, Sentence-Transformers (`all-MiniLM-L6-v2`)
* **Document Parsing:** `PyPDFLoader` (Multi-page lineage & metadata extraction)

---

## 🗺️ Sprint Roadmap & Progress

* **[Day 1] Infrastructure & Vector Storage:** Setting up Dockerized PostgreSQL, configuring native vector types, and running vector math (`pgvector`, `psycopg2`, cosine distance).
* **[Day 2] Smart Chunking & Batch Embeddings:** Implementing LangChain's `RecursiveCharacterTextSplitter` and generating local 384-dimensional dense embeddings in batches.
* **[Day 3] Real PDF Ingestion & Metadata Tracking:** Parsing multi-page documentation with persistent source lineages (`source_file`, `page_number`) to eliminate hallucinations and enable verifiable citations.
* **[Day 4-5] Local Generative RAG & LLM Integration:** Air-gapped orchestration using Ollama (`llama3.2`) and LangChain to synthesize grounded answers with end-to-end page-level citations.
* **[Day 6] Advanced Retrieval Architecture:** Hybrid Search combining dense vector embeddings with BM25 keyword matching via Reciprocal Rank Fusion (RRF), paired with a Cross-Encoder Reranker (`ms-marco-MiniLM-L-6-v2`).
* **[Future Days] Advanced Features:** Ragas Evaluation, FastAPI Backend, and Agentic Workflows via LangGraph.

---

## 📂 Project Structure

├── .github/                # GitHub templates & configurations
├── docker-compose.yml      # Containerized PostgreSQL service
├── db_test.py              # Day 1: Vector storage & basic database checks
├── chunking_test.py        # Day 2: Semantic text splitting & embedding generation
├── pdf_ingest.py           # Day 3: Multi-page PDF parser & metadata injector
├── generative_rag.py       # Day 5: Offline generative RAG pipeline with Ollama
├── hybrid_rag.py           # Day 6: Hybrid search (BM25 + Vector) & Cross-Encoder reranking
├── DEV_WORKFLOW.md         # Standard operating procedures & engineering playbook
├── SESSION_JOURNEY.md      # Architectural logs, design decisions & reviews
└── GLOSSARY.md             # Beginner-friendly AI dictionary & technical reference

---

## 🚀 Getting Started

### 1. Clone the Repository
git clone [https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git)
cd YOUR_REPOSITORY_NAME

### 2. Spin Up Infrastructure
Start your containerized vector database using Docker Compose:
docker compose up -d

### 3. Set Up Python Environment
python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\Activate
pip install -r requirements.txt

---

## 📖 Documentation & Playbooks
For a deeper dive into our architectural choices, engineering decisions, and daily study notes, check out:
* Workflow Playbook (`DEV_WORKFLOW.md`)
* Session Journey & Tidbits (`SESSION_JOURNEY.md`)
* Living Glossary (`GLOSSARY.md`)