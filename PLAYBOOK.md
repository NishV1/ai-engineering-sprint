# 🛠️ AI Engineering Workflow & Best Practices Playbook

This document outlines the standard operating procedures, infrastructure habits, and engineering patterns established during the AI Engineering Sprint. Use this as a blueprint for all future production projects.

---

## 1. Environment Hygiene, Startup & Shutdown Routine
Managing your development environment lifecycle prevents port conflicts, memory leaks, and environment drift. Always follow these strict checklists at the beginning and end of every coding session:

### 🚀 Daily Startup Sequence
1. **Start Infrastructure Containers:** Run `docker compose up -d` to spin up databases and services (e.g., PostgreSQL with `pgvector`). Verify via `docker ps` to ensure port `5432` is active.
2. **Launch & Verify Local RAG Services:** Ensure local background services (such as Ollama on port `11434`) are active. If an address-in-use error occurs, it indicates the service is already running.
3. **Activate Python Virtual Environment:** Run `.\venv\Scripts\Activate` (or equivalent shell path) to load dependencies.
4. **Execute Pipeline:** Run your primary scripts (e.g., `python hybrid_rag.py`).

### 🛑 Mandatory Day-End Shutdown & Documentation Checklist
1. **Update Living Documentation (Mandatory Pre-Logout Step):** 
   * Review and append architectural notes, design decisions, and interview soundbites to `SESSION_JOURNEY.md`.
   * Add any new technical terms or libraries to `GLOSSARY.md`.
   * Ensure `README.md` reflects current sprint progress and file structures.
2. **Version Control & Commit:** Stage all changes (`git add .`), write a descriptive conventional commit (`git commit -m "feat: [description] + update docs"`), and push to GitHub (`git push`).
3. **Stop Infrastructure Containers:** Run `docker compose down` to gracefully stop databases and services while preserving data via persistent Docker volumes.
4. **Optimize OS Resources (WSL 2):** Run `wsl --shutdown` on Windows to clear background Linux utility VMs and free up host RAM.
5. **Deactivate Runtimes:** Run `deactivate` to clean up active Python virtual environments in the terminal.

---

## 2. Tooling & Dependency Guardrails
When introducing new libraries, frameworks, or external utilities into a sprint project:
* **Pre-Installation Auditing:** Always verify local requirements and check for existing installations or port allocations before adding new tools.
* **Explicit Documentation:** Document any new CLI utilities or Python bridge packages (`pip install`) in setup documentation immediately.

---

## 3. Version Control & Commit Standards
Writing clear, descriptive commit messages keeps your repository professional and makes tracking feature increments easy for recruiters and collaborators.
* **Frequent Commits:** Commit logical chunks of work (e.g., separating infrastructure setup from ingestion logic).
* **Conventional Commits Format:** Use prefixes like `feat:`, `fix:`, or `refactor:` followed by a clear, concise description.
  * *Example:* `git commit -m "feat: complete Day 6 hybrid search and reranking pipeline"`

---

## 4. Legacy Code & Schema Management (Defensive Engineering)
As projects evolve from simple proof-of-concepts (Day 1) to complex multi-table production pipelines (Day 3+), database schemas and dependencies change.
* **Idempotency:** Write scripts that are self-healing where possible (e.g., using `CREATE EXTENSION IF NOT EXISTS` and `DROP TABLE IF EXISTS` where appropriate) so scripts can re-initialize themselves cleanly.
* **Dependency Auditing:** Regularly review older test scripts when underlying infrastructure, libraries, or database schemas change to prevent silent technical debt.

---

## 5. Multi-Day Session & Progress Tracking
When executing sprint-based or complex engineering tasks across multiple days in a single sitting:
* **Explicit Documentation:** Document every individual day's accomplishments clearly in session summaries.
* **Continuous Integration of Habits:** Layer process improvements progressively into your standard workflow.

---

## 6. Portfolio & GitHub Optimization
Your GitHub profile is your living resume. Make sure your repositories communicate value instantly:
* **Descriptive Metadata:** Keep GitHub repository descriptions punchy, highlighting the core tech stack (Python, PostgreSQL/pgvector, LangChain) and architectural patterns (RAG, hybrid search, agentic workflows).
* **Comprehensive Documentation:** Maintain a thorough `README.md` that outlines the roadmap, architecture diagrams, and setup instructions.

---

## 7. Living Documentation & Glossary Maintenance
As new tools, libraries, or conceptual patterns are introduced during a sprint:
* **Immediate Updates:** Whenever a new technical term, architecture pattern, or core concept is learned, append or edit it in `GLOSSARY.md` with beginner-friendly definitions and analogies.
* **Session Retrospectives:** Continuously update `SESSION_JOURNEY.md` to capture architectural reviews, design decisions, and interview-ready soundbites.