import sys
from typing import Optional
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QGraphicsView,
    QLineEdit, QLabel, QHBoxLayout, QApplication
)
from PySide6.QtGui import QPainter, QTransform
from ui.components.canvas import ManualWorkbenchCanvas, NodeType


class TraceWorkbench(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Project Trace - Blueprint Workbench")
        self.resize(1024, 600)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.canvas = ManualWorkbenchCanvas(self)
        self.view = QGraphicsView(self.canvas, self)
        self.view.centerOn(0,0)
        self.view.setTransform(QTransform().scale(1.0, 1.0))
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

    @Slot()
    def _execute_vector_command(self)-> None:
        raw_text = self.command_palette.text().strip()
        self.command_palette.clear()

        if not raw_text or ":" not in raw_text:
            return

        prefix, name = raw_text.split(":", 1)
        prefix = prefix.upper().strip()
        name = name.strip()

        if not name:
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
            self.canvas.spawn_node(name, target_type, center_scene.x(), center_scene.y())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TraceWorkbench()
    window.show()
    sys.exit(app.exec())


