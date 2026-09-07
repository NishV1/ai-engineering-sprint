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

