import streamlit.components.v1 as components
from pyvis.network import Network
import tempfile
import os

def render_graph(graph_data):
    """
    Renders a PyVis graph in Streamlit using the provided graph data.
    graph_data should be a dict with 'nodes' and 'edges' lists.
    """
    if "error" in graph_data:
        return f"Error loading graph: {graph_data['error']}"

    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])

    if not nodes:
        return "No graph data available."

    net = Network(height="500px", width="100%", bgcolor="#222222", font_color="white", notebook=False)
    
    # Add nodes
    for node in nodes:
        net.add_node(
            node["id"],
            label=node.get("label", node["id"]),
            title=node.get("title", ""),
            group=node.get("group", "concept")
        )

    # Add edges
    for edge in edges:
        net.add_edge(
            edge["from"],
            edge["to"],
            label=edge.get("label", ""),
            title=edge.get("title", "")
        )

    # Physics options for better layout
    net.force_atlas_2based()
    
    # Save to a temporary file and read it back
    # We use a fixed filename in the temp dir to avoid clutter, 
    # but in a multi-user app this would need to be unique per session.
    # For a local tool, this is fine.
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode='w+', encoding='utf-8') as tmp:
            net.save_graph(tmp.name)
            tmp.seek(0)
            html_content = tmp.read()
        
        # Clean up temp file
        os.unlink(tmp.name)
        
        components.html(html_content, height=510)
        return None
    except Exception as e:
        return f"Error rendering graph: {str(e)}"
