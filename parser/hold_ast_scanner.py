import ast
from pathlib import Path
from typing import NamedTuple, Dict, List, Any

class RepoNodeData(NamedTuple):
    node_type: str
    name: str
    line_start: int
    line_end: int
    parent_scope: str

class RepoASTVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.manifest: Dict[str, List[Any]] = {
            "classes": [],
            "functions": [],
            "imports": [],
            "calls": []
        }
        self._scope_stack: List[str]= ["global"]

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        class_info = RepoNodeData(
            node_type = "class",
            name = node.name,
            line_start = node.lineno,
            line_end=node.end_lineno or node.lineno,
            parent_scope = self._scope_stack[-1]
        )
        self.manifest["classes"].append(class_info._asdict())

        self._scope_stack.append(node.name)
        self.generic_visit(node)
        self._scope_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        func_info = RepoNodeData(
            node_type="function",
            name = node.name,
            line_start = node.lineno,
            line_end = node.end_lineno or node.lineno,
            parent_scope = self._scope_stack[-1]
        )
        self.manifest["functions"].append(func_info._asdict())

        self._scope_stack.append(node.name)
        self.generic_visit(node)
        self._scope_stack.pop()

    def visit_Import(self, node:ast.Import)-> None:
        for alias in node.names:
            self.manifest["imports"].append({
                "type": "standard",
                "module": alias.name,
                "alias": alias.asname,
                "line": node.lineno,
            })
    def visit_ImportFrom(self, node: ast.ImportForm) -> None:
        for alias in node.names:
            self.manifest["imports"].append({
                "type": "from",
                "module": node.module,
                "name": alias.name,
                "alias": alias.asname,
                "level": node.level,
                "line": node.lineno
            })
    def visit_Call(self, node: ast.Call) -> None:
        call_name = None
        if isinstance(node.func, ast.Name):
            call_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            call_name = node.func.attr

        if call_name:
            self.manifest["calls"].append({
                "target": call_name,
                "line": node.lineno,
                "scope": self._scope_stack[-1]
            })
        self.generic_visit(node)

