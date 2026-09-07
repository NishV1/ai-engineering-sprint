import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from pgvector.psycopg2 import register_vector
from sentence_transformers import SentenceTransformer
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import ChatOllama

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "vector_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")  # Change to your preferred local model

def initialize_database_and_schema():
    """Ensures target DB exists, enables pgvector, and creates table schema if missing."""
    try:
        temp_conn = psycopg2.connect(
            host=DB_HOST, port=DB_PORT, dbname="postgres", user=DB_USER, password=DB_PASSWORD
        )
        temp_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        temp_cursor = temp_conn.cursor()
        
        temp_cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s;", (DB_NAME,))
        if not temp_cursor.fetchone():
            print(f"📦 Database '{DB_NAME}' not found. Creating automatically...")
            temp_cursor.execute(f"CREATE DATABASE {DB_NAME};")
            print(f"✅ Database '{DB_NAME}' created!")
            
        temp_cursor.close()
        temp_conn.close()

        target_conn = psycopg2.connect(
            host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
        )
        target_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        target_cursor = target_conn.cursor()
        
        target_cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
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
        print(f"⚠️ Notice during database initialization: {e}")

def run_ingestion_if_needed(cursor, conn, model):
    """Checks if database is empty; if so, automatically scans and ingests PDFs."""
    cursor.execute("SELECT COUNT(*) FROM document_chunks;")
    count = cursor.fetchone()[0]
    
    if count > 0:
        print(f"✅ Found {count} existing chunks in database. Skipping re-ingestion.")
        return

    pdf_files = [f for f in os.listdir('.') if f.lower().endswith('.pdf')]
    if not pdf_files:
        print("⚠️ No PDF files found in project directory to ingest!")
        return

    print(f"📚 Found {len(pdf_files)} PDF(s) to ingest: {pdf_files}")
    
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    all_chunks = []
    
    for pdf in pdf_files:
        print(f"📄 Parsing {pdf}...")
        loader = PyPDFLoader(pdf)
        pages = loader.load()
        
        for page in pages:
            splits = splitter.split_text(page.page_content)
            for split in splits:
                all_chunks.append({
                    "text": split,
                    "source": pdf,
                    "page": page.metadata.get("page", 0) + 1
                })

    if not all_chunks:
        print("⚠️ No text content extracted from PDFs.")
        return

    print(f"🔄 Generating embeddings for {len(all_chunks)} chunks...")
    texts = [c["text"] for c in all_chunks]
    embeddings = model.encode(texts, batch_size=32, show_progress_bar=True)

    print("💾 Storing embeddings and metadata into PostgreSQL...")
    insert_query = """
        INSERT INTO document_chunks (chunk_text, source_file, page_number, embedding)
        VALUES (%s, %s, %s, %s);
    """
    
    for chunk, embedding in zip(all_chunks, embeddings):
        cursor.execute(insert_query, (
            chunk["text"],
            chunk["source"],
            chunk["page"],
            embedding.tolist()
        ))
    
    conn.commit()
    print("✅ Ingestion complete! All document chunks stored securely.\n")

def main():
    print("🚀 Initializing Generative RAG Engine...")
    
    # 1. Database Setup
    initialize_database_and_schema()

    # 2. Load Local Embedding Model & LLM
    print("📦 Loading embedding model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')

    print(f"🤖 Initializing local LLM ({OLLAMA_MODEL} via Ollama)...")
    llm = ChatOllama(model=OLLAMA_MODEL, temperature=0.1)

    # 3. Connect to Database
    print(f"🔌 Connecting to database '{DB_NAME}'...")
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
    )
    register_vector(conn)
    cursor = conn.cursor()
    print("✅ Connected successfully!\n")

    # 4. Auto-Ingest PDFs if empty
    run_ingestion_if_needed(cursor, conn, model)

    print("=" * 60)
    print("✨ Generative RAG Terminal Ready (Type 'exit' to quit)")
    print("=" * 60)

    try:
        while True:
            query = input("\nAsk a question about your docs: ").strip()
            
            if query.lower() in ['exit', 'quit']:
                print("\nExiting generative terminal. Have a great day!")
                break
                
            if not query:
                print("⚠️ Query cannot be empty. Please try again.")
                continue

            # Step A: Vector search for relevant chunks
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
                print("\n❌ No matching documents found in the database.")
                continue

            # Step B: Build context block and source list
            context_pieces = []
            sources_used = set()
            
            for chunk_text, source_file, page_number, distance in results:
                context_pieces.append(f"[Source: {source_file}, Page {page_number}]\n{chunk_text.strip()}")
                sources_used.add(f"{source_file} (Page {page_number})")

            combined_context = "\n\n---\n\n".join(context_pieces)

            # Step C: Construct prompt for the LLM
            prompt = f"""You are a precise technical AI assistant. Answer the user's question using ONLY the provided context snippets below. If the answer cannot be found in the context, state clearly that you do not know. Always cite your source file and page numbers.

Context:
{combined_context}

User Question: {query}
Answer:"""

            print("\n🤖 Generating synthesized answer...")
            response = llm.invoke(prompt)

            print("\n" + "=" * 60)
            print("📝 SYNTHESIZED ANSWER:")
            print("=" * 60)
            print(response.content.strip())
            print("-" * 60)
            print(f"📖 Sources Referenced: {', '.join(sources_used)}")
            print("=" * 60)

    except KeyboardInterrupt:
        print("\n\n👋 Session interrupted by user. Exiting gracefully...")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
    finally:
        cursor.close()
        conn.close()
        print("🔌 Database connection closed.")

if __name__ == "__main__":
    main()