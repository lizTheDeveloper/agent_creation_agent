import json

class GraphRAG:
    def __init__(self, data):
        self.graph = self.build_graph(data)

    def build_graph(self, data):
        graph = {}
        for node_id, node_info in data.items():
            graph[node_id] = node_info["edges"]
        return graph

    def retrieve_related(self, node_id):
        if node_id not in self.graph:
            raise ValueError("Node ID not in graph")
        return self.graph[node_id]

    def add_node(self, node_id, edges):
        if node_id in self.graph:
            raise ValueError("Node already exists")
        self.graph[node_id] = edges

    def remove_node(self, node_id):
        if node_id not in self.graph:
            raise ValueError("Node ID not in graph")
        del self.graph[node_id]

@function_tool
def manipulate_graph_rag(file_path: str, action: str, node_id: str, edges: dict) -> dict:
    """Manages a graph-based RAG (Retrieval-Augmented Generation) system using a JSON file as input. Can add, remove, or retrieve nodes."""
    with open(file_path, 'r') as f:
        data = json.load(f)

    rag = GraphRAG(data)

    if action == "retrieve":
        return {"result": rag.retrieve_related(node_id)}
    elif action == "add":
        rag.add_node(node_id, edges)
        with open(file_path, 'w') as f:
            json.dump(rag.graph, f)
        return {"result": f"Node {node_id} added."}
    elif action == "remove":
        rag.remove_node(node_id)
        with open(file_path, 'w') as f:
            json.dump(rag.graph, f)
        return {"result": f"Node {node_id} removed."}
    else:
        raise ValueError("Unsupported action")