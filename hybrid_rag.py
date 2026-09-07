import os
import psycopg2
from sentence_transformers import SentenceTransformer, CrossEncoder
from rank_bm25 import BM25Okapi
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

# Configuration Constants
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "vector_db"
DB_USER = "postgres"
DB_PASSWORD = "password"

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
RERANKER_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"
OLLAMA_MODEL = "llama3.2"

def main():
    print("🚀 Initializing Advanced Hybrid RAG Engine (Day 6)...")

    # 1. Load Models
    print("📦 Loading embedding model & cross-encoder reranker...")
    embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    reranker = CrossEncoder(RERANKER_MODEL_NAME)

    # 2. Initialize LLM
    print("🤖 Initializing local LLM (llama3.2 via Ollama)...")
    llm = ChatOllama(model=OLLAMA_MODEL, temperature=0.0)

    # 3. Connect to Database
    print("🔌 Connecting to database 'vector_db'...")
    try:
        conn = psycopg2.connect(
            host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
        )
        print("✅ Connected successfully!")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return

    cursor = conn.cursor()

    # 4. # Fetch all documents from DB for BM25 Corpus index
    print("📚 Indexing corpus for BM25 keyword search...")
    cursor.execute("SELECT id, chunk_text, source_file, page_number FROM document_chunks;")
    rows = cursor.fetchall()
    
    doc_ids = [row[0] for row in rows]
    doc_texts = [row[1] for row in rows]
    doc_metadata = [{"source": row[2], "page": row[3]} for row in rows]
    
    # Tokenize corpus for BM25
    tokenized_corpus = [text.lower().split() for text in doc_texts]
    bm25 = BM25Okapi(tokenized_corpus)

    print(f"✅ Indexed {len(doc_texts)} chunks for hybrid search.")
    print("============================================================")
    print("✨ Hybrid RAG Terminal Ready (Type 'exit' to quit)")
    print("============================================================")

    while True:
        query = input("\nAsk a question about your docs (Hybrid): ")
        if query.lower() == 'exit':
            break
        if not query.strip():
            continue

        print("\n🔍 Executing Hybrid Retrieval (Vector + BM25)...")

        # --- A. Vector Similarity Search (Top 10) ---
        query_vector = embedding_model.encode(query).tolist()
        vector_sql = """
            SELECT id, chunk_text, source_file, page_number, 1 - (embedding <=> %s::vector) AS similarity
            FROM document_chunks
            ORDER BY embedding <=> %s::vector
            LIMIT 10;
        """
        cursor.execute(vector_sql, (query_vector, query_vector))
        vector_results = cursor.fetchall()
        
        # Map vector results by ID for easy lookup
        vector_candidates = {
            row[0]: {"text": row[1], "meta": {"source": row[2], "page": row[3]}, "vector_score": row[4]} 
            for row in vector_results
        }

        # --- B. BM25 Keyword Search (Top 10) ---
        tokenized_query = query.lower().split()
        bm25_scores = bm25.get_scores(tokenized_query)
        top_bm25_indices = bm25_scores.argsort()[::-1][:10]
        
        bm25_candidates = {}
        for idx in top_bm25_indices:
            doc_id = doc_ids[idx]
            bm25_candidates[doc_id] = {"text": doc_texts[idx], "meta": doc_metadata[idx], "bm25_score": float(bm25_scores[idx])}

        # --- C. Reciprocal Rank Fusion (RRF) ---
        # Combine candidate sets using rank positions
        rrf_scores = {}
        k = 60 # RRF smoothing constant
        
        # Rank vector results
        for rank, row in enumerate(vector_results):
            doc_id = row[0]
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + 1.0 / (k + (rank + 1))
            
        # Rank BM25 results
        for rank, idx in enumerate(top_bm25_indices):
            doc_id = doc_ids[idx]
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + 1.0 / (k + (rank + 1))

        # Sort combined candidates by RRF score and pick top 10 for reranking
        sorted_rrf = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Build candidate pool for reranking
        combined_pool_ids = [item[0] for item in sorted_rrf]
        id_to_data = {row[0]: (row[1], {"source": row[2], "page": row[3]}) for row in rows if row[0] in combined_pool_ids}

        # --- D. Cross-Encoder Reranking ---
        print("⚡ Reranking candidate chunks with Cross-Encoder...")
        rerank_pairs = []
        pool_ids_ordered = []
        for doc_id in combined_pool_ids:
            if doc_id in id_to_data:
                text, meta = id_to_data[doc_id]
                rerank_pairs.append([query, text])
                pool_ids_ordered.append((doc_id, text, meta))

        if rerank_pairs:
            rerank_scores = reranker.predict(rerank_pairs)
            # Attach scores and sort
            scored_pool = list(zip(pool_ids_ordered, rerank_scores))
            scored_pool.sort(key=lambda x: x[1], reverse=True)
            
            # Select top 3 absolute best chunks for LLM context
            top_chunks = scored_pool[:3]
        else:
            top_chunks = []

        # --- E. Synthesize Answer with LLM ---
        print("🤖 Generating synthesized answer...")
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

        print("\n" + "="*60)
        print("📝 SYNTHESIZED HYBRID ANSWER:")
        print("="*60)
        print(response.content)
        print("-" * 60)
        print(f"📖 Sources Referenced: {', '.join(sorted(sources_used))}")
        print("="*60)

    cursor.close()
    conn.close()
    print("🔌 Database connection closed.")

if __name__ == "__main__":
    main()