import sys
import types

# --- RAGAS COMPATIBILITY PATCH ---
if "langchain_community.chat_models.vertexai" not in sys.modules:
    dummy_chat = types.ModuleType("langchain_community.chat_models.vertexai")
    dummy_chat.ChatVertexAI = type("ChatVertexAI", (object,), {})
    sys.modules["langchain_community.chat_models.vertexai"] = dummy_chat
# ---------------------------------

import os
import psycopg2
import pandas as pd
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from sentence_transformers import SentenceTransformer, CrossEncoder
from rank_bm25 import BM25Okapi
from langchain_ollama import ChatOllama
from langchain_community.embeddings import HuggingFaceEmbeddings
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

def run_evaluation():
    print("🚀 Initializing Ragas Evaluation Harness (Aligned with Ingested Corpus)...")

    # 1. Load Models & LLM
    embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    reranker = CrossEncoder(RERANKER_MODEL_NAME)
    llm = ChatOllama(model=OLLAMA_MODEL, temperature=0.0)

    evaluator_llm = LangchainLLMWrapper(llm)
    evaluator_embeddings = LangchainEmbeddingsWrapper(
        HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    )

    # 2. Connect to Database & Build BM25 Corpus Index
    conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)
    cursor = conn.cursor()

    cursor.execute("SELECT id, chunk_text, source_file, page_number FROM document_chunks;")
    rows = cursor.fetchall()
    
    doc_ids = [row[0] for row in rows]
    doc_texts = [row[1] for row in rows]
    doc_metadata = [{"source": row[2], "page": row[3]} for row in rows]
    
    tokenized_corpus = [text.lower().split() for text in doc_texts]
    bm25 = BM25Okapi(tokenized_corpus)
    print(f"✅ Indexed {len(doc_texts)} chunks successfully.")

    # 3. Define Ground-Truth Questions Aligned with Your Actual Documents (HyperFlex / Infrastructure)
    eval_data = {
        "question": [
            "What does the document discuss regarding HX node architecture and NFS datastore traffic?",
            "What information is provided about encryption and drive technologies?",
        ],
        "ground_truth": [
            "The documentation details HX node architecture, IOvisor operations, and NFS datastore traffic handling.",
            "The documentation outlines enterprise storage encryption features and underlying drive technologies within the infrastructure.",
        ],
        "answer": [],
        "contexts": []
    }

    print("\n🚀 Executing evaluation pipeline queries...")

    for query in eval_data["question"]:
        print(f"Processing query: '{query}'")

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

        # --- B. BM25 Keyword Search (Top 10) ---
        tokenized_query = query.lower().split()
        bm25_scores = bm25.get_scores(tokenized_query)
        top_bm25_indices = bm25_scores.argsort()[::-1][:10]

        # --- C. Reciprocal Rank Fusion (RRF) ---
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
        id_to_data = {row[0]: (row[1], {"source": row[2], "page": row[3]}) for row in rows if row[0] in combined_pool_ids}

        # --- D. Cross-Encoder Reranking ---
        rerank_pairs = []
        pool_ids_ordered = []
        for doc_id in combined_pool_ids:
            if doc_id in id_to_data:
                text, meta = id_to_data[doc_id]
                rerank_pairs.append([query, text])
                pool_ids_ordered.append((doc_id, text, meta))

        if rerank_pairs:
            rerank_scores = reranker.predict(rerank_pairs)
            scored_pool = list(zip(pool_ids_ordered, rerank_scores))
            scored_pool.sort(key=lambda x: x[1], reverse=True)
            top_chunks = scored_pool[:3]
        else:
            top_chunks = []

        # --- E. Synthesize Answer with LLM ---
        context_blocks = []
        retrieved_contexts = []

        for item, score in top_chunks:
            doc_id, text, meta = item
            filename = meta.get("source", "unknown")
            page = meta.get("page", "unknown")
            context_blocks.append(f"[Source: {filename}, Page {page}]\n{text}")
            retrieved_contexts.append(text)

        context_str = "\n\n---\n\n".join(context_blocks)

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", "You are an expert technical assistant. Answer the user's question accurately using ONLY the provided context. Include source file names and page citations for every claim."),
            ("human", "Context:\n{context}\n\nQuestion: {question}")
        ])

        chain = prompt_template | llm
        response = chain.invoke({"context": context_str, "question": query})

        eval_data["answer"].append(response.content)
        eval_data["contexts"].append(retrieved_contexts)

    cursor.close()
    conn.close()

    # 4. Evaluate via Ragas
    dataset = Dataset.from_dict({
        "question": eval_data["question"],
        "answer": eval_data["answer"],
        "contexts": eval_data["contexts"],
        "ground_truth": eval_data["ground_truth"]
    })

    print("\n📊 Running Ragas Evaluation Metrics...")
    
    result = evaluate(
        dataset=dataset,
        metrics=[
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall,
        ],
        llm=evaluator_llm,
        embeddings=evaluator_embeddings,
    )

    print("\n✅ Evaluation Successful!")
    print(result)
    
    df = result.to_pandas()
    df.to_csv("evaluation_report.csv", index=False)
    print("📁 Detailed report saved to evaluation_report.csv")

if __name__ == "__main__":
    run_evaluation()