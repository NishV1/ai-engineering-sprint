import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from pgvector.psycopg2 import register_vector
from sentence_transformers import SentenceTransformer

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "vector_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")

def ensure_database_and_schema():
    """Ensures target DB exists, enables pgvector, and creates table schema if missing."""
    try:
        # Step 1: Connect to default 'postgres' db to ensure target DB exists
        temp_conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname="postgres",
            user=DB_USER,
            password=DB_PASSWORD
        )
        temp_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        temp_cursor = temp_conn.cursor()
        
        temp_cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s;", (DB_NAME,))
        exists = temp_cursor.fetchone()
        
        if not exists:
            print(f"📦 Database '{DB_NAME}' not found. Creating it automatically...")
            temp_cursor.execute(f"CREATE DATABASE {DB_NAME};")
            print(f"✅ Database '{DB_NAME}' created successfully!")
            
        temp_cursor.close()
        temp_conn.close()

        # Step 2: Connect to target DB, enable extension, and ensure table schema exists
        target_conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        target_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        target_cursor = target_conn.cursor()
        
        target_cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        
        # Ensure document_chunks table exists so queries never throw a relation error
        target_cursor.execute("""
            CREATE TABLE IF NOT EXISTS document_chunks (
                id SERIAL PRIMARY KEY,
                chunk_text TEXT,
                source_file TEXT,
                page_number INT,
                embedding VECTOR(384)
            );
        """)
        
        target_cursor.close()
        target_conn.close()
        
    except Exception as e:
        print(f"⚠️ Notice during database pre-flight check: {e}")

def main():
    print("🚀 Initializing AI Engineering CLI Search Interface...")
    
    # 0. Pre-flight check to guarantee database, extension, and table exist
    ensure_database_and_schema()

    # 1. Load the local embedding model
    print("📦 Loading embedding model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # 2. Connect to the target vector database
    print(f"🔌 Connecting to PostgreSQL database '{DB_NAME}'...")
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    
    register_vector(conn)
    cursor = conn.cursor()
    print("✅ Connected successfully!\n")

    print("=" * 60)
    print("🔍 RAG Vector Search Terminal Ready (Type 'exit' to quit)")
    print("=" * 60)

    try:
        while True:
            query = input("\nEnter your search query: ").strip()
            
            if query.lower() in ['exit', 'quit']:
                print("\nExiting search terminal. Have a great day!")
                break
                
            if not query:
                print("⚠️ Query cannot be empty. Please try again.")
                continue

            query_embedding = model.encode(query).tolist()

            sql_query = """
                SELECT chunk_text, source_file, page_number, (embedding <=> %s::vector) AS distance
                FROM document_chunks
                ORDER BY distance ASC
                LIMIT 3;
            """
            
            cursor.execute(sql_query, (query_embedding,))
            results = cursor.fetchall()

            if not results:
                print("\n❌ Table exists, but no chunks found. (Make sure you've ingested your PDF files using your ingestion script!)")
                continue

            print(f"\nTop {len(results)} Semantic Matches Found:\n")
            print("-" * 60)

            for idx, (chunk_text, source_file, page_number, distance) in enumerate(results, start=1):
                similarity_score = max(0.0, 1.0 - (distance / 2.0)) * 100
                
                print(f"[{idx}] Source: {source_file} (Page {page_number})")
                print(f"    Relevance Score: {similarity_score:.1f}% (Distance: {distance:.4f})")
                print(f"    Snippet: \"{chunk_text.strip()}\"")
                print("-" * 60)

    except KeyboardInterrupt:
        print("\n\n👋 Search session interrupted by user. Exiting gracefully...")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
    finally:
        cursor.close()
        conn.close()
        print("🔌 Database connection closed.")

if __name__ == "__main__":
    main()