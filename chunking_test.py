import psycopg2
from pgvector.psycopg2 import register_vector
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 1. Simulate a long, unstructured document (e.g., system logs or tech docs)
long_document = """
Network engineering involves the setup, configuration, and maintenance of network hardware and infrastructure. 
Routers, switches, and firewalls form the backbone of modern enterprise networking, ensuring secure and fast packet routing.

Python has emerged as the premier programming language for backend engineering, automation, and artificial intelligence. 
With frameworks like FastAPI and LangChain, developers can rapidly prototype and deploy scalable AI microservices.

PostgreSQL is a powerful, enterprise-grade relational database. Combined with the pgvector extension, 
it transforms into a high-performance vector database capable of executing lightning-fast similarity searches 
for Retrieval-Augmented Generation (RAG) pipelines.
"""

print(f"Original Document Length: {len(long_document)} characters\n")

# 2. Configure the Recursive Character Text Splitter
# We set a small chunk size to see how it breaks down paragraphs cleanly
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=40,
    separators=["\n\n", "\n", " ", ""]
)

# Split the document into chunks
chunks = text_splitter.split_text(long_document)
print(f"Successfully split document into {len(chunks)} chunks!\n")

for idx, chunk in enumerate(chunks):
    print(f"--- Chunk {idx+1} ({len(chunk)} chars) ---")
    print(chunk.strip())
    print()

# 3. Load our local embedding model
print("Loading embedding model...")
model = SentenceTransformer('all-MiniLM-L6-v2')

# Generate embeddings for all chunks in a batch
chunk_embeddings = model.encode(chunks).tolist()

# 4. Connect to PostgreSQL and store the chunks
conn = psycopg2.connect(
    dbname="aidb",
    user="postgres",
    password="password",
    host="localhost",
    port="5432"
)

cursor = conn.cursor()
# ENABLE THE EXTENSION FIRST
cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;") 
# NOW REGISTER IT
register_vector(conn)

try:
    # Create a table for chunked knowledge base
    cursor.execute("""
        DROP TABLE IF EXISTS document_chunks;
        CREATE TABLE document_chunks (
            id SERIAL PRIMARY KEY,
            chunk_index INT,
            content TEXT,
            embedding VECTOR(384)
        );
    """)

    # Insert all chunks and their embeddings
    for idx, (content, emb) in enumerate(zip(chunks, chunk_embeddings)):
        cursor.execute(
            "INSERT INTO document_chunks (chunk_index, content, embedding) VALUES (%s, %s, %s)",
            (idx, content, emb)
        )
    
    conn.commit()
    print(f"Successfully stored all {len(chunks)} chunks and vectors into PostgreSQL!")

    # 5. Run a test semantic search against our chunked database
    query = "How do routers and switches relate to enterprise systems?"
    print(f"\nRunning search query: '{query}'")
    
    query_embedding = model.encode(query).tolist()

    cursor.execute("""
        SELECT chunk_index, content, embedding <=> %s::vector AS distance
        FROM document_chunks
        ORDER BY distance ASC
        LIMIT 1;
    """, (query_embedding,))
    
    result = cursor.fetchone()
    print(f"\nTop Matching Chunk ID: {result[0] + 1}")
    print(f"Content: '{result[1].strip()}'")
    print(f"Distance Score: {result[2]:.4f}")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    cursor.close()
    conn.close()