from typing import List, Dict, Set, Optional, Any, Tuple
from app.graph.schemas import GraphNodeSchema, GraphEdgeSchema

class GraphTraversalEngine:
    """
    Controlled Graph Traversal & Query Safety Engine for ThreatTrace AI.
    Provides bounded neighborhood lookup, shortest path traversal, and relationship filtering.
    """

    @classmethod
    def get_neighbors(
        cls,
        node_id: str,
        nodes: List[GraphNodeSchema],
        edges: List[GraphEdgeSchema],
        max_depth: int = 2,
        min_confidence: float = 0.0
    ) -> Tuple[List[GraphNodeSchema], List[GraphEdgeSchema]]:
        safe_depth = min(max(1, max_depth), 3)  # Hard query safety limit: max depth 3
        visited_nodes: Set[str] = {node_id}
        result_edges: List[GraphEdgeSchema] = []

        current_level = {node_id}

        for _ in range(safe_depth):
            next_level: Set[str] = set()
            for edge in edges:
                if edge.confidence < min_confidence:
                    continue

                if edge.source_node in current_level and edge.target_node not in visited_nodes:
                    visited_nodes.add(edge.target_node)
                    next_level.add(edge.target_node)
                    result_edges.append(edge)
                elif edge.target_node in current_level and edge.source_node not in visited_nodes:
                    visited_nodes.add(edge.source_node)
                    next_level.add(edge.source_node)
                    result_edges.append(edge)

            current_level = next_level
            if not current_level:
                break

        result_nodes = [n for n in nodes if n.node_id in visited_nodes]
        return result_nodes, result_edges
