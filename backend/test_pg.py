import psycopg2

try:
    conn = psycopg2.connect(
        dbname="scheme_analyzer",
        user="postgres",
        password="postgres", # assuming default
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    conn.commit()
    print("Success: Connected to Postgres and pgvector is available!")
except Exception as e:
    print(f"Error: {e}")
