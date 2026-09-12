# 📖 AI Engineering Glossary (Beginner-Friendly Dictionary)

A living reference guide for all tools, languages, libraries, and technical concepts used throughout the AI Engineering Sprint. Designed for clear, foundational understanding.

---

## 1. Core Concepts & Data Types
* **Unstructured Data:** Information that does not fit neatly into traditional relational database tables. Examples include free-flowing text paragraphs, PDF manuals, audio recordings, images, and videos. Processing unstructured text requires specialized AI parsing and vectorization pipelines.
* **Vector / Embedding:** A list of numbers (coordinates) that represents the semantic "meaning" of a piece of data (a word, sentence, or document chunk) in a multi-dimensional mathematical space. Words with similar meanings are positioned close together in vector space.
* **Vector Space / High-Dimensional Space:** The mathematical space where vectors reside. While a physical map has 2 dimensions ($X$ and $Y$), embedding models use hundreds of dimensions (e.g., 384 dimensions for `all-MiniLM-L6-v2`) to capture fine-grained linguistic nuances.
* **Cosine Distance (`<=>`):** A mathematical formula used to measure the angle between two vectors in multi-dimensional space. A score of `0.0` indicates identical semantic meaning, while values approaching `2.0` indicate completely unrelated text.

---

## 2. Artificial Intelligence & Machine Learning Fundamentals
* **Transformer Model:** An AI model architecture introduced in 2017 that processes sequential text using self-attention mechanisms to evaluate relationships between words in context (e.g., distinguishing a financial bank from a river bank based on surrounding words).
* **Embedding Model:** A specialized neural network designed to take text inputs and convert them into dense numerical vectors that represent their underlying semantic concepts.
* **Sentence-Transformers:** A Python framework built on top of PyTorch that enables developers to run pre-trained sentence and text embedding models locally.
* **`all-MiniLM-L6-v2`:** A lightweight sentence-transformer model that maps text into a 384-dimensional vector space, balancing fast CPU inference with high semantic accuracy.

---

## 3. Infrastructure & Databases
* **Docker / Docker Compose:** Containerization tools used to package applications, databases, and dependencies into isolated environments. Compose allows multi-container applications (FastAPI, PostgreSQL, Streamlit, Ollama) to be defined and launched using a single configuration file.
* **PostgreSQL (Postgres):** An open-source relational database management system used to store structured application data transactionally.
* **`pgvector`:** An open-source extension for PostgreSQL that adds native high-dimensional vector storage and fast vector distance search operators (`<=>`).

---

## 4. Data Ingestion & Processing
* **LangChain / LangChain Community:** An open-source framework and collection of utility packages designed to streamline building applications with Large Language Models, document loaders, and vector stores.
* **`PyPDFLoader`:** A document parsing utility that reads multi-page PDF files, extracts raw text content, and preserves page-level metadata lineage (`source_file`, `page_number`).
* **Recursive Character Text Splitter:** A semantic text chunking algorithm that recursively evaluates a hierarchical list of separators (`\n\n`, `\n`, ` `, ``) to split long documents while keeping paragraphs and sentences intact.
* **Chunking & Chunk Overlap:**
  * *Chunking:* Segmenting large documents into smaller, uniform blocks suitable for context window constraints.
  * *Chunk Overlap:* Duplicating trailing tokens from Chunk $N$ into the start of Chunk $N+1$ to preserve semantic continuity across chunk boundaries.

---

## 5. Software Engineering & Architecture Patterns
* **Metadata Lineage:** Attaching structural data (`source_file`, `page_number`, `chunk_id`) directly to vectorized chunks in the database to enable verifiable source citations and auditability.
* **Idempotency & Self-Healing Schemas:** Programming database initialization scripts to execute safely multiple times (`CREATE EXTENSION IF NOT EXISTS`, `CREATE TABLE IF NOT EXISTS`) without causing schema corruption or environment failure.
* **Retrieval-Augmented Generation (RAG):** An architectural pattern where an LLM is provided with relevant context retrieved from an external database before generating an answer, eliminating hallucinations and grounding responses in facts.
* **Document Scoping / Context Isolation:** Restricting search queries to specific document filenames (`WHERE source_file = %s`) across both vector and sparse retrieval indexes to prevent context bleeding between unrelated files.

---

## 6. Advanced Retrieval & Search Concepts
* **Hybrid Search:** A retrieval strategy combining dense vector search (semantic proximity) with sparse lexical search (BM25 keyword matching) to achieve high recall across both conceptual queries and exact serial numbers.
* **Reciprocal Rank Fusion (RRF):** A scale-agnostic ranking algorithm that combines ranked candidate lists from different search algorithms (Vector and BM25) into a unified order based on candidate rank positions: $S_{\text{RRF}}(d) = \sum \frac{1}{k + r(d)}$.
* **Cross-Encoder Reranker:** A transformer model (`ms-marco-MiniLM-L-6-v2`) that evaluates query-document text pairs simultaneously through full attention layers to re-score and rank top candidates before sending them to the LLM.

---

## 7. Generative RAG & LLM Concepts
* **Ollama:** A local LLM runtime engine that manages model weights (`llama3.2`) and exposes an air-gapped OpenAI-compatible API endpoint (`:11434`).
* **Context Grounding / Prompt Constraints:** System prompt instructions that explicitly restrict an LLM to synthesizing answers using *only* retrieved context chunks, instructing the model to declare ignorance if context is insufficient.
* **Source Attribution:** The capability of an AI application to cite exact source files and page numbers alongside generated text.

---

## 8. Production APIs, UI & Resilience
* **FastAPI:** An asynchronous, high-performance Python web framework used to build RESTful microservice backend endpoints with automatic OpenAPI (`/docs`) generation.
* **Streamlit:** A Python web application framework used to construct interactive chat user interfaces and dynamic sidebars.
* **Asynchronous Execution (`async`/`await`):** Non-blocking concurrency handling that enables API services to process incoming network I/O and database operations efficiently.
* **Backend Health Polling (`/health`):** A UX resilience pattern where frontend applications periodically query a readiness endpoint (`/health`) using status indicators (`st.status`) until heavy ML models finish warm-up initialization.

---

## 9. Containerization & Network Architecture
* **Container Isolation:** Environment encapsulation guaranteeing that application code runs identically regardless of underlying host OS differences.
* **Environment-Agnostic Configuration:** Reading system endpoints and database credentials dynamically from environment variables (`os.getenv`) with local fallback defaults.
* **Docker Bridge Network:** A virtual internal network allowing isolated Docker containers to communicate securely using container service names (e.g., `http://ollama:11434`) as hostnames.

---

## 10. Quantitative Retrieval Benchmarking & Evaluation
* **Hit-Rate@K:** The percentage of evaluation queries for which the correct ground-truth document chunk appears anywhere within the top $K$ retrieved candidates.
* **Mean Reciprocal Rank (MRR):** A statistical evaluation metric measuring where the first relevant chunk appears in the ranked results, calculated as the average of reciprocal ranks ($\frac{1}{\text{rank}}$) across test queries.
* **Ragas Framework:** An automated evaluation library that measures RAG pipeline performance metrics, including **Faithfulness** (hallucination detection) and **Context Recall** (retrieval completeness).

---

## 11. Automated Testing & Reliability
* **FastAPI `TestClient`:** A synchronous test runner utility built on Starlette/HTTPX for testing REST API endpoints without launching external web servers.
* **Mocking (`unittest.mock` / `@patch`):** A software testing technique that substitutes heavy dependencies (vector databases, embedding models, local LLMs) with controlled mock objects to enable fast, deterministic test runs.
* **`pytest-cov`:** A testing plugin that calculates statement coverage across Python application modules during test suite execution.