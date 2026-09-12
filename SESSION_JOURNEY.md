# 🚀 AI Engineering Sprint: Session Journey & Tidbits

This document logs the daily architectural concepts, engineering decisions, technical takeaways, and structured reviews from each session of the sprint.

---

## 🟢 Day 1: Infrastructure & Vector Storage Basics
* **Core Goal:** Spin up an isolated development environment and store/query mathematical vectors in a traditional relational database.
* **Key Technologies:** Docker, Docker Compose, PostgreSQL 17, `pgvector`, `psycopg2`.
* **Engineering Tidbits & Review:**
  * *Containerization vs. Local Install:* Using Docker prevents environment drift and version conflicts. Volume mounting (`pgdata`) ensures data persistence across container teardowns.
  * *Vector Registration:* Standard database drivers don't understand arrays natively. Registering the vector extension (`register_vector(conn)`) hooks into `psycopg2`'s type-casting engine to serialize Python lists directly into PostgreSQL's internal binary format for `pgvector`.
  * *Cosine Distance (`<=>`):* Computes the cosine of the angle between two vectors in high-dimensional space, ignoring magnitude. A score of `0.0` means semantically identical; scores closer to `2.0` mean unrelated.
  * *Interview Framing:* "For my infrastructure, I avoid local machine installations by using Docker and Docker Compose to spin up a containerized PostgreSQL instance. To handle unstructured data, I extend PostgreSQL with `pgvector`, allowing me to store high-dimensional embeddings natively alongside structured relational data."

---

## 🔵 Day 2: Document Ingestion & Smart Chunking
* **Core Goal:** Transition from hardcoded strings to automated Extract, Transform, Load (ETL) pipelines for unstructured text.
* **Key Technologies:** LangChain, Sentence-Transformers (`all-MiniLM-L6-v2`), PyTorch.
* **Engineering Tidbits & Review:**
  * *Recursive Semantic Chunking:* Naive splitting cuts text arbitrarily. LangChain's `RecursiveCharacterTextSplitter` takes a hierarchical approach using a prioritized list of separators (`\n\n`, `\n`, ` `, ``) to keep paragraphs and sentences intact.
  * *Chunk Overlap:* Ensures context isn't lost at boundaries by repeating a portion of the end of Chunk $N$ at the beginning of Chunk $N+1$.
  * *Local Model Inference:* Loading `SentenceTransformer` locally tokenizes text, passes it through transformer attention layers, and outputs dense 384-dimensional matrices.
  * *Interview Framing:* "To handle long-form or unstructured documents, I implement a recursive character chunking strategy to preserve semantic flow. I then pass those chunks through a local sentence-transformer model to generate dense vector embeddings in batches, securely storing them inside a PostgreSQL database powered by pgvector."

---

## 🟣 Day 3: Real PDF Ingestion & Metadata Tracking
* **Core Goal:** Ingest real-world multi-page documents and associate them with verifiable source citations.
* **Key Technologies:** `PyPDFLoader`, `langchain-community`, Structured Relational Mapping.
* **Engineering Tidbits & Review:**
  * *Metadata Lineage:* Storing `source_file` and `page_number` alongside vector embeddings ensures traceability and minimizes LLM hallucinations by enabling verifiable source citations.
  * *Idempotency & Self-Healing:* Designing scripts with `DROP TABLE IF EXISTS` and `CREATE EXTENSION IF NOT EXISTS` ensures pipelines automatically reconcile database states to match required schemas after environment resets.
  * *Interview Framing:* "I use `PyPDFLoader` to extract text while maintaining document lineage by capturing metadata like page numbers and source filenames. This allows for 'Source Attribution,' where the application retrieves a verifiable reference alongside the answer, which is critical for building user trust."

---

## 🟡 Day 4: Unified Ingestion & CLI Search Engine
* **Core Goal:** Consolidate PDF parsing, vector storage, and interactive search into a single self-healing application (`rag_app.py`).
* **Key Technologies:** LangChain PDF loaders, Sentence-Transformers (`all-MiniLM-L6-v2`), PostgreSQL (`pgvector`), Python CLI loops.
* **Engineering Tidbits & Review:**
  * *Unified Architecture:* Combining ingestion and search into one script eliminates database and schema mismatch errors across separate scripts.
  * *Idempotent Pre-flight Checks:* Programmatically verifying database existence, enabling the `vector` extension, and checking chunk counts before triggering ingestion makes the application robust and production-ready.
  * *Interview Framing:* "For Day 4, I engineered a unified RAG engine that checks database state, self-heals schemas and vector extensions, processes multi-page technical manuals into dense vector embeddings, and exposes a real-time semantic CLI search terminal with source and page-level citations."

---

## 🟢 Day 5: Generative RAG & Local LLM Integration

