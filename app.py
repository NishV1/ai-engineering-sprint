import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from sentence_transformers import SentenceTransformer, CrossEncoder
from rank_bm25 import BM25Okapi
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

app = FastAPI(
    title="Air-Gapped Hybrid RAG API",
    description="Production-grade local RAG pipeline with Hybrid Search (Vector + BM25), Cross-Encoder Reranking, and Llama 3.2.",
    version="1.0.0"
)

# Configuration Constants
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "vector_db"
DB_USER = "postgres"
DB_PASSWORD = "password"

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
RERANKER_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"
OLLAMA_MODEL = "llama3.2"

print("🚀 Initializing FastAPI Hybrid RAG Backend...")

print("📦 Loading embedding model & cross-encoder reranker...")
embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
reranker = CrossEncoder(RERANKER_MODEL_NAME)

print("🤖 Initializing local LLM (llama3.2 via Ollama)...")
llm = ChatOllama(model=OLLAMA_MODEL, temperature=0.0)

print("🔌 Connecting to database and indexing BM25 corpus...")
doc_ids = []
doc_texts = []
doc_metadata = []
chunk_lookup = {}
bm25 = None

try:
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
    )
    cursor = conn.cursor()
    cursor.execute("SELECT id, chunk_text, source_file, page_number FROM document_chunks;")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    doc_ids = [row[0] for row in rows]
    doc_texts = [row[1] for row in rows]
    doc_metadata = [{"source": row[2], "page": row[3]} for row in rows]
    
    chunk_lookup = {row[0]: {"text": row[1], "source": row[2], "page": row[3]} for row in rows}

    tokenized_corpus = [text.lower().split() for text in doc_texts]
    bm25 = BM25Okapi(tokenized_corpus)
    print(f"✅ Backend successfully initialized with {len(doc_texts)} chunks indexed!")

except Exception as e:
    print(f"❌ Startup database indexing failed: {e}")

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    query: str
    answer: str
    sources: list[str]

@app.post("/query", response_model=QueryResponse)
def execute_hybrid_query(request: QueryRequest):
    query = request.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    if embedding_model is None or bm25 is None:
        raise HTTPException(status_code=500, detail="Models or BM25 index are not initialized.")

    try:
        conn = psycopg2.connect(
            host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
        )
        cursor = conn.cursor()

        # 1. Vector Search
        query_vector = embedding_model.encode(query).tolist()
        vector_sql = """
            SELECT id, chunk_text, source_file, page_number, 1 - (embedding <=> %s::vector) AS similarity
            FROM document_chunks
            ORDER BY embedding <=> %s::vector
            LIMIT 10;
        """
        cursor.execute(vector_sql, (query_vector, query_vector))
        vector_results = cursor.fetchall()

        # 2. BM25 Keyword Search
        tokenized_query = query.lower().split()
        bm25_scores = bm25.get_scores(tokenized_query)
        top_bm25_indices = bm25_scores.argsort()[::-1][:10]

        # 3. Reciprocal Rank Fusion (RRF)
        rrf_scores = {}
        k = 60
        for rank, row in enumerate(vector_results):
            doc_id = row[0]
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + 1.0 / (k + (rank + 1))

        for rank, idx in enumerate(top_bm25_indices):
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

        # 5. LLM Synthesis
        context_blocks = []
        sources_used = set()
        for item, score in top_chunks:
            doc_id, text, meta = item
            filename = meta.get("source", "unknown")
            page = meta.get("page", "unknown")
            context_blocks.append(f"[Source: {filename}, Page {page}]\n{text}")
            sources_used.add(f"{filename} (Page {page})")

        context_str = "\n\n---\n\n".join(context_blocks)
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", "You are an expert technical assistant. Answer the user's question accurately using ONLY the provided context. Include source file names and page citations for every claim. If the answer is not in the context, state that you cannot find it."),
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