import networkx as nx
from typing import List, Dict, Any
from .models import WorldObject, Morphism

class CategoryGraph:
    def __init__(self):
        # MultiDiGraph allows multiple edges between nodes (multiple laws/relationships)
        self.graph = nx.MultiDiGraph()

    def add_node(self, node: WorldObject):
        self.graph.add_node(node.id, data=node)

    def add_morphism(self, morphism: Morphism):
        self.graph.add_edge(
            morphism.source,
            morphism.target,
            label=morphism.label,
            rule=morphism.rule
        )

    def get_context(self, node_id: str) -> str:
        """Retrieves laws (morphisms) surrounding a concept for RAG."""
        if node_id not in self.graph:
            return ""
        
        # Get outgoing edges (laws starting from this concept)
        edges = self.graph.out_edges(node_id, data=True)
        context = []
        for u, v, data in edges:
            context.append(f"- {data.get('label', 'Relation')}: {data.get('rule', '')} (-> {v})")
        
        # Optionally, we could also look at incoming edges or neighbors
        return "\n".join(context)

    def export_for_vis(self) -> Dict[str, List[Dict[str, Any]]]:
        """Exports the graph in a format suitable for PyVis/Vis.js."""
        nodes = []
        for n_id, attrs in self.graph.nodes(data=True):
            node_data: WorldObject = attrs.get('data')
            if node_data:
                nodes.append({
                    "id": n_id,
                    "label": node_data.label,
                    "title": node_data.description,
                    "group": node_data.type
                })
            else:
                # Fallback if data is missing
                nodes.append({
                    "id": n_id,
                    "label": n_id,
                    "group": "unknown"
                })

        edges = []
        for u, v, key, attrs in self.graph.edges(keys=True, data=True):
            edges.append({
                "from": u,
                "to": v,
                "label": attrs.get('label', ''),
                "title": attrs.get('rule', '')
            })

        return {"nodes": nodes, "edges": edges}

    def clear(self):
        self.graph.clear()