### 📊 Architectural Review & Design Decisions
* **Private, Air-Gapped Stack:** Deployed a fully offline pipeline combining PostgreSQL (`pgvector`), `sentence-transformers` (`all-MiniLM-L6-v2`), and local `llama3.2` via Ollama and LangChain (`ChatOllama`). This guarantees zero external data leakage and eliminates cloud API latency.
* **Strict Context Grounding:** Implemented prompt constraints that restrict the LLM to utilizing *only* the retrieved database chunks, eliminating hallucination risks and enforcing deterministic synthesis.
* **End-to-End Citation Lineage:** Preserved metadata (`source_file` and `page_number`) from PDF ingestion through vector similarity search to final LLM output generation, ensuring complete auditability.

### 🎙️ Interview Soundbites & Engineering Defense
* **On Local Privacy:** *"When architecting our RAG pipeline, I prioritized a local-first stack using Ollama and pgvector. This ensures complete data sovereignty and complies with strict enterprise governance where proprietary documents cannot touch external cloud APIs."*
* **On Combating Hallucinations:** *"To ensure production-grade reliability, I enforced strict prompt-level grounding. By forcing the model to rely solely on retrieved PostgreSQL chunks and cite exact page numbers, I eliminated unverified extrapolations."*
* **On Traceability:** *"Maintainability in RAG requires robust metadata flow. I engineered our ingestion and database schema to track document lineage end-to-end, making debugging and source verification trivial for end users."*

---

## 🟢 Day 6: Advanced Retrieval Architecture (Hybrid Search & Reranking)

### 📊 Architectural Review & Design Decisions
* **Hybrid Retrieval (Vector + BM25):** Combined dense semantic vector search (via PostgreSQL `pgvector` and Sentence-Transformers) with lexical keyword matching (`rank_bm25`). This bridges the gap between conceptual understanding and exact-match precision for specific model numbers, acronyms, or part numbers.
* **Reciprocal Rank Fusion (RRF):** Integrated RRF ($k=60$) to cleanly merge semantic and keyword result lists without requiring complex score normalization, ensuring a robust candidate pool.
* **Cross-Encoder Reranking:** Deployed a local cross-encoder (`cross-encoder/ms-marco-MiniLM-L-6-v2`) to evaluate query-document pairs simultaneously in deeper transformer layers, filtering out noisy candidates and passing only top-scoring chunks to the local LLM.

### 🎙️ Interview Soundbites & Engineering Defense
* **On Overcoming Vector Search Limitations:** *"While dense vector embeddings excel at semantic matching, they often fail on exact keyword or serial number lookups. On Day 6, I engineered a hybrid retrieval system combining PostgreSQL vector similarity with BM25 lexical search, merged via Reciprocal Rank Fusion."*
* **On Precision Reranking:** *"To optimize context quality and prevent context window pollution, I introduced a cross-encoder reranking layer. Instead of relying solely on bi-encoder distance metrics, the cross-encoder deeply scores query-chunk relevance, significantly boosting retrieval precision before handing data off to Ollama."*

---

## 🟢 Day 7: Production REST API (FastAPI), Streamlit UI, & Dynamic Ingestion Architecture

### 📊 Architectural Review & Design Decisions
* **FastAPI Service Layer (`app.py`):** Wrapped the hybrid search and cross-encoder reranking engine into an asynchronous REST API (`/query`). Initialized and cached models and BM25 indices globally at startup to minimize per-request latency.
* **Interactive Chat Interface (`app_ui.py`):** Built a responsive frontend using Streamlit to provide a visual chat experience with live assistant responses, session history, and page-level source citations.
* **Dynamic Ingestion Architecture:** Mapped out the multi-document ingestion strategy, establishing the blueprint for runtime ingestion via a FastAPI `/upload` endpoint and Streamlit file uploader widget.

### 🎙️ Interview Soundbites & Engineering Defense
* **On Moving from Scripts to Services:** *"On Day 7, I transitioned the RAG pipeline from an offline CLI script into a production-grade FastAPI backend service, enabling asynchronous handling, structured Pydantic data validation, and automated Swagger documentation."*
* **On Full-Stack AI Engineering & System Design:** *"To bridge the backend to users, I built a companion Streamlit chat interface that preserves session state and renders verifiable page citations, while also designing the runtime dynamic ingestion architecture for multi-document scalability."*

---

## 🔵 Day 8: Document Scoping, Self-Healing Endpoints & UI Health Polling

### 📊 Architectural Review & Design Decisions
* **Document-Scoped Filtering:** Added an optional `selected_file` parameter to `/query` to allow users to target queries to specific PDFs or perform global searches across all ingested documents. This completely eliminates cross-document context bleeding.
* **Self-Healing File Inventory (`/files`):** Refactored `/files` to auto-provision missing tables (`CREATE TABLE IF NOT EXISTS`) and return a clean empty payload (`{"files": []}`) instead of throwing HTTP 500 errors when queried before initial file upload.
* **Startup Health Polling (`/health`):** Created a dedicated `/health` endpoint in FastAPI and wired it to Streamlit using `st.status`. The UI displays a live loading indicator while transformer models and BM25 indices initialize, automatically unlocking once backend readiness is confirmed.

