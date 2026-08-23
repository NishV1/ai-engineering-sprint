# 📖 AI Engineering Glossary (Beginner-Friendly Dictionary)

A living reference guide for all tools, languages, libraries, and technical concepts used throughout the AI Engineering Sprint. Designed for clear, foundational understanding.

---

## 1. Core Concepts & Data Types
* **Unstructured Data:** Information that does not fit neatly into rows and columns (like a traditional Excel spreadsheet or SQL table). Examples include free-flowing text paragraphs, PDF manuals, audio recordings, images, and videos. Because computers cannot natively "read" unstructured text the way humans do, we need specialized AI pipelines to process it.
* **Vector / Embedding:** A list of numbers (coordinates) that represents the "meaning" of a piece of data (like a word, sentence, or entire document) in a multi-dimensional mathematical space. 
  * *Analogy:* Imagine a massive map where words with similar meanings are placed close to each other. "Puppy" and "dog" would live right next to each other, while "spaceship" would be far away. An embedding translates words into coordinates on this map.
* **Vector Space / High-Dimensional Space:** The mathematical "map" where vectors live. While a physical map has 2 dimensions (X and Y), AI maps often have hundreds or thousands of dimensions (e.g., 384 dimensions) to capture subtle nuances in human language.
* **Cosine Distance (`<=>`):** A mathematical formula used to measure how close two vectors are to each other on our conceptual map. 
  * *Scale:* A score of `0.0` means the two pieces of text mean the exact same thing. Higher numbers (up to `2.0`) mean they are completely unrelated.

---

## 2. Artificial Intelligence & Machine Learning Fundamentals
* **Transformer Model:** A revolutionary type of artificial intelligence architecture introduced in 2017 that powers modern AI (including ChatGPT and embedding generators). Instead of reading text word-by-word like a human, a transformer looks at an entire sentence at once, using "attention mechanisms" to figure out how words relate to one another contextually (e.g., understanding that the word "bank" means a river bank vs. a financial bank based on surrounding words).
* **Embedding Model:** A specific type of AI model whose only job is to take text input and convert it into a vector (a list of numbers) that captures its semantic meaning.
* **Sentence-Transformers:** A popular Python framework built on top of PyTorch that allows developers to run powerful embedding models directly on their local computers.
* **`all-MiniLM-L6-v2`:** A specific, lightweight, and fast embedding model. It takes text and maps it into a compact 384-dimensional vector space, striking an ideal balance between speed and accuracy for local development.

---

## 3. Infrastructure & Databases
* **Docker / Docker Compose:** A tool that lets you package software applications and databases into isolated containers. 
  * *Analogy:* Think of Docker like shipping containers. No matter what computer you put the container on (Windows, Mac, Linux), everything inside runs identically without messing up your computer's main system files.
* **PostgreSQL (Postgres):** An extremely popular, reliable, and powerful open-source relational database used to store data in tables (rows and columns).
* **`pgvector`:** A plugin (or extension) added to PostgreSQL that transforms a traditional relational database into a **Vector Database**. It teaches Postgres how to store vectors and run ultra-fast similarity searches across millions of rows.

---

## 4. Data Ingestion & Processing
* **LangChain / LangChain Community:** A massive collection of pre-built Python tools and frameworks designed to help developers build applications with Large Language Models (LLMs). It handles chores like loading files, splitting text, and connecting to databases.
* **`PyPDFLoader`:** A utility tool that opens binary PDF files, extracts the raw text letters, and keeps track of structural details like which page number each sentence came from.
* **Recursive Character Text Splitter:** A smart text-chopping algorithm. Because AI models have limits on how much text they can read at once, long documents must be cut into smaller pieces (chunks). This splitter tries its best not to cut sentences or paragraphs in half, preferring to split neatly at natural breaks like double line-breaks (`\n\n`) or periods.
* **Chunking & Chunk Overlap:** 
  * *Chunking:* Breaking a 100-page book down into hundreds of smaller, manageable paragraphs.
  * *Chunk Overlap:* Copying a few sentences from the end of Chunk A and pasting them at the start of Chunk B. This ensures that ideas spanning across a split boundary aren't accidentally cut in half and lost.

---

## 5. Software Engineering & Architecture Patterns
* **Metadata Tracking:** Storing extra "label" information alongside your main data. In our RAG pipeline, we store the `source_file` name and `page_number` alongside our text chunks so we can trace exactly where an answer came from.
* **Idempotency / Self-Healing Scripts:** Code design where running a script multiple times produces the same safe result without breaking things. For example, writing database code that checks `DROP TABLE IF EXISTS` so it can cleanly rebuild itself if something gets wiped out.
* **Retrieval-Augmented Generation (RAG):** An architectural pattern where an AI model doesn't just rely on what it memorized during training; instead, it searches your private database (like your PDF chunks) for relevant facts first, and then *augments* its answer using that retrieved data.

---

## 6. Search & Retrieval Metrics (Day 4 Additions)
* **Cosine Distance (`<=>`):** A mathematical metric measuring the cosine of the angle between two vectors. In pgvector, smaller distance values represent higher semantic alignment.
* **Unified Application Architecture:** Design pattern where initialization, data ingestion, and query interfaces are combined into a single continuous program to prevent state and database synchronization bugs.