import math
from enum import Enum, auto
from typing import Dict, List, Optional
from engine.repository_graph import RepositoryGraph
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtWidgets import (
    QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem,
    QGraphicsItem, QGraphicsSceneMouseEvent, QGraphicsLineItem,
)
from PySide6.QtGui import QPen, QBrush, QColor, QPainter, QPolygonF

class NodeType(Enum):
    FILE = auto()
    FOLDER = auto()
    CLASS = auto()
    FUNCTION = auto()
    VARIABLE = auto()
    EXTERNAL = auto()

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
        if self.node_type == NodeType.FOLDER:
            self.setRect(0, 0, 180, 60)
        elif self.node_type == NodeType.FILE:
            self.setRect(0, 0, 500, 650)
        elif self.node_type == NodeType.CLASS:
            self.setRect(0, 0, 200, 100)
        elif self.node_type == NodeType.FUNCTION:
            self.setRect(0, 0, 160, 260)
        elif self.node_type == NodeType.VARIABLE:
            self.setRect(0, 0, 120, 40)
        elif self.node_type == NodeType.EXTERNAL:
            self.setRect(0, 0, 160, 60)


    def _get_color_theme(self) -> QColor:
        themes = {
            NodeType.FOLDER: QColor(241, 196, 15), #Yellow
            NodeType.FILE: QColor(41, 128, 185), #Blue
            NodeType.CLASS: QColor(230, 126, 34), #White
            NodeType.FUNCTION: QColor(46, 204, 113), #Green
            NodeType.VARIABLE: QColor(236, 240, 241), #Cyan
            NodeType.EXTERNAL: QColor(155, 89, 182), #Purple
        }
        return themes.get(self.node_type, QColor(200, 200, 200))

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
    RELATION_THEMES = {
        "CALL": QColor(39, 174, 96), #Green
        "IMPORT": QColor(1, 128, 185), #Blue
        "EXTERNAL": QColor(155, 89, 182), #Purple
        "READ": QColor(241, 196, 15), #Yellow
        "WRITE": QColor(241, 196, 15),
        "FLOW": QColor(255, 0, 0),
    }
    def __init__(self, edge_id: str, source: BlueprintNodeItem, target: BlueprintNodeItem, relation_type: str) -> None:
        super().__init__()
        self.edge_id = edge_id
        self.source_node = source
        self.target_node = target
        self.relation_type = relation_type

        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsFocusable)

        self.setZValue(10.0)

        self.relation_type = relation_type.upper()
        self.label = QGraphicsTextItem(self.relation_type, self)

        if self.relation_type =="FLOW":
            self.label.setVisible(False)
        else:
            self.label.setVisible(True)
            self.label.setDefaultTextColor(QColor(200, 200, 200))

        color = self.RELATION_THEMES.get(relation_type, QColor(255, 0, 0))
        self.setPen(QPen(color, 4, Qt.SolidLine))
        self.source_node.connected_edges.append(self)
        self.target_node.connected_edges.append(self)
        self.update_position()

    def update_position(self) -> None:
        if not self.source_node or not self.target_node:
            return
        if not hasattr(self, 'label'):
            return

        p1 = self.source_node.scenePos() + self.source_node.rect().center()
        p2 = self.target_node.scenePos() + self.target_node.rect().center()
        self.setLine(p1.x(), p1.y(), p2.x(), p2.y())

        if self.label.isVisible():
            mid_x = (p1.x() + p2.x()) / 2
            mid_y = (p1.y() + p2.y()) / 2
            self.label.setPos(mid_x, mid_y)

    def paint(self, painter, option, widget=None):
        painter.setPen(self.pen())
        line = self.line()
        painter.drawLine(line)
        if line.isNull(): return

        arrow_size = 15
        angle = math.atan2(-line.dy(), line.dx())
        #p1: depart, p2: end
        painter.setBrush(self.pen().color())
        painter.setRenderHint(QPainter.Antialiasing)

        p2_head = QPolygonF([
            line.p2(),
            line.p2() - QPointF(math.sin(angle + math.pi / 6) * arrow_size,
                                math.cos(angle + math.pi / 6) * arrow_size),
            line.p2() - QPointF(math.sin(angle - math.pi + math.pi / 6) * arrow_size,
                                math.cos(angle - math.pi + math.pi / 6) * arrow_size)
        ])

        painter.drawPolygon(p2_head)

        if self.is_bidirectional:
            p1_head = QPolygonF([
                line.p1(),
                line.p1() + QPointF(math.sin(angle - math.pi / 3) * arrow_size,
                                    math.cos(angle - math.pi / 3) * arrow_size),
                line.p1() + QPointF(math.sin(angle - math.pi + math.pi / 3) * arrow_size,
                                    math.cos(angle - math.pi + math.pi / 3) * arrow_size)
            ])
            painter.drawPolygon(p1_head)

class ManualWorkbenchCanvas(QGraphicsScene):
    def __init__(self, graph_instance: RepositoryGraph, parent: Optional[object] = None) -> None:
        super().__init__(parent)
        self.graph = graph_instance
        self.setSceneRect(-5000, -5000, 10000, 10000)
        self.setBackgroundBrush((QColor(15, 15, 20)))
        self.node_registry: Dict[str, BlueprintNodeItem] = {}

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Delete, Qt.Key_backspace):
            for item in self.selectedItems():
                if isinstance(item, BlueprintNodeItem):
                    self._delete_node(item)
                elif isinstance(item, BlueprintEdgeItem):
                    self._delete_edge(item)
        super().keyPressEvent(event)

    def _delete_node(self, node: BlueprintNodeItem):
        #remove connected visuals first
        for edge in list(node.connected_edges):
            self._delete_edge(edge)

        self.graph.remove_node(node.node_id)
        if node.node_id in self.node_registry:
            del self.node_registry[node.node_id]
        self.removeItem(node)

    def _delete_edge(self, edge: BlueprintEdgeItem):
        self.graph.remove_edge(edge.source_node.node_id, edge.target_node.node_id)

        if edge in edge.source_node.connected_edges:
            edge.source_node.connected_edges.remove(edge)
        if edge in edge.target_node.connected_edges:
            edge.target_node.connected_edges.remove(edge)

        self.removeItem(edge)

    def spawn_node(self, name: str, node_type: NodeType, x: float = 0.0, y: float = 0.0) -> BlueprintNodeItem:

        node_id = self.graph.add_node(name, node_type.name, x, y)

        node = BlueprintNodeItem(node_id, name, node_type)
        node.setPos(x, y)
        self.addItem(node)
        self.node_registry[node_id] = node
        return node

    def spawn_edge(self, source_name: str, target_name: str, relation_type: str = "CALL") -> Optional[BlueprintEdgeItem]:

        source_item = self._find_node_by_name(source_name)
        target_item = self._find_node_by_name(target_name)

        if not source_item or not target_item:
            return None


        edge_id = self.graph.add_edge(source_item.node_id, target_item.node_id, relation_type)
        if not edge_id: return None

        edge_item = BlueprintEdgeItem(edge_id, source_item, target_item, relation_type)

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
