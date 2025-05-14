from typing import List
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
import numpy as np
import json

# Initializing the FAISS index
def initialize_faiss_index(data: List[str], embedding_model) -> FAISS:
    embeddings = embedding_model.embed(data)
    index = FAISS.from_embeddings(embeddings)
    return index

# Querying the FAISS index
def query_faiss_index(index: FAISS, query: str, embedding_model, top_k: int) -> List[str]:
    query_embedding = embedding_model.embed([query])[0]
    distances, indices = index.search(query_embedding, top_k)
    results = [index.data[i] for i in indices[0]]
    return results

# Main RAG system function
def rag_system(data: List[str], query: str, top_k: int = 3) -> List[str]:
    """Implements a Retrieval-Augmented Generation system using a FAISS index.
    Args:
        data: List of documents to index.
        query: User query for which retrieval is performed.
        top_k: Number of top documents to retrieve.
    Returns:
        List of retrieved documents as potential answers.
    """
    # Initialize embedding model
    embedding_model = OpenAIEmbeddings()
    # Initialize or Load FAISS index
    index = initialize_faiss_index(data, embedding_model)  
    # Query the FAISS index
    return query_faiss_index(index, query, embedding_model, top_k)