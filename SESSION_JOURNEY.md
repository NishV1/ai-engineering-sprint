# 🚀 AI Engineering Sprint: Session Journey & Tidbits

This document logs the daily architectural concepts, engineering decisions, technical takeaways, and structured reviews from each session of the sprint.

---

## 🟢 Day 1: Infrastructure & Vector Storage Basics
* **Core Goal:** Spin up an isolated development environment and store/query mathematical vectors in a traditional relational database.
* **Key Technologies:** Docker, Docker Compose, PostgreSQL, `pgvector`, `psycopg2`.
* **Engineering Tidbits & Review:**
  * *Containerization vs. Local Install:* Using Docker prevents environment drift and version conflicts. Volume mounting (`pgdata`) ensures data persistence across container teardowns.
  * *Vector Registration:* Standard database drivers don't understand arrays. Registering the vector extension (`register_vector(conn)`) hooks into `psycopg2`'s type-casting engine to serialize Python lists directly into PostgreSQL's internal binary format for `pgvector`.
  * *Cosine Distance (`<=>`):* Computes the cosine of the angle between two vectors in a high-dimensional space, ignoring magnitude. A score of `0.0` means semantically identical; scores closer to `2.0` mean unrelated.
  * *Interview Framing:* "For my infrastructure, I avoid local machine installations by using Docker and Docker Compose to spin up a containerized PostgreSQL instance. To handle unstructured data, I extend PostgreSQL with `pgvector`, allowing me to store high-dimensional embeddings natively alongside structured relational data."

---

## 🔵 Day 2: Document Ingestion & Smart Chunking
* **Core Goal:** Transition from hardcoded strings to automated Extract, Transform, Load (ETL) pipelines for unstructured text.
* **Key Technologies:** LangChain, Sentence-Transformers (`all-MiniLM-L6-v2`), PyTorch.
* **Engineering Tidbits & Review:**
  * *Recursive Semantic Chunking:* Naive splitting cuts text arbitrarily. LangChain's `RecursiveCharacterTextSplitter` takes a hierarchical approach using a prioritized list of separators (`\n\n`, `\n`, ` `, ``) to keep paragraphs and sentences together.
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

## 🟢 Day 5: Generative RAG & Local LLM Integration (Review & Retrospective)

### 📊 Architectural Review & Design Decisions
* **Private, Air-Gapped Stack:** Successfully deployed a fully offline pipeline combining PostgreSQL (`pgvector`), `sentence-transformers` (`all-MiniLM-L6-v2`), and local `llama3.2` via Ollama and LangChain (`ChatOllama`). This guarantees zero external data leakage and eliminates cloud API latency.
* **Strict Context Grounding:** Implemented rigorous prompt constraints that restrict the LLM to utilizing *only* the retrieved database chunks. This eliminates hallucination risks and enforces deterministic answering.
* **End-to-End Citation Lineage:** Preserved metadata (source filename and exact page numbers) from initial PDF ingestion through vector similarity search all the way to final LLM output generation, ensuring complete auditability.

### 🎙️ Interview Soundbites & Engineering Defense
* **On Local Privacy:** *"When architecting our RAG pipeline, I prioritized a local-first stack using Ollama and pgvector. This ensures complete data sovereignty and complies with strict enterprise governance where proprietary documents cannot touch external cloud APIs."*
* **On Combating Hallucinations:** *"To ensure production-grade reliability, I enforced strict prompt-level grounding. By forcing the model to rely solely on retrieved PostgreSQL chunks and cite exact page numbers, I eliminated unverified extrapolations."*
* **On Traceability:** *"Maintainability in RAG requires robust metadata flow. I engineered our ingestion and database schema to track document lineage end-to-end, making debugging and source verification trivial for end users."*

---

## 🟢 Day 6: Advanced Retrieval Architecture (Hybrid Search & Reranking)

### 📊 Architectural Review & Design Decisions
* **Hybrid Retrieval (Vector + BM25):** Combined dense semantic vector search (via PostgreSQL `pgvector` and Sentence-Transformers) with lexical keyword matching (`rank-bm25`). This bridges the gap between conceptual understanding and exact-match precision for specific model numbers, acronyms, or part numbers.
* **Reciprocal Rank Fusion (RRF):** Integrated RRF to cleanly merge semantic and keyword result lists without requiring complex score normalization, ensuring a robust and balanced candidate pool.
* **Cross-Encoder Reranking:** Deployed a local cross-encoder (`cross-encoder/ms-marco-MiniLM-L-6-v2`) to evaluate query-document pairs simultaneously in deeper transformer layers. This filters out noisy candidates and passes only the absolute sharpest chunks to the local LLM.

### 🎙️ Interview Soundbites & Engineering Defense
* **On Overcoming Vector Search Limitations:** *"While dense vector embeddings excel at semantic matching, they often fail on exact keyword or serial number lookups. On Day 6, I engineered a hybrid retrieval system combining PostgreSQL vector similarity with BM25 lexical search, merged via Reciprocal Rank Fusion."*
* **On Precision Reranking:** *"To optimize context quality and prevent context window pollution, I introduced a cross-encoder reranking layer. Instead of relying solely on bi-encoder distance metrics, the cross-encoder deeply scores query-chunk relevance, significantly boosting retrieval precision before handing data off to Ollama."*

---

## 🟢 Day 7: Production REST API (FastAPI), Streamlit UI, & Dynamic Ingestion Architecture

