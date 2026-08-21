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