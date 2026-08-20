import psycopg2
from pgvector.psycopg2 import register_vector
from sentence_transformers import SentenceTransformer

# 1. Load a lightweight, open-source local embedding model (produces 384-dimensional vectors)
print("Loading local embedding model (all-MiniLM-L6-v2)...")
model = SentenceTransformer('all-MiniLM-L6-v2')

# 2. Define real text documents
documents = [
    "Network engineering involves configuring routers, switches, and firewalls.",
    "Python is a popular programming language for backend development and AI.",
    "PostgreSQL with pgvector allows efficient similarity searches for AI applications."
]

# Generate real vector embeddings for the text documents
print("Generating vector embeddings for documents...")
doc_embeddings = model.encode(documents).tolist()

# 3. Establish connection to your Docker PostgreSQL database
conn = psycopg2.connect(
    dbname="aidb",
    user="postgres",
    password="password",
    host="localhost",
    port="5432"
)

# Register pgvector extension types with psycopg2
register_vector(conn)
cursor = conn.cursor()

try:
    # 4. Create a table configured for 384 dimensions (matching our model)
    cursor.execute("""
        DROP TABLE IF EXISTS knowledge_base;
        CREATE TABLE knowledge_base (
            id SERIAL PRIMARY KEY,
            content TEXT,
            embedding VECTOR(384)
        );
    """)
    
    # Insert documents and their corresponding vector embeddings into PostgreSQL
    for content, emb in zip(documents, doc_embeddings):
        cursor.execute(
            "INSERT INTO knowledge_base (content, embedding) VALUES (%s, %s)",
            (content, emb)
        )
    conn.commit()
    print("Successfully stored real text documents and embeddings in PostgreSQL!")

    # 5. Perform a semantic similarity search using a brand new query string
    query = "How do I query data for AI systems using a database?"
    print(f"\nRunning search query: '{query}'")
    
    query_embedding = model.encode(query).tolist()

    cursor.execute("""
        SELECT content, embedding <=> %s::vector AS distance
        FROM knowledge_base
        ORDER BY distance ASC
        LIMIT 1;
    """, (query_embedding,))
    
    result = cursor.fetchone()
    print(f"Closest semantic match: '{result[0]}'")
    print(f"Distance score: {result[1]:.4f}")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    cursor.close()
    conn.close()