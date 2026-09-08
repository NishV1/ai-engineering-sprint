# 🏛️ System Architecture: Air-Gapped Hybrid RAG Pipeline

This document outlines the architectural design, component choices, and data flow of the Production-Grade RAG system.

---

## 📐 System Data Flow

Raw PDF Documents 
       │
       ▼ (Day 2-3)
LangChain RecursiveCharacterTextSplitter 
       │
       ├───────────────────────────────┐
       ▼                               ▼
Dense Embeddings                Sparse Lexical Index
(SentenceTransformers)          (BM25Okapi Token Index)
       │                               │
       ▼                               ▼
PostgreSQL + pgvector           In-Memory BM25 Pool
       └───────────────┬───────────────┘
                       │
                       ▼ (Day 6)
      Reciprocal Rank Fusion (RRF)
                       │
                       ▼ (Top Candidates)
      Cross-Encoder Reranker 
      (ms-marco-MiniLM-L-6-v2)
                       │
                       ▼ (Top Precision Chunks)
      Ollama LLM (Llama 3.2) ──► Grounded Response + Page Citations

---

## 🔍 Core Architectural Decisions & Trade-Offs

### 1. Hybrid Search (Dense + Sparse with RRF)
* **The Problem:** Pure vector search excels at semantic matching but often fails to retrieve exact keywords, version numbers, or part codes.
* **The Solution:** Combining dense vector embeddings (cosine distance via `pgvector`) with lexical keyword search (`BM25`) using **Reciprocal Rank Fusion (RRF)**.
* **Trade-off:** Slight compute overhead during retrieval, offset by massive recall gains for technical texts.

### 2. Two-Stage Retrieval with Cross-Encoder Reranking
* **The Problem:** Bi-encoders score queries and documents independently, missing subtle semantic interactions.
* **The Solution:** Casting a wide net with Hybrid Search (top 10 candidates), then using a computationally intensive **Cross-Encoder** to jointly score query-document pairs. Only the top 3 chunks go to the LLM.
* **Trade-off:** Adds milliseconds of inference latency to guarantee context noise is minimized.

### 3. Air-Gapped & Local-First Infrastructure
* **The Problem:** Enterprise clients face strict data compliance and privacy regulations prohibiting cloud LLM APIs.
* **The Solution:** 100% local orchestration using Dockerized PostgreSQL, Hugging Face models, and Ollama. Zero external data egress.

---

## 🛠️ Technology Stack
* **Orchestration & Framework:** Python, FastAPI, Streamlit, LangChain
* **Vector Storage:** PostgreSQL 16 + `pgvector` extension (Dockerized)
* **Embeddings & Reranking:** `sentence-transformers`, `rank_bm25`
* **Local LLM Engine:** Ollama (`llama3.2`)