# Project Trace 🗺️(README IN PROGRESS)

## 🎯 Why I Built This

I needed a tool to track my own projects while building them. Automated code scanners generate noise — they infer structure a parser sees, not structure an architect understands. What I wanted was a whiteboard that knows the vocabulary of software: files, classes, functions, variables, imports, calls. One that lets me draw the architecture myself, as I understand it.

So I built one.

## 🖥️ What It Does

Project Trace is a manual-first repository visualization workbench. A desktop application for drawing and documenting software architecture as you build it — nodes, edges, hierarchy, and relationships — saved to a portable JSON workspace file.

Think Excalidraw, but purpose-built for code architecture diagrams, with semantic edge types that mean something to a developer.

- Spawn nodes by type via command palette: `FILE`, `FOLDER`, `CLASS`, `FUNCTION`, `VARIABLE`, `EXTERNAL`
- Draw directed edges with semantic relation types: `CALL`, `IMPORT`, `READ`, `WRITE`, `FLOW`, `EXTERNAL`
- Bidirectional edges supported (`<->` syntax)
- Directional arrows rendered mathematically using `atan2`
- Node nesting — `CLASS` inside `FILE`, `VARIABLE` inside `FUNCTION` — with boundary detection on drag-drop
- Delete nodes and edges via keyboard or command
- Layer filtering — `HIDE`/`SHOW` nodes and edges by type
- Infinite canvas with mouse-wheel zoom
- Full workspace persistence — save and load named JSON files, restoring exact node positions, hierarchy, and edge topology

## 🏗️ Architecture
Project-Trace/
├── engine/
│ └── repository_graph.py # State model — nodes, edges, hierarchy, serialization
├── ui/
│ ├── components/
│ │ └── canvas.py # QGraphicsScene, BlueprintNodeItem, BlueprintEdgeItem
│ └── workbench_main.py # QMainWindow, command palette, zoom, load/save
└── main.py
Clean separation — graph state in engine, visual representation in UI, command interface in workbench.

## 🛠️ Technical Stack

| Layer | Tools |
|---|---|
| UI Framework | PySide6 / Qt — QGraphicsScene, QGraphicsView, QMainWindow |
| Workspace Persistence | JSON serialization |
| Arrow Geometry | `math.atan2` |
| Node Identity | UUID-based — names are display only |
| Language | Python |

## 💡 Key Engineering Decisions

**Manual-first over automated AST scanning.** The tool serves the architect, not the parser. Structure is drawn as understood, not inferred.

**UUID identity for all nodes and edges.** Names are display only. Rename without breaking references.

**Parent sorting on serialization.** Parents always serialized before children. Prevents hydration order bugs on load.

**Coordinate system discipline.** Parent-local coordinates stored on save. No double-transform on load.

**Command palette over menus.** Keyboard-driven workflow. No mouse required for node creation.

## 🐛 Interesting Problem Solved

Qt's `QGraphicsItem` parent-child coordinate system caused a load bug — `CLASS` nodes appeared at wrong positions after reload. `pos()` returns parent-local coordinates when a parent exists. The fix was storing and restoring those coordinates directly, without `mapFromScene` conversion.

The broken line was:
```python
child_item.setPos(parent_item.mapFromScene(node.x, node.y))
```
The correct line:
```python
child_item.setPos(node.x, node.y)
```

## 📦 Current Status

Complete. Used actively during Project Trace's own development. Shareable — a colleague in a non-technical field is a potential user for the `HIDE`/`SHOW` layer filtering feature.

## 🤝 Project Credits

| Role | Contributor | Responsibility |
|---|---|---|
| **Lead Architect** | lynekojawa (Human) | Core idea, architectural decisions, audit, mathematics |
| **Logic Orchestrator** | PODO (Gemini) | System design, logic review, code review |
| **Junior Orchestrator** | PODO (GPT) | Supporting logic review, code review |
| **Master Planner** | Orion (Gemini) | Strategic planning, phase roadmaps |
| **Code Partner** | Dante (Claude) | Implementation review, debugging, Git strategy |
| **Code Partner** | mini-Dante (Claude) | Code review |