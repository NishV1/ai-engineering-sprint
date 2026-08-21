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
* **[Day 4] Interactive CLI Search Interface:** *(Upcoming)* Live terminal queries searching through vector chunks with real-time similarity metrics.
* **[Future Days] Advanced Features:** Hybrid Search (BM25 + Dense Vectors), Cross-Encoder Rerankers, Ragas Evaluation, and Agentic Workflows via LangGraph.

---

## 📂 Project Structure

```text
├── .github/                # GitHub templates & configurations
├── docker-compose.yml      # Containerized PostgreSQL service
├── db_test.py              # Day 1: Vector storage & basic database checks
├── chunking_test.py        # Day 2: Semantic text splitting & embedding generation
├── pdf_ingest.py           # Day 3: Multi-page PDF parser & metadata injector
├── DEV_WORKFLOW.md         # Standard operating procedures & engineering playbook
├── SESSION_JOURNEY.md      # Architectural logs, design decisions & reviews
└── GLOSSARY.md             # Beginner-friendly AI dictionary & technical reference