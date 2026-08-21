# 🛠️ AI Engineering Workflow & Best Practices Playbook

This document outlines the standard operating procedures, infrastructure habits, and engineering patterns established during the AI Engineering Sprint. Use this as a blueprint for all future production projects.

---

## 1. Environment Hygiene & Shutdown Routine
Leaving development containers or background virtual machines running can consume system RAM, lock up ports, or cause environment drift. Always follow a strict shutdown checklist before ending a coding session:
* **Stop Infrastructure Containers:** Run `docker compose down` to gracefully stop databases and services while preserving data via persistent Docker volumes.
* **Optimize OS Resources (WSL 2):** Run `wsl --shutdown` on Windows to clear background Linux utility VMs and free up host RAM.
* **Deactivate Runtimes:** Run `deactivate` to clean up active Python virtual environments in the terminal.

---

## 2. Version Control & Commit Standards
Writing clear, descriptive commit messages keeps your repository professional and makes tracking feature increments easy for recruiters and collaborators.
* **Frequent Commits:** Commit logical chunks of work (e.g., separating infrastructure setup from ingestion logic).
* **Conventional Commits Format:** Use prefixes like `feat:`, `fix:`, or `refactor:` followed by a clear, concise description.
  * *Example:* `git commit -m "feat: complete Day 3 PDF ingestion and metadata tracking pipeline"`

---

## 3. Legacy Code & Schema Management (Defensive Engineering)
As projects evolve from simple proof-of-concepts (Day 1) to complex multi-table production pipelines (Day 3+), database schemas and dependencies change.
* **Idempotency:** Write scripts that are self-healing where possible (e.g., using `CREATE EXTENSION IF NOT EXISTS` and `DROP TABLE IF EXISTS` where appropriate) so scripts can re-initialize themselves cleanly.
* **Dependency Auditing:** Regularly review older test scripts when underlying infrastructure, libraries, or database schemas change to prevent silent technical debt.

---

## 4. Multi-Day Session & Progress Tracking
When executing sprint-based or complex engineering tasks across multiple days in a single sitting:
* **Explicit Documentation:** Document every individual day's accomplishments clearly in session summaries.
* **Continuous Integration of Habits:** Layer process improvements (like adding automated Git tracking or shutdown checks) progressively into your standard workflow.

---

## 5. Portfolio & GitHub Optimization
Your GitHub profile is your living resume. Make sure your repositories communicate value instantly:
* **Descriptive Metadata:** Keep GitHub repository descriptions punchy, highlighting the core tech stack (Python, PostgreSQL/pgvector, LangChain) and architectural patterns (RAG, hybrid search, agentic workflows).
* **Comprehensive Documentation:** Maintain a thorough `README.md` that outlines the roadmap, architecture diagrams, and setup instructions.

---

## 6. Living Documentation & Glossary Maintenance
As new tools, libraries, or conceptual patterns are introduced during a sprint:
* **Immediate Updates:** Whenever a new technical term, architecture pattern, or core concept is learned, append or edit it in `GLOSSARY.md` with beginner-friendly definitions and analogies.
* **Session Retrospectives:** Continuously update `SESSION_JOURNEY.md` to capture architectural reviews, design decisions, and interview-ready soundbites.
* **Pre-Logout Check:** Treat documentation updates as an mandatory step of the completion cycle before running final Git commits and shutting down.