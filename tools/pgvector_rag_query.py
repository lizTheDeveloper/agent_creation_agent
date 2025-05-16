from sentence_transformers import SentenceTransformer
import psycopg2
from psycopg2.extras import execute_values
import numpy as np
import os
from agents import function_tool


@function_tool
def custom_tool(query: str) -> list:
    try:
            
        top_k = 5
        # Generate query embedding
        model = SentenceTransformer.load("sentence_transformers_model")
        # Extract first element to make it a 1D array
        query_embedding = model.encode([query])[0].astype('float').tolist()
        
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            os.environ['DATABASE_URL']
        )
        cur = conn.cursor()
        
        # Perform vector similarity search
        query_sql = '''
        SELECT document_text, (vector_local <-> %s::vector) as similarity, document_title
        FROM documents 
        ORDER BY similarity DESC 
        LIMIT %s;
        '''
        cur.execute(query_sql, (query_embedding, top_k))
        results = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return [{
            'document': row[0],
            'similarity': round(row[1], 4) if row[1] is not None else None
        } for row in results]
    except Exception as e:
        print(f"Error in custom_tool: {e}")
    finally:
        cur.close()
        conn.close()
        return []