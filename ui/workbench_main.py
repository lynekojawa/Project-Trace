import sys
from typing import Optional
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QGraphicsView,
    QLineEdit, QLabel, QHBoxLayout, QApplication
)
from PySide6.QtGui import QPainter, QTransform
from engine.repository_graph import RepositoryGraph
from ui.components.canvas import ManualWorkbenchCanvas, NodeType, BlueprintNodeItem, BlueprintEdgeItem


class TraceWorkbench(QMainWindow):
    def __init__(self, graph_instance: RepositoryGraph) -> None:
        super().__init__()
        self.graph = graph_instance
        self.setWindowTitle("Project Trace - Blueprint Workbench")
        self.resize(1024, 600)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.canvas = ManualWorkbenchCanvas(self.graph, self)
        self.view = QGraphicsView(self.canvas, self)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setDragMode(QGraphicsView.RubberBandDrag)
        self.view.setStyleSheet("border: none; background-color: #0f0f14;")
        main_layout.addWidget(self.view)

        palette_container = QWidget(self)
        palette_container.setStyleSheet("background-color: #15151c; border-top: 1px solid #252535;")
        palette_layout = QHBoxLayout(palette_container)
        palette_layout.setContentsMargins(10, 6, 10, 6)

        syntax_hint = QLabel("Command Vector Prefix: [FILE:|FUNC:|VAR:]", palette_container)
        syntax_hint.setStyleSheet("color: #7f8c8d; font-family:'Courier', monospace; font-size: 11px;")
        palette_layout.addWidget(syntax_hint)

        self.command_palette = QLineEdit(palette_container)
        self.command_palette.setPlaceholderText("e.g. FILE: main.py or FUNC: authenticate()")
        self.command_palette.setStyleSheet(
            "background-color: #0f0f14; color: #f0f0f5; border: 1px solid #353545; "
            "padding: 4px; font-family: 'Courier', monospace; border-radius: 3px;"
        )
        self.command_palette.returnPressed.connect(self._execute_vector_command)
        palette_layout.addWidget(self.command_palette)

        main_layout.addWidget(palette_container)

    def _hydrate_ui_from_graph(self) -> None:
        """Fully restores graph topology from the backend model."""
        self.canvas.blockSignals(True)
        self.canvas.clear()
        self.canvas.node_registry.clear()

        for node_id, node in self.graph.nodes.items():
            node_type_enum = NodeType[node.node_type]
            item = BlueprintNodeItem(node_id, node.name, node_type_enum)
            item.setPos(node.x, node.y)
            self.canvas.addItem(item)
            self.canvas.node_registry[node_id] = item

        for node_id, node in self.graph.nodes.items():
            if node.parent_id and node.parent_id in self.canvas.node_registry:
                child_item = self.canvas.node_registry[node_id]
                parent_item = self.canvas.node_registry[node.parent_id]
                child_item.setParentItem(parent_item)
                child_item.setPos(parent_item.mapFromScene(node.x, node.y))

        for edge_id, edge in self.graph.edges.items():
            source_item = self.canvas.node_registry.get(edge.source_id)
            target_item = self.canvas.node_registry.get(edge.target_id)

            if source_item and target_item:
                edge_item = BlueprintEdgeItem(edge_id, source_item, target_item, edge.relation_type)
                self.canvas.addItem(edge_item)

        self.canvas.blockSignals(False)
        self.canvas.update()


    @Slot()
    def _execute_vector_command(self)-> None:
        raw_text = self.command_palette.text().strip()
        self.command_palette.clear()
        if not raw_text: return

        if ":" in raw_text:
            prefix, argument = raw_text.split(":", 1)
            prefix = prefix.upper().strip()
            argument = argument.strip()
        else:
            prefix = raw_text.upper().strip()
            argument = ""

        if prefix == "SAVE":
            filename = f"{argument}.json" if argument else "workspace.json"
            self.graph.export_workspace(filename)
            print(f"DEBUG: Workspace saved to {filename}")
            return

        elif prefix == "LOAD":
            filename = f"{argument}.json" if argument else "workspace.json"
            if self.graph.import_workspace(filename):
                self._hydrate_ui_from_graph()
            return

        EDGE_RELATIONS = ["CALL", "IMPORT", "EXTERNAL", "READ", "WRITE", "CONNECT"]
        if prefix in EDGE_RELATIONS and  "->" in argument:
            source_name, target_name = argument.split("->", 1)
            self.canvas.spawn_edge(source_name.strip(), target_name.strip(), prefix)
            return

        elif prefix == "DELETE":
            if argument.upper() == "ALL":
                for node in list(self.canvas.node_registry.values()):
                    self.canvas._delete_node(node)
                print("DEBUG: Workspace cleared.")
            else:
                target_node = self.canvas._find_node_by_name(argument)
                if target_node:
                    self.canvas._delete_node(target_node)
                    print(f"DEBUG: Node '{argument}' deleted.")
                else:
                    print(f"DEBUG: Node '{argument}' not found.")
        elif prefix == "DELETE_EDGE" and "->" in argument:
            source_id, target_id = argument.split("->", 1)

            for item in self.canvas.items():
                if isinstance(item, BlueprintEdgeItem):
                    if item.source_node.name == source_id.strip() and \
                            item.target_node.name == target_id.strip():
                        self.canvas._delete_edge(item)
                        print(f"DEBUG: Edge {source_id}->{target_id} deleted.")
            return

        target_type: Optional[NodeType] = None
        if prefix == "FILE":
            target_type = NodeType.FILE
        elif prefix == "FUNC":
            target_type = NodeType.FUNCTION
        elif prefix == "VAR":
            target_type = NodeType.VARIABLE

        if target_type is not None:
            center_scene = self.view.mapToScene(self.view.viewport().rect().center())
            self.canvas.spawn_node(argument, target_type, center_scene.x(), center_scene.y())

if __name__ == "__main__":
    shared_graph = RepositoryGraph()
    app = QApplication(sys.argv)
    window = TraceWorkbench(shared_graph)
    window.show()
    sys.exit(app.exec())


