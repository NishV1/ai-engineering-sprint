import os
import shutil
from typing import Optional
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
import psycopg2
import psycopg2.extras
from sentence_transformers import SentenceTransformer, CrossEncoder
from rank_bm25 import BM25Okapi
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

app = FastAPI(
    title="Air-Gapped Hybrid RAG API",
    description="Production-grade local RAG pipeline with Hybrid Search (Vector + BM25), Cross-Encoder Reranking, Llama 3.2, and Dynamic Ingestion.",
    version="1.2.0"
)

# Configuration Constants with Environment Variable Fallbacks
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "vector_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
RERANKER_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"
OLLAMA_MODEL = "llama3.2"
UPLOAD_DIR = "./uploaded_docs"

os.makedirs(UPLOAD_DIR, exist_ok=True)

print("🚀 Initializing FastAPI Hybrid RAG Backend...")
embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
reranker = CrossEncoder(RERANKER_MODEL_NAME)
llm = ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL, temperature=0.0)

# Global indexing structures
doc_ids = []
doc_texts = []
doc_metadata = []
chunk_lookup = {}
bm25 = None

def load_corpus_from_db():
    """Ensures database schema exists, then loads existing chunks into memory for BM25 search."""
    global doc_ids, doc_texts, doc_metadata, chunk_lookup, bm25
    try:
        conn = psycopg2.connect(
            host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
        )
        cursor = conn.cursor()
        
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS document_chunks (
                id SERIAL PRIMARY KEY,
                chunk_text TEXT NOT NULL,
                embedding vector(384),
                source_file TEXT,
                page_number INT
            );
        """)
        conn.commit()

        cursor.execute("SELECT id, chunk_text, source_file, page_number FROM document_chunks;")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        doc_ids = [row[0] for row in rows]
        doc_texts = [row[1] for row in rows]
        doc_metadata = [{"source": row[2], "page": row[3]} for row in rows]
        chunk_lookup = {row[0]: {"text": row[1], "source": row[2], "page": row[3]} for row in rows}

        if doc_texts:
            tokenized_corpus = [text.lower().split() for text in doc_texts]
            bm25 = BM25Okapi(tokenized_corpus)
            print(f"✅ Hot-loaded {len(doc_texts)} chunks into BM25 index.")
        else:
            bm25 = None
            print("⚠️ Database is empty. Table provisioned.")
    except Exception as e:
        print(f"❌ Error initializing DB: {e}")
        bm25 = None

print("🔌 Connecting to database and verifying schema...")
load_corpus_from_db()

class QueryRequest(BaseModel):
    query: str
    selected_file: Optional[str] = None  # Optional document filter

class QueryResponse(BaseModel):
    query: str
    answer: str
    sources: list[str]

@app.get("/health")
def health_check():
    """Checks if heavy AI models and database connections are ready."""
    is_ready = embedding_model is not None and reranker is not None
    return {
        "status": "ready" if is_ready else "loading",
        "bm25_loaded": bm25 is not None,
        "active_chunks": len(doc_ids)
    }

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Dynamically ingests a new PDF, batch-embeds chunks, bulk-inserts into PostgreSQL, and hot-loads search indices."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        loader = PyPDFLoader(file_path)
        pages = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = text_splitter.split_documents(pages)
        
        if not chunks:
            raise HTTPException(status_code=400, detail="No extractable text found in PDF.")

        texts = [chunk.page_content for chunk in chunks]
        page_nums = [chunk.metadata.get("page", 0) + 1 for chunk in chunks]
        source_files = [file.filename] * len(chunks)

        embeddings = embedding_model.encode(texts, batch_size=32).tolist()
        records = list(zip(texts, embeddings, source_files, page_nums))

        conn = psycopg2.connect(
            host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
        )
        cursor = conn.cursor()
        insert_sql = """
            INSERT INTO document_chunks (chunk_text, embedding, source_file, page_number)
            VALUES %s;
        """
        psycopg2.extras.execute_values(cursor, insert_sql, records, template="(%s, %s::vector, %s, %s)")
        conn.commit()
        cursor.close()
        conn.close()

        load_corpus_from_db()

        return {
            "status": "success",
            "filename": file.filename,
            "chunks_ingested": len(chunks),
            "message": f"Successfully ingested {file.filename}."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files")
def list_ingested_files():
    """Safely retrieves all unique ingested source files without failing if empty."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
        )
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS document_chunks (
                id SERIAL PRIMARY KEY, chunk_text TEXT NOT NULL, embedding vector(384), source_file TEXT, page_number INT
            );
        """)
        conn.commit()
        cursor.execute("SELECT DISTINCT source_file FROM document_chunks WHERE source_file IS NOT NULL ORDER BY source_file;")
        files = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return {"files": files}
    except Exception:
        return {"files": []}

@app.post("/query", response_model=QueryResponse)
def execute_hybrid_query(request: QueryRequest):
    query = request.query.strip()
    selected_file = request.selected_file

    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    if embedding_model is None or bm25 is None or not doc_ids:
        raise HTTPException(status_code=400, detail="No documents ingested yet. Please upload a PDF first.")

    try:
        conn = psycopg2.connect(
            host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
        )
        cursor = conn.cursor()

        # 1. Vector Search (Scoped if selected_file is provided)
        query_vector = embedding_model.encode(query).tolist()
        if selected_file:
            vector_sql = """
                SELECT id, chunk_text, source_file, page_number, 1 - (embedding <=> %s::vector) AS similarity
                FROM document_chunks
                WHERE source_file = %s
                ORDER BY embedding <=> %s::vector
                LIMIT 10;
            """
            cursor.execute(vector_sql, (query_vector, selected_file, query_vector))
        else:
            vector_sql = """
                SELECT id, chunk_text, source_file, page_number, 1 - (embedding <=> %s::vector) AS similarity
                FROM document_chunks
                ORDER BY embedding <=> %s::vector
                LIMIT 10;
            """
            cursor.execute(vector_sql, (query_vector, query_vector))
        
        vector_results = cursor.fetchall()

        # 2. BM25 Keyword Search (Filtered by document if scoped)
        tokenized_query = query.lower().split()
        bm25_scores = bm25.get_scores(tokenized_query)
        top_bm25_indices = bm25_scores.argsort()[::-1]

        filtered_bm25_indices = []
        for idx in top_bm25_indices:
            if idx < len(doc_ids):
                d_id = doc_ids[idx]
                if selected_file:
                    if chunk_lookup.get(d_id, {}).get("source") == selected_file:
                        filtered_bm25_indices.append(idx)
                else:
                    filtered_bm25_indices.append(idx)
            if len(filtered_bm25_indices) >= 10:
                break

        # 3. Reciprocal Rank Fusion (RRF)
        rrf_scores = {}
        k = 60
        for rank, row in enumerate(vector_results):
            doc_id = row[0]
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + 1.0 / (k + (rank + 1))

        for rank, idx in enumerate(filtered_bm25_indices):
            doc_id = doc_ids[idx]
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + 1.0 / (k + (rank + 1))

        sorted_rrf = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:10]
        combined_pool_ids = [item[0] for item in sorted_rrf]

        # 4. Cross-Encoder Reranking
        rerank_pairs = []
        pool_ids_ordered = []
        for doc_id in combined_pool_ids:
            if doc_id in chunk_lookup:
                text = chunk_lookup[doc_id]["text"]
                meta = {"source": chunk_lookup[doc_id]["source"], "page": chunk_lookup[doc_id]["page"]}
                rerank_pairs.append([query, text])
                pool_ids_ordered.append((doc_id, text, meta))

        top_chunks = []
        if rerank_pairs:
            rerank_scores = reranker.predict(rerank_pairs)
            scored_pool = list(zip(pool_ids_ordered, rerank_scores))
            scored_pool.sort(key=lambda x: x[1], reverse=True)
            top_chunks = scored_pool[:3]

        cursor.close()
        conn.close()

        # 5. LLM Synthesis with Explicit Document Boundaries
        context_blocks = []
        sources_used = set()
        for item, score in top_chunks:
            doc_id, text, meta = item
            filename = meta.get("source", "unknown")
            page = meta.get("page", "unknown")
            context_blocks.append(f"--- DOCUMENT: {filename} (Page {page}) ---\n{text}")
            sources_used.add(f"{filename} (Page {page})")

        context_str = "\n\n".join(context_blocks)
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", "You are an expert technical assistant. Answer the user's question accurately using ONLY the provided context. Include source file names and page citations for every claim. Clearly distinguish between different documents if multiple are referenced."),
            ("human", "Context:\n{context}\n\nQuestion: {question}")
        ])

        chain = prompt_template | llm
        response = chain.invoke({"context": context_str, "question": query})

        return QueryResponse(
            query=query,
            answer=response.content,
            sources=sorted(list(sources_used))
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))