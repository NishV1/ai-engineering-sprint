import os
import psycopg2
from pgvector.psycopg2 import register_vector
from sentence_transformers import SentenceTransformer
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

pdf_path = "sample.pdf"

if not os.path.exists(pdf_path):
    print(f"Error: Could not find '{pdf_path}' in the project directory.")
    print("Please place a sample PDF named 'sample.pdf' in your project root and try again.")
    exit(1)

print(f"Loading and parsing '{pdf_path}'...")

# 1. Load the PDF using LangChain's PyPDFLoader
loader = PyPDFLoader(pdf_path)
pages = loader.load()
print(f"Successfully loaded {len(pages)} pages from the PDF.\n")

# 2. Extract text and attach page-level metadata
raw_documents = []
for page in pages:
    raw_documents.append({
        "content": page.page_content,
        "source": os.path.basename(page.metadata.get("source", pdf_path)),
        "page": page.metadata.get("page", 0) + 1  # 1-indexed page numbers for humans
    })

# 3. Configure Text Splitter to process chunks while retaining metadata lineage
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=50,
    separators=["\n\n", "\n", " ", ""]
)

processed_chunks = []
for doc in raw_documents:
    splits = text_splitter.split_text(doc["content"])
    for split in splits:
        processed_chunks.append({
            "content": split,
            "source": doc["source"],
            "page": doc["page"]
        })

print(f"Split PDF into {len(processed_chunks)} total chunks with metadata tracking.\n")

# 4. Generate Embeddings for all chunks
print("Generating vector embeddings...")
model = SentenceTransformer('all-MiniLM-L6-v2')
texts_to_embed = [chunk["content"] for chunk in processed_chunks]
embeddings = model.encode(texts_to_embed).tolist()

# 5. Connect to PostgreSQL and store chunks + metadata
conn = psycopg2.connect(
    dbname="aidb",
    user="postgres",
    password="password",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()
cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
register_vector(conn)

try:
    # Create an upgraded table with metadata columns
    cursor.execute("""
        DROP TABLE IF EXISTS pdf_chunks;
        CREATE TABLE pdf_chunks (
            id SERIAL PRIMARY KEY,
            source_file TEXT,
            page_number INT,
            content TEXT,
            embedding VECTOR(384)
        );
    """)

    # Insert chunks with their source file and page numbers
    for chunk, emb in zip(processed_chunks, embeddings):
        cursor.execute(
            """
            INSERT INTO pdf_chunks (source_file, page_number, content, embedding) 
            VALUES (%s, %s, %s, %s)
            """,
            (chunk["source"], chunk["page"], chunk["content"], emb)
        )
    
    conn.commit()
    print(f"Successfully stored all {len(processed_chunks)} PDF chunks and metadata into PostgreSQL!\n")

    # 6. Run a test search query against the PDF database
    query = "What is the main topic of this document?"
    print(f"Running semantic search query: '{query}'")
    
    query_embedding = model.encode(query).tolist()

    cursor.execute("""
        SELECT source_file, page_number, content, embedding <=> %s::vector AS distance
        FROM pdf_chunks
        ORDER BY distance ASC
        LIMIT 1;
    """, (query_embedding,))
    
    result = cursor.fetchone()
    if result:
        print(f"\n--- Best Match Found ---")
        print(f"Source File: {result[0]}")
        print(f"Page Number: {result[1]}")
        print(f"Content Snippet: '{result[2].strip()}'")
        print(f"Distance Score: {result[3]:.4f}")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    cursor.close()
    conn.close()