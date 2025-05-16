## open and walk the curriculum folder

import psycopg2
import os
import json
from sentence_transformers import SentenceTransformer
db = psycopg2.connect(os.environ['DATABASE_URL'])
from psycopg2.extras import execute_values
cursor = db.cursor()

model = SentenceTransformer('intfloat/multilingual-e5-large-instruct')
model.save("sentence_transformers_model")

for dirpath, dirnames, filenames in os.walk('/Users/annhoward/Library/Mobile Documents/iCloud~md~obsidian/Documents/multiverse_school_curriculum/Curriculum'):
    for filename in filenames:
        if filename.endswith('.md'):
            with open(os.path.join(dirpath, filename), 'r') as f:
                content = f.read()
                
                ## generate embedding for the content
                document_embeddings = model.encode(content)
                
                print(document_embeddings)
                print("Embedding Shape:", document_embeddings.shape)
                embeddings_fp64 = document_embeddings.astype('float').tolist()
                
                # Convert numpy array to Python list to make it compatible with PostgreSQL
                embedding = document_embeddings.tolist()
                document_content = content
                document_title = os.path.join(dirpath, filename)
                sql = '''
                INSERT INTO documents (document_text, document_title, vector_local)
                VALUES (%s, %s, %s)
                '''
                data = (document_content, document_title, embeddings_fp64)
                cursor.execute(sql, data)
                    
                db.commit()
                ## save the embedding to the database
                ## save the content to the database
                ## save the pathname to the database


