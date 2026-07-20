import json
import uuid
from dataclasses import dataclass, asdict, field
from typing import Dict, Optional, Set, List

@dataclass
class NodeState:
    node_id: str
    name: str
    node_type: str
    x: float = 0.0
    y: float = 0.0
    parent_id: Optional[str] = None

@dataclass
class EdgeState:
    edge_id: str
    source_id: str
    target_id: str
    relation_type: str # "CALL", "IMPORT", "READ", "WRITE", "FLOW", "EXTERNAL"
    is_bidirectional: bool = False

class RepositoryGraph:
    def __init__(self) -> None:
        self.nodes:Dict[str, NodeState] = {}
        self.edges: Dict[str, EdgeState] = {}
        self.hierarchy: Dict[str, Set[str]] = {}

    def add_node(self, name: str, node_type: str, x:float = 0.0, y: float = 0.0, preset_id: Optional[str]=None) -> str:
        """Generates an identity record. Accepts a preset_id strictly for persistence tracking."""
        node_id = preset_id if preset_id else str(uuid.uuid4())
        self.nodes[node_id] = NodeState(
            node_id = node_id,
            name = name,
            node_type=node_type,
            x=x,
            y=y
        )
        return node_id

    def update_node_position(self, node_id: str, x: float, y: float) -> bool:
        if node_id not in self.nodes: return False
        self.nodes[node_id].x = x
        self.nodes[node_id].y = y
        return True

    def set_node_parent(self, child_id: str, parent_id: Optional[str])-> bool:
        if child_id not in self.nodes: return False

        old_parent = self.nodes[child_id].parent_id

        if old_parent and old_parent in self.hierarchy:
            self.hierarchy[old_parent].discard(child_id)

        self.nodes[child_id].parent_id = parent_id

        if parent_id:
            if parent_id not in self.nodes: return False
            if parent_id not in self.hierarchy: self.hierarchy[parent_id] = set()
            self.hierarchy[parent_id].add(child_id)

        return True

    def add_edge(self, source_id: str, target_id: str, relation_type: str, is_bidirectional = False) -> Optional[str]:
        """Establishes a directed logical edge vector between two verified workspace nodes"""
        if source_id not in self.nodes or target_id not in self.nodes:
            return None

        edge_lookup_key = f"{source_id} -> {target_id}"
        if edge_lookup_key in self.edges:
            return self.edges[edge_lookup_key].edge_id

        edge_id = str(uuid.uuid4())

        self.edges[edge_lookup_key] = EdgeState(
            edge_id=edge_id,
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type,
            is_bidirectional = is_bidirectional
        )
        return edge_id

    def export_workspace(self, file_path: str) -> None:
        for edge in self.edges.values():
            print(f"DEBUG SAVE: {edge.relation_type} is_bidirectional={edge.is_bidirectional}")
        """Serializes the exact in-memory directed topological state tree out to disk."""
        nodes_sorted = sorted(
            self.nodes.values(),
            key=lambda n: (0 if n.parent_id is None else 1)
        )
        serialized_data = {
            "version": "1.0.0",
            "nodes": [asdict(node) for node in nodes_sorted],
            "edges": [asdict(edge) for edge in self.edges.values()]
        }
        with open(file_path, "w", encoding="utf-8") as out_file:
            json.dump(serialized_data, out_file, indent = 4)

    def import_workspace(self, file_path: str) -> bool:
        """Purges active tracking frames and fully rebuilds topology from standard workspace.json."""
        try:
            with open(file_path, "r", encoding="utf-8") as in_file:
                data = json.load(in_file)

            # Clear active states
            self.nodes.clear()
            self.edges.clear()
            self.hierarchy.clear()

            # Phase 1 Hydration: Re-instantiate Vertices
            for node_raw in data.get("nodes", []):
                n_id = node_raw["node_id"]
                self.add_node(
                    name=node_raw["name"],
                    node_type=node_raw["node_type"],
                    x=node_raw["x"],
                    y=node_raw["y"],
                    preset_id=n_id
                )
                # Re-establish parent tree connections
                if node_raw.get("parent_id"):
                    self.set_node_parent(n_id, node_raw["parent_id"])

            # Phase 2 Hydration: Re-instantiate Directed Edges
            for edge_raw in data.get("edges", []):
                self.add_edge(
                    source_id=edge_raw["source_id"],
                    target_id=edge_raw["target_id"],
                    relation_type=edge_raw["relation_type"],
                    is_bidirectional = edge_raw.get("is_bidirectional", False)
                )
            return True
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            return False

    def remove_node(self, node_id: str) -> None:
        if node_id in self.hierarchy:
            children = list(self.hierarchy[node_id])
            for child_id in children:
                self.remove_node(child_id)
            del self.hierarchy[node_id]

        edges_to_remove = [
            edge_id for edge_id, edge in self.edges.items()
            if edge.source_id == node_id or edge.target_id == node_id
        ]
        for edge_id in edges_to_remove:
            del self.edges[edge_id]

        node_to_delete = self.nodes.get(node_id)

        if node_to_delete and node_to_delete.parent_id:
            parent_id = node_to_delete.parent_id
            if parent_id in self.hierarchy:
                self.hierarchy[parent_id].discard(node_id)

        if node_id in self.nodes:
            del self.nodes[node_id]


    def remove_edge(self, source_id: str, target_id: str) -> bool:
        edge_lookup_key = f"{source_id} -> {target_id}"
        if edge_lookup_key in self.edges:
            del self.edges[edge_lookup_key]
            return True
        return False