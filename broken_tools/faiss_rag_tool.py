import faiss
import numpy as np
from typing import List, Tuple

class RAGSystem:
    def __init__(self, dimension: int):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.documents = []

    def add_documents(self, embeddings: np.ndarray, documents: List[str]):
        """Adds documents and their embeddings to the index."""
        if embeddings.shape[1] != self.dimension:
            raise ValueError("Embedding dimensions do not match the index dimension.")
        self.index.add(embeddings)
        self.documents.extend(documents)

    def retrieve(self, query_embedding: np.ndarray, k: int = 5) -> List[Tuple[str, float]]:
        """Retrieves the top k documents similar to the query embedding."""
        if query_embedding.shape[0] != self.dimension:
            raise ValueError("Query embedding dimension does not match the index dimension.")
        distances, indices = self.index.search(query_embedding.reshape(1, -1), k)
        return [(self.documents[i], distances[0][j]) for j, i in enumerate(indices[0])]

    def get_document_count(self) -> int:
        """Returns the number of documents in the index."""
        return len(self.documents)

rag_system = RAGSystem(dimension=512)  # Dimension should match the model's embedding size

@function_tool
def add_to_index(embeddings: List[List[float]], documents: List[str]):
    """Adds documents and their embeddings to the FAISS index."""
    np_embeddings = np.array(embeddings)
    rag_system.add_documents(np_embeddings, documents)

@function_tool
def retrieve_documents(query_embedding: List[float], k: int = 5) -> List[Tuple[str, float]]:
    """Retrieves top k documents similar to the query embedding from the FAISS index."""
    np_query_embedding = np.array(query_embedding)
    return rag_system.retrieve(np_query_embedding, k)

@function_tool
def get_document_count() -> int:
    """Returns the number of documents currently in the FAISS index."""
    return rag_system.get_document_count()