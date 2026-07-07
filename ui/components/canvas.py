from enum import Enum, auto
from typing import Dict, Optional
from engine.repository_graph import RepositoryGraph
from PySide6.QtCore import Qt, QRectF
from PySide6.QtWidgets import (
    QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem,
    QGraphicsItem, QGraphicsSceneMouseEvent
)
from PySide6.QtGui import QPen, QBrush, QColor, QPainter

class NodeType(Enum):
    FILE = auto()
    FUNCTION = auto()
    VARIABLE = auto()

class BlueprintNodeItem(QGraphicsRectItem):
    def __init__(self, node_id: str, name: str, node_type:NodeType, parent_item: Optional[QGraphicsItem] = None) -> None:
        super().__init__(parent_item)
        self.node_id = node_id
        self.name = name
        self.node_type = node_type

        self.setFlags(
            QGraphicsItem.ItemIsMovable |
            QGraphicsItem.ItemIsSelectable |
            QGraphicsItem.ItemSendsGeometryChanges
        )

        if self.node_type == NodeType.FILE:
            self.setZValue(1.0)
            self.setRect(0, 0, 240, 180)
        elif self.node_type == NodeType.FUNCTION:
            self.setZValue(2.0)
            self.setRect(0, 0, 180, 60)
        elif self.node_type == NodeType.VARIABLE:
            self.setZValue(3.0)
            self.setRect(0,  0, 140, 40)

        self.setPen(QPen(self._get_color_theme(), 2))
        self.setBrush(QBrush(QColor(25, 25, 35, 230)))
        self.label = QGraphicsTextItem(f"[{self.node_type.name}] {self.name}", self)
        self.label.setDefaultTextColor(QColor(230, 230, 235))
        self.label.setPos(6, 6)

    def _get_color_theme(self) -> QColor:
        if self.node_type == NodeType.FILE:
            return QColor(41, 128, 185) #Blue
        if self.node_type == NodeType.FUNCTION:
            return QColor(39, 174, 96) #Green
        return QColor(241, 196, 15) #Yellow

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

class ManualWorkbenchCanvas(QGraphicsScene):
    def __init__(self, graph_instance: RepositoryGraph, parent: Optional[object] = None) -> None:
        super().__init__(parent)
        self.graph = graph_instance
        self.setSceneRect(-1000, -1000, 2000, 2000)
        self.setBackgroundBrush((QColor(15, 15, 20)))
        self.node_registry: Dict[str, BlueprintNodeItem] = {}

    def spawn_node(self, name: str, node_type: NodeType, x: float = 0.0, y: float = 0.0) -> BlueprintNodeItem:
        node_str_type = node_type.name

        node_id = self.graph.add_node(name, node_str_type, x, y)

        node = BlueprintNodeItem(node_id, name, node_type)
        node.setPos(x, y)
        self.addItem(node)
        self.node_registry[name] = node
        return node
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