### 📊 Architectural Review & Design Decisions
* **FastAPI Service Layer (`app.py`):** Wrapped the Day 6 hybrid search and cross-encoder reranking engine into an asynchronous REST API (`/query`). Initialized and cached models and BM25 index globally at startup to eliminate latency.
* **Interactive Chat Interface (`app_ui.py`):** Built a responsive frontend using Streamlit to provide a visual chat experience with live assistant responses and page-level source citations.
* **Dynamic Ingestion Architecture:** Mapped out the multi-document ingestion strategy, establishing the blueprint for runtime ingestion via a FastAPI `/upload` endpoint and Streamlit file uploader widget.

### 🎙️ Interview Soundbites & Engineering Defense
* **On Moving from Scripts to Services:** *"On Day 7, I transitioned the RAG pipeline from an offline CLI script into a production-grade FastAPI backend service, enabling asynchronous handling, structured Pydantic data validation, and automated Swagger documentation."*
* **On Full-Stack AI Engineering & System Design:** *"To bridge the backend to users, I built a companion Streamlit chat interface that preserves session state and renders verifiable page citations, while also designing the runtime dynamic ingestion architecture for multi-document scalability."*

---

## 🔵 Day 8: Scientific Rigor & Automated Evaluation (Ragas)

### 📊 Architectural Review & Design Decisions
* **Metrics-Driven Pipeline Validation:** Replaced subjective "vibe-based" testing with automated, data-driven pipeline benchmarking using **Ragas (Retrieval Augmented Generation Assessment)**.
* **Air-Gapped Evaluation Judges:** Configured Ragas to run entirely offline by wrapping local Ollama models (`llama3.2`) and HuggingFace embeddings as the evaluation judge engine, ensuring zero cloud API dependencies.
* **Core Metrics Tracked:** Measured **Faithfulness** (hallucination detection), **Answer Relevancy** (prompt adherence), and **Context Recall** (retrieval quality) to scientifically validate that Hybrid Search + Cross-Encoder reranking delivers optimal context to the LLM.
* **Automated Reporting:** Exported structured evaluation logs directly to `evaluation_report.csv` for continuous integration tracking and portfolio documentation.

### 🎙️ Interview Soundbites & Engineering Defense
* **On Moving Beyond Vibe Checks:** *"To treat AI engineering with the same rigor as traditional software engineering, I implemented automated evaluation using Ragas. Instead of subjectively testing a few prompts, I built an evaluation harness that scores faithfulness, answer relevancy, and context recall against a golden dataset."*
* **On Local Benchmarking:** *"Maintaining strict data privacy requirements, I configured Ragas to execute its evaluation judge locally via Ollama, proving that advanced pipeline benchmarking can be achieved completely air-gapped without relying on external cloud APIs like OpenAI."*

---

## 🟢 Day 9: Dynamic File Ingestion Execution

### 📊 Architectural Review & Design Decisions
* **Runtime PDF Ingestion API (/upload):** Extended the FastAPI backend to accept runtime multi-document uploads, handling batch embedding generation (sentence-transformers) and bulk database insertions (psycopg2.extras) on the fly without requiring server restarts.
* **File Inventory & Corpus Synchronization:** Implemented active file tracking endpoints (/files) that expose ingested document states, allowing real-time BM25 index corpus hot-reloading when new files are added.
* **Interactive Frontend Sidebar Integration:** Enhanced the Streamlit UI with a dedicated document management sidebar displaying active files, file sizes, and drag-and-drop runtime upload capabilities.
### 🎙️ Interview Soundbites & Engineering Defense
* **On Moving from Static to Dynamic Pipelines**: *"Static RAG applications break down when users need to inject new documents on the fly. On Day 9, I engineered a dynamic runtime ingestion pipeline featuring bulk batch database insertion and automated BM25 corpus re-indexing, allowing users to upload PDFs directly through the UI without restarting the backend."*

---

## 📅 Day 10: Containerization & Multi-Service Orchestration
* **Objective:** Package the entire AI engineering sprint into a production-ready, multi-service Docker Compose ecosystem.
* **Architecture Decisions:** 
  * Configured `docker-compose.yml` to orchestrate PostgreSQL (`pgvector`), FastAPI Backend, and Streamlit Frontend concurrently.
  * Implemented environment-agnostic configuration (`os.getenv`) with sensible local fallbacks to ensure seamless execution between local workstations and container bridges.
* **Key Takeaway:** Containerizing multi-service AI applications eliminates "works on my machine" syndrome and provides instant environment parity for deployments.
* **Interview Soundbite:** *"I containerized a hybrid RAG pipeline using Docker Compose, orchestrating PostgreSQL with pgvector, a FastAPI microservice, and a Streamlit UI with unified networking and persistent data volumes."*

---

## 📅 Day 11: Production-Grade Automated Testing (`pytest`)
* **Objective:** Implement a robust automated testing and code coverage suite for backend FastAPI endpoints and retrieval pipelines.
* **Implementation Details:**
  * Installed `pytest`, `pytest-cov`, and configured FastAPI's `TestClient` for asynchronous REST API verification.
  * Applied `unittest.mock` (`MagicMock`, `@patch`) to isolate database connections (`psycopg2`), dense embedding models, BM25 keyword indices, cross-encoders, and LangChain LLM invocations.
  * Successfully resolved mock return type mappings (e.g., NumPy `.argsort()` support, Pydantic `QueryResponse` string constraints) to achieve 100% passing test suites and healthy coverage reports (`pytest test_app.py -v --cov=app`).
* **Key Takeaway:** Rigorous test-driven development in AI engineering requires thoughtful mocking of heavy ML models and databases, allowing tests to run in seconds without external network or GPU flakiness.
* **Interview Soundbite:** *"I implemented a production-grade automated testing suite using pytest and FastAPI's TestClient, utilizing targeted mocking for vector databases, embedding models, and local LLMs to guarantee reliable, high-speed test execution."*