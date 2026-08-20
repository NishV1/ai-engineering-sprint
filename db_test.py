import psycopg2
from pgvector.psycopg2 import register_vector

# 1. Establish connection to your Docker PostgreSQL database
conn = psycopg2.connect(
    dbname="aidb",
    user="postgres",
    password="password",
    host="localhost",
    port="5432"
)

# 2. Register pgvector extension types with psycopg2
register_vector(conn)

cursor = conn.cursor()

try:
    # 3. Create a table with a vector column (using 3 dimensions for a simple test)
    cursor.execute("""
        DROP TABLE IF EXISTS items;
        CREATE TABLE items (
            id SERIAL PRIMARY KEY,
            name TEXT,
            embedding VECTOR(3)
        );
    """)
    
    # 4. Insert some mock data (embeddings)
    cursor.execute("INSERT INTO items (name, embedding) VALUES (%s, %s)", ("Document A", [0.1, 0.1, 0.9]))
    cursor.execute("INSERT INTO items (name, embedding) VALUES (%s, %s)", ("Document B", [0.8, 0.2, 0.1]))
    conn.commit()
    print("Successfully inserted vector data into PostgreSQL!")

    # 5. Perform a vector similarity search with explicit type casting
    query_vector = [0.1, 0.1, 0.8]
    cursor.execute("""
        SELECT name, embedding <=> %s::vector AS distance
        FROM items
        ORDER BY distance ASC
        LIMIT 1;
    """, (query_vector,))
    
    result = cursor.fetchone()
    print(f"Closest match to query: {result[0]} with a distance score of {result[1]:.4f}")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    cursor.close()
    conn.close()