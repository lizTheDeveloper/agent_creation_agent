## open and walk the curriculum folder
from openai import OpenAI
import psycopg2
import os
import json
client = OpenAI()
db = psycopg2.connect(os.environ['DATABASE_URL'])
from psycopg2.extras import execute_values
cursor = db.cursor()

for dirpath, dirnames, filenames in os.walk('/Users/annhoward/Library/Mobile Documents/iCloud~md~obsidian/Documents/multiverse_school_curriculum/Curriculum'):
    for filename in filenames:
        if filename.endswith('.md'):
            with open(os.path.join(dirpath, filename), 'r') as f:
                content = f.read()
                
                ## generate embedding for the content

                response = client.embeddings.create(
                    input=content,
                    model="text-embedding-3-small"
                )

                print(response.data[0].embedding)
                
                embedding = response.data[0].embedding
                document_content = content
                document_title = os.path.join(dirpath, filename)
                sql = '''
                INSERT INTO documents (document_text, document_title, embeddings_small)
                VALUES (%s, %s, %s)
                '''
                data = (document_content, document_title, embedding)
                cursor.execute(sql, data)
                    
                db.commit()
                ## save the embedding to the database
                ## save the content to the database
                ## save the pathname to the database