### 🎙️ Interview Soundbites & Engineering Defense
* **On Eliminating Context Bleeding:** *"When ingesting disparate document domains—like technical manuals and literature—global vector searches can pull conflicting context into the prompt. On Day 8, I engineered document-scoped metadata filtering across both `pgvector` and BM25 retrieval layers, guaranteeing strict context isolation."*
* **On Resilient User Experience:** *"Heavy transformer models take time to load on warm startup. Instead of letting the frontend fail with connection errors, I implemented a health-check polling pattern using Streamlit's `st.status`, providing real-time visual initialization feedback to the user."*

---

## 🟢 Day 9: Dynamic File Ingestion Execution

### 📊 Architectural Review & Design Decisions
* **Runtime PDF Ingestion API (`/upload`):** Extended FastAPI to accept multi-document PDF uploads, executing batch embedding generation (`sentence-transformers`) and bulk database insertions (`psycopg2.extras.execute_values`) on the fly.
* **Corpus Synchronization:** Hot-loaded the in-memory BM25 index and chunk lookup dictionaries immediately following database insertion, ensuring newly ingested documents are instantly searchable without server restarts.
* **Interactive Sidebar Inventory:** Enhanced Streamlit with dynamic document inventory listings, file selector dropdowns for target scoping, and automated UI reruns (`st.rerun()`) upon successful upload.

### 🎙️ Interview Soundbites & Engineering Defense
* **On Moving from Static to Dynamic Pipelines:** *"Static RAG applications break down when users need to inject new documents on the fly. On Day 9, I engineered a dynamic runtime ingestion pipeline featuring bulk batch database insertion and automated BM25 corpus re-indexing, allowing users to upload PDFs directly through the UI without restarting the backend."*

---

## 📅 Day 10: Containerization & Multi-Service Orchestration

### 📊 Architectural Review & Design Decisions
* **Unified Container Ecosystem:** Configured `docker-compose.yml` to orchestrate four dedicated microservices: PostgreSQL (`postgres_vector`), FastAPI backend (`rag_fastapi_backend`), Streamlit UI (`rag_streamlit_ui`), and local Ollama (`rag_ollama`).
* **Air-Gapped Container Networking:** Configured internal Docker bridge networking so FastAPI communicates with Ollama directly over `http://ollama:11434`, removing host network dependencies and resolving host port collision errors (`bind: 11434`).
* **Volume Persistence:** Attached named volumes (`pgdata`, `ollama_storage`) to retain vectorized chunks and pulled LLM weights (`llama3.2`) across container teardowns and rebuilds.

### 🎙️ Interview Soundbites & Engineering Defense
* **On Containerized LLM Orchestration:** *"I containerized our entire hybrid RAG pipeline using Docker Compose, isolating PostgreSQL with pgvector, FastAPI, Streamlit, and Ollama into a unified network with persistent data volumes for zero external network dependencies."*
* **On Resolving Port Collisions:** *"When deploying Ollama in Docker alongside host installations, port conflicts on 11434 are common. I resolved this by scoping host bindings and establishing container-to-container internal routing via Docker's bridge network (`http://ollama:11434`)."*

---

## 📅 Day 11: Production-Grade Automated Testing & Retrieval Evaluation

### 📊 Architectural Review & Design Decisions
* **Automated Retrieval Evaluation (`evaluate_retrieval.py`):** Built a metrics harness to benchmark Hit-Rate@K and Mean Reciprocal Rank (MRR) across indexed documents. Implemented diagnostic mismatch logging to trace source and page discrepancies.
* **Benchmark Performance Achieved:** Achieved **100.00% Hit-Rate@5** and **1.0000 MRR** across 7,800+ indexed chunks, validating that the combination of `pgvector`, BM25, RRF ($k=60$), and Cross-Encoder reranking places ground-truth candidate chunks in rank position #1.
* **Automated Unit Testing (`pytest`):** Implemented unit and endpoint test suites using FastAPI `TestClient`, leveraging `unittest.mock` (`MagicMock`, `@patch`) to mock database queries, dense transformer models, BM25 indices, and LLM synthesis.

### 🎙️ Interview Soundbites & Engineering Defense
* **On Quantitative Retrieval Benchmarking:** *"To move beyond subjective evaluation, I built a quantitative benchmarking harness measuring Hit-Rate@K and MRR. Testing against 7,800+ chunks proved that our Hybrid RRF and Cross-Encoder pipeline delivers a 100% Hit-Rate@5 and 1.0000 MRR."*
* **On Unit Testing Machine Learning Pipelines:** *"Testing AI pipelines requires isolating heavy model execution. Using `pytest` and `unittest.mock`, I mocked vector store interactions and embedding models, creating an automated test suite that executes in seconds while ensuring full API contract compliance."*