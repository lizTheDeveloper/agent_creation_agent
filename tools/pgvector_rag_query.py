from sentence_transformers import SentenceTransformer
import psycopg2
from psycopg2.extras import execute_values
import numpy as np

@function_tool
def pgvector_rag_query(query: str, host: str, port: int, dbname: str, user: str, password: str, top_k: int) -> list:
    
    # Generate query embedding
    model = SentenceTransformer('all-MiniLM-L6-v2')
    query_embedding = model.encode([query])[0].tolist()
    
    # Connect to PostgreSQL
    conn = psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password
    )
    cur = conn.cursor()
    
    # Perform vector similarity search
    query_sql = ''''''
    SELECT content, 1 - (embedding <=> %s::vector) AS similarity 
    FROM documents 
    ORDER BY similarity DESC 
    LIMIT %s;
    ''''''
    cur.execute(query_sql, (query_embedding, top_k))
    results = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return [{
        'document': row[0],
        'similarity': round(row[1], 4)
    } for row in results]