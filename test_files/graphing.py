import pickle
import networkx as nx
import json

# Load the graph from the .pkl file
def load_graph(graph_file):
    with open(graph_file, "rb") as f:
        graph = pickle.load(f)
    return graph

# Export the graph to JSON
def export_graph_to_json(graph, output_file):
    data = nx.node_link_data(graph)  # Convert graph to node-link format
    with open(output_file, "w") as f:
        json.dump(data, f)
    print(f"Graph exported to {output_file}")

# Example usage for HazMapApp
graph_file = r"c:\Users\emong\Desktop\noodl\indexes\HazMapApp\graph.pkl"
graph = load_graph(graph_file)

# Export to JSON for online visualization
export_graph_to_json(graph, "hazmapapp_graph.json")


