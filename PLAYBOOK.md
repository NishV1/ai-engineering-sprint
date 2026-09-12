# 🛠️ AI Engineering Workflow & Best Practices Playbook

This document outlines the standard operating procedures, infrastructure habits, defensive programming standards, and engineering patterns established during the AI Engineering Sprint. Use this as a blueprint for all future production projects.

---

## 1. Environment Hygiene, Startup & Shutdown Routine
Managing your development environment lifecycle prevents port conflicts, memory leaks, container crashes, and environment drift. Always follow these strict checklists at the beginning and end of every coding session:

### 🚀 Daily Startup Sequence
1. **Start Infrastructure Containers:** Spin up your multi-service stack via Docker Compose (`docker compose up --build -d`). Verify via `docker ps` to ensure ports (`5432`, `8000`, `8501`) are active.
2. **Launch & Verify Local RAG Services:** Ensure local or containerized background services (such as Ollama on port `11434`) are active. If host port collisions occur (e.g., native Windows Ollama locking `11434`), route internal container communication directly over the Docker bridge network (`http://ollama:11434`).
3. **Model Warmup & Verification:** Verify target models (`llama3.2`) are present in persistent volume storage (`ollama_storage`) or pull them inside the container (`docker exec -it rag_ollama ollama pull llama3.2`).
4. **Activate Python Virtual Environment:** Run `.\venv\Scripts\Activate` (or equivalent shell path) to load local dependencies if running in hybrid development mode.
5. **Execute Pipeline & Check Health:** Test API endpoints or verify backend health status via `/health` or Streamlit readiness status loader (`st.status`).

### 🛑 Mandatory Day-End Shutdown & Documentation Checklist
1. **Update Living Documentation (Mandatory Pre-Logout Step):** 
   * Review and append architectural notes, design decisions, and interview soundbites to `SESSION_JOURNEY.md`.
   * Add any new technical terms or libraries to `GLOSSARY.md`.
   * Ensure `README.md` reflects current sprint progress, benchmark metrics, and file structures.
2. **Version Control & Commit:** Stage all changes (`git add .`), write a descriptive conventional commit (`git commit -m "feat: [description] + update docs"`), and push to GitHub (`git push`).
3. **Stop Infrastructure Containers:** Run `docker compose down` to gracefully stop databases and microservices while preserving vector and LLM data via persistent Docker volumes (`pgdata`, `ollama_storage`).
4. **Optimize OS Resources (WSL 2):** Run `wsl --shutdown` on Windows to clear background Linux utility VMs and free up host RAM.
5. **Deactivate Runtimes:** Run `deactivate` to clean up active Python virtual environments in the terminal.

---

## 2. Tooling & Dependency Guardrails
When introducing new libraries, embedding models, vector stores, or external utilities into a sprint project:
* **Pre-Installation Auditing:** Always verify local requirements and check for existing installations or port allocations before adding new tools. Avoid duplicate dependencies (e.g., standardizing on `psycopg2-binary` and `sentence-transformers` for local builds).
* **Explicit Documentation:** Document any new CLI utilities, Python dependencies in `requirements.txt`, or Docker container definitions (`docker-compose.yml`, `Dockerfile.backend`, `Dockerfile.frontend`) in setup documentation immediately.
* **Volume Persistence Guardrails:** Always mount persistent Docker volumes for databases (`pgdata`) and LLM model weights (`ollama_storage`) to prevent long model re-download times across container rebuilds.

---

## 3. Version Control & Commit Standards
Writing clear, descriptive commit messages keeps your repository professional and makes tracking feature increments easy for recruiters and collaborators.
* **Frequent Commits:** Commit logical, self-contained units of work (e.g., separating infrastructure setup from hybrid RRF retrieval, Streamlit UI integration, or container orchestration).
* **Conventional Commits Format:** Use structured prefixes (`feat:`, `fix:`, `refactor:`, `docs:`, `test:`) followed by clear, concise descriptions.
  * *Example:* `git commit -m "feat: containerize multi-service stack with Docker Compose and env-agnostic config"`

---

## 4. Legacy Code & Schema Management (Defensive Engineering)
As projects evolve from simple proof-of-concepts to complex multi-table production pipelines and containerized microservices:
* **Idempotency & Self-Healing Schemas:** Write database setup routines that are completely self-healing (using `CREATE EXTENSION IF NOT EXISTS vector;` and `CREATE TABLE IF NOT EXISTS document_chunks...`) at startup and prior to query execution so scripts re-initialize themselves cleanly.
* **Resilient API Contracts:** Design endpoints to return graceful empty responses (e.g., returning `{"files": []}` from `/files`) rather than throwing HTTP 500 errors when queried against unpopulated databases.
* **Environment-Agnostic Configuration:** Never hardcode connection strings, database hosts, or API URLs. Always utilize environment variables (`os.getenv`) with sensible local fallbacks (`localhost`, `http://host.docker.internal:11434`) to guarantee seamless execution across local workstations and Docker bridge networks.
* **Context Isolation (Document Scoping):** Prevent cross-document context bleeding by implementing document-scoped metadata filters across both vector (`WHERE source_file = %s`) and BM25 keyword search paths.
* **Backend Health Polling:** Replace fixed delay sleeps (`time.sleep()`) with active polling against backend readiness endpoints (`/health`) using visual status components (`st.status`) in frontend UIs.

---

## 5. Multi-Day Session & Progress Tracking
When executing sprint-based or complex engineering tasks across multiple days in a single sitting:
* **Quantitative Retrieval Evaluation:** Benchmark retrieval performance using **Hit-Rate@K** and **Mean Reciprocal Rank (MRR)** (`evaluate_retrieval.py`).
* **Automated Unit & API Testing (`pytest`):** Isolate API endpoint logic from heavy ML execution using `unittest.mock` (`MagicMock`, `@patch`) to mock database queries, dense embedding models, BM25 indices, and LLM synthesis.
* **Explicit Documentation:** Document every individual day's accomplishments clearly in session summaries and track metrics progression.

---

## 6. Portfolio & GitHub Optimization
Your GitHub profile is your living resume. Make sure your repositories communicate value instantly:
* **Descriptive Metadata:** Keep GitHub repository descriptions punchy, highlighting the core tech stack (Python 3.11, PostgreSQL 17 / `pgvector`, FastAPI, Streamlit, Docker Compose, Ollama) and architectural patterns (Hybrid RAG, RRF, Cross-Encoder Reranking).
* **Comprehensive Documentation:** Maintain a thorough `README.md` that outlines the roadmap, ASCII architecture diagrams, quickstart instructions, and verifiable benchmarks (**Hit-Rate@5: 100.00%**, **MRR: 1.0000**).

---

## 7. Living Documentation & Glossary Maintenance
As new tools, libraries, or conceptual patterns are introduced during a sprint:
* **Immediate Updates:** Whenever a new technical term, architecture pattern, or core concept is learned (e.g., Cosine Distance, Reciprocal Rank Fusion, Cross-Encoder), append or edit it in `GLOSSARY.md` with beginner-friendly definitions and analogies.
* **Session Retrospectives:** Continuously update `SESSION_JOURNEY.md` to capture architectural reviews, design decisions, and interview-ready soundbites.