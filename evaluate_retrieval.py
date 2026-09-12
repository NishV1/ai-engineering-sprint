import psycopg2
from sentence_transformers import SentenceTransformer, CrossEncoder
from rank_bm25 import BM25Okapi
import numpy as np

# Configuration
DB_HOST = "127.0.0.1"
DB_PORT = "5432"
DB_NAME = "aidb"
DB_USER = "postgres"
DB_PASSWORD = "password"

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
RERANKER_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

print("📦 Loading evaluation models and database indices...")
embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
reranker = CrossEncoder(RERANKER_MODEL_NAME)

# 1. Load database chunks
conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)
cursor = conn.cursor()
cursor.execute("SELECT id, chunk_text, source_file, page_number FROM document_chunks;")
rows = cursor.fetchall()
cursor.close()
conn.close()

if not rows:
    print("❌ ERROR: Database contains 0 document chunks! Please ingest PDFs via UI/API before evaluating.")
    exit(1)

doc_ids = [r[0] for r in rows]
doc_texts = [r[1] for r in rows]
chunk_lookup = {r[0]: {"text": r[1], "source": r[2], "page": r[3]} for r in rows}
tokenized_corpus = [t.lower().split() for t in doc_texts]
bm25 = BM25Okapi(tokenized_corpus)
print(f"✅ Loaded {len(rows)} chunks from database into evaluation index.")


def retrieve_top_k(query: str, top_k: int = 5) -> list[dict]:
    """Runs Vector + BM25 + RRF + Cross-Encoder retrieval."""
    conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)
    cursor = conn.cursor()

    query_vector = embedding_model.encode(query).tolist()
    cursor.execute("""
        SELECT id, chunk_text, source_file, page_number, 1 - (embedding <=> %s::vector) AS sim
        FROM document_chunks ORDER BY embedding <=> %s::vector LIMIT 10;
    """, (query_vector, query_vector))
    vector_results = cursor.fetchall()
    cursor.close()
    conn.close()

    tokenized_query = query.lower().split()
    bm25_scores = bm25.get_scores(tokenized_query)
    top_bm25_indices = bm25_scores.argsort()[::-1][:10]

    rrf_scores = {}
    k = 60
    for rank, r in enumerate(vector_results):
        rrf_scores[r[0]] = rrf_scores.get(r[0], 0.0) + 1.0 / (k + (rank + 1))

    for rank, idx in enumerate(top_bm25_indices):
        d_id = doc_ids[idx]
        rrf_scores[d_id] = rrf_scores.get(d_id, 0.0) + 1.0 / (k + (rank + 1))

    sorted_rrf = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:10]
    candidate_ids = [item[0] for item in sorted_rrf]

    pairs = [[query, chunk_lookup[d]["text"]] for d in candidate_ids if d in chunk_lookup]
    meta_list = [chunk_lookup[d] for d in candidate_ids if d in chunk_lookup]

    if not pairs:
        return []

    scores = reranker.predict(pairs)
    ranked_results = sorted(zip(meta_list, scores), key=lambda x: x[1], reverse=True)
    return [item[0] for item in ranked_results[:top_k]]


def evaluate_pipeline(eval_dataset: list[dict], top_k: int = 5):
    """Evaluates Hit-Rate and MRR with detailed mismatch diagnostics."""
    hits = 0
    reciprocal_ranks = []

    print(f"\n📊 Evaluating {len(eval_dataset)} test queries (Top-K = {top_k})...\n")

    for idx, test_case in enumerate(eval_dataset, start=1):
        query = test_case["query"]
        expected_source = test_case["expected_source"]
        expected_page = test_case.get("expected_page")

        results = retrieve_top_k(query, top_k=top_k)
        found_rank = 0

        for rank, res in enumerate(results, start=1):
            source_match = res["source"] == expected_source
            page_match = (expected_page is None) or (res["page"] == expected_page)
            
            if source_match and page_match:
                found_rank = rank
                break

        if found_rank > 0:
            hits += 1
            reciprocal_ranks.append(1.0 / found_rank)
            print(f"[{idx}/{len(eval_dataset)}] ✅ Hit at Rank {found_rank} | Query: '{query}'")
        else:
            reciprocal_ranks.append(0.0)
            print(f"[{idx}/{len(eval_dataset)}] ❌ Miss | Query: '{query}'")
            print("   Top retrieved candidate metadata instead:")
            for r_idx, res in enumerate(results[:2], start=1):
                print(f"     Rank {r_idx}: Source='{res['source']}', Page={res['page']}")

    hit_rate = (hits / len(eval_dataset)) * 100
    mrr = np.mean(reciprocal_ranks)

    print("\n" + "=" * 45)
    print("📈 RETRIEVAL PERFORMANCE RESULTS")
    print("=" * 45)
    print(f"Total Test Queries : {len(eval_dataset)}")
    print(f"Hit-Rate@{top_k}        : {hit_rate:.2f}%")
    print(f"MRR                : {mrr:.4f}")
    print("=" * 45)


if __name__ == "__main__":
    test_cases = [
        {
            "query": "What request does the creature make regarding a female companion?",
            "expected_source": "Shelley_1888_Frankenstein.pdf",
            "expected_page": None  # Set to None first to verify document-level Hit-Rate
        },
        {
            "query": "How do thoughts affect our internal belief system?",
            "expected_source": "Dont-Believe-Everything-You-Think.pdf",
            "expected_page": None
        }
    ]

    evaluate_pipeline(test_cases, top_k=5)