from enum import Enum, auto
from typing import Dict, List, Optional
from engine.repository_graph import RepositoryGraph
from PySide6.QtCore import Qt, QRectF
from PySide6.QtWidgets import (
    QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem,
    QGraphicsItem, QGraphicsSceneMouseEvent, QGraphicsLineItem,
)
from PySide6.QtGui import QPen, QBrush, QColor, QPainter

class NodeType(Enum):
    FILE = auto()
    FUNCTION = auto()
    VARIABLE = auto()

class BlueprintNodeItem(QGraphicsRectItem):
    def __init__(self, node_id: str, name: str, node_type: NodeType, parent_item: Optional[QGraphicsItem] = None) -> None:
        super().__init__(parent_item)
        self.node_id = node_id
        self.name = name
        self.node_type = node_type
        self.connected_edges: List['BlueprintEdgeItem'] = []

        self.setFlags(
            QGraphicsItem.ItemIsMovable |
            QGraphicsItem.ItemIsSelectable |
            QGraphicsItem.ItemSendsGeometryChanges
        )

        #Geometry setup
        self._setup_geometry()
        #Visuals
        self.setPen(QPen(self._get_color_theme(), 2))
        self.setBrush(QBrush(QColor(25, 25, 35, 230)))

        self.label = QGraphicsTextItem(f"[{self.node_type.name}] {self.name}", self)
        self.label.setDefaultTextColor(QColor(230, 230, 235))
        self.label.setPos(6, 6)

    def _setup_geometry(self):
        if self.node_type == NodeType.FILE:
            self.setZValue(1.0);
            self.setRect(0, 0, 240, 180)
        elif self.node_type == NodeType.FUNCTION:
            self.setZValue(2.0);
            self.setRect(0, 0, 180, 60)
        else:
            self.setZValue(3.0);
            self.setRect(0, 0, 140, 40)

    def _get_color_theme(self) -> QColor:
        if self.node_type == NodeType.FILE:
            return QColor(41, 128, 185) #Blue
        if self.node_type == NodeType.FUNCTION:
            return QColor(39, 174, 96) #Green
        return QColor(241, 196, 15) #Yellow

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value: any) -> any:
        if change == QGraphicsItem.ItemPositionHasChanged and self.scene():
            scene = self.scene()
            if hasattr(scene, 'graph') and scene.graph:
                scene.graph.update_node_position(self.node_id, self.pos().x(), self.pos().y())

            for edge in self.connected_edges:
                edge.update_position()

        return super().itemChange(change, value)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent)-> None:
        """Triggers the physical boundary evaluation for compound node nesting on drop """
        super().mouseReleaseEvent(event)

        if self.node_type == NodeType.FILE:
            return
        scene = self.scene()
        if not scene or not hasattr(scene, 'graph'):
            return

        scene_polygon = self.mapToScene(self.rect())
        intersecting_items = scene.items(scene_polygon)

        potential_parent: Optional[BlueprintNodeItem] = None

        for item in intersecting_items:
            if isinstance(item, BlueprintNodeItem) and item != self:
                if item.node_type == NodeType.FILE:
                    potential_parent = item
                    break

        if potential_parent:
            if self.parentItem() != potential_parent:
                absolute_pos = self.scenePos()
                self.setParentItem(potential_parent)
                self.setPos(potential_parent.mapFromScene(absolute_pos))
                scene.graph.set_node_parent(self.node_id, potential_parent.node_id)
        else:
            if self.parentItem() is not None:
                absolute_pos = self.scenePos()
                self.setParentItem(None)
                self.setPos(absolute_pos)
                scene.graph.set_node_parent(self.node_id, None)


class BlueprintEdgeItem(QGraphicsLineItem):
    def __init__(self, edge_id: str, source: BlueprintNodeItem, target: BlueprintNodeItem) -> None:
        super().__init__()
        print(f"DEBUG: BlueprintEdgeItem __init__ reached for {edge_id}")
        self.edge_id = edge_id
        self.source_node = source
        self.target_node = target

        self.source_node.connected_edges.append(self)
        self.target_node.connected_edges.append(self)

        self.setZValue(10.0)
        self.setPen(QPen(QColor(255, 0, 0), 4, Qt.SolidLine))
        self.update_position()

    def update_position(self) -> None:
        print(f"DEBUG: Edge {self.edge_id} update_position called!")
        if not self.source_node or not self.target_node:
            print(f"DEBUG: Edge {self.edge_id} source/target node is None!")  # <--- 추가
            return

        p1 = self.source_node.scenePos() + self.source_node.rect().center()
        p2 = self.target_node.scenePos() + self.target_node.rect().center()
        print(f"DEBUG: Edge {self.edge_id} -> P1:{p1.x()},{p1.y()} to P2:{p2.x()},{p2.y()}")
        self.setLine(p1.x(), p1.y(), p2.x(), p2.y())


class ManualWorkbenchCanvas(QGraphicsScene):
    def __init__(self, graph_instance: RepositoryGraph, parent: Optional[object] = None) -> None:
        super().__init__(parent)
        self.graph = graph_instance
        self.setSceneRect(-1000, -1000, 2000, 2000)
        self.setBackgroundBrush((QColor(15, 15, 20)))
        self.node_registry: Dict[str, BlueprintNodeItem] = {}

    def spawn_node(self, name: str, node_type: NodeType, x: float = 0.0, y: float = 0.0) -> BlueprintNodeItem:

        node_id = self.graph.add_node(name, node_type.name, x, y)
        print(f"DEBUG: Graph created node {name} with ID: {node_id}")

        node = BlueprintNodeItem(node_id, name, node_type)
        node.setPos(x, y)
        self.addItem(node)
        self.node_registry[node_id] = node
        print(f"DEBUG: Current registry keys: {list(self.node_registry.keys())}")
        return node

    def spawn_edge(self, source_name: str, target_name: str, relation_type: str = "CALL") -> Optional[BlueprintEdgeItem]:

        source_item = self._find_node_by_name(source_name)
        target_item = self._find_node_by_name(target_name)

        if not source_item or not target_item:
            print(f"DEBUG: FAILED! Found Source: {bool(source_item)}, Found Target: {bool(target_item)}")
            return None

        print(f"DEBUG: Trying to link {source_name}({source_item.node_id}) -> {target_name}({target_item.node_id})")

        edge_id = self.graph.add_edge(source_item.node_id, target_item.node_id, relation_type)
        if not edge_id: return None

        edge_item = BlueprintEdgeItem(edge_id, source_item, target_item)
        self.addItem(edge_item)
        return edge_item

    def drawBackground(self, painter: QPainter, rect: QRectF) -> None:
        painter.fillRect(rect, QColor(15, 15, 20))
        pen = QPen(QColor(35, 35, 45), 0.75, Qt.DotLine)
        painter.setPen(pen)

        left = int(rect.left()) - (int(rect.left()) % 40)
        top = int(rect.top()) - (int(rect.top()) % 40)

        for x in range(left, int(rect.right()), 40):
            painter.drawLine(x, int(rect.top()), x, int(rect.bottom()))
        for y in range(top, int(rect.bottom()), 40):
            painter.drawLine(int(rect.left()), y, int(rect.right()), y)

    def _find_node_by_name(self, name: str) -> Optional[BlueprintNodeItem]:
        """Helper to resolve name to object since registry uses UUID keys."""
        for node in self.node_registry.values():
            if node.name == name:
                return node
        return None
