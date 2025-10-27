#!/usr/bin/env python3
"""
Module Call Graph Builder (single-file)

Builds a call graph of module-level functions and class methods within
one Python file, using heuristic AST analysis.

Output: Graphviz DOT file (can be converted to PNG with graphviz).

Usage:
  python3 module_callgraph.py \
    --file /absolute/path/to/module.py \
    --out-dir /absolute/path/to/output

Notes:
- Only intra-module calls are considered (calls to functions/methods
  defined in the same file).
- Resolves calls by name for module functions, and handles common
  method cases: self.method(), cls.method(), ClassName.method().
- For unknown variable.method() it links if method name is unique
  across all classes in the module.
"""

from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class FunctionDefInfo:
    name: str
    lineno: int


@dataclass
class MethodDefInfo:
    class_name: str
    method_name: str
    lineno: int

    @property
    def fqname(self) -> str:
        return f"{self.class_name}.{self.method_name}"


@dataclass
class ModuleDefs:
    file_path: Path
    functions: Dict[str, FunctionDefInfo]
    classes: Dict[str, Dict[str, MethodDefInfo]]  # class -> {method -> info}

    @property
    def method_name_to_fq(self) -> Dict[str, List[str]]:
        mapping: Dict[str, List[str]] = {}
        for class_name, methods in self.classes.items():
            for method_name in methods.keys():
                mapping.setdefault(method_name, []).append(f"{class_name}.{method_name}")
        return mapping


class ModuleCollector(ast.NodeVisitor):
    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path
        self.functions: Dict[str, FunctionDefInfo] = {}
        self.classes: Dict[str, Dict[str, MethodDefInfo]] = {}

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # type: ignore[override]
        self.functions[node.name] = FunctionDefInfo(name=node.name, lineno=getattr(node, "lineno", 1))

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:  # type: ignore[override]
        self.functions[node.name] = FunctionDefInfo(name=node.name, lineno=getattr(node, "lineno", 1))

    def visit_ClassDef(self, node: ast.ClassDef) -> None:  # type: ignore[override]
        class_name = node.name
        methods: Dict[str, MethodDefInfo] = {}
        for body in node.body:
            if isinstance(body, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods[body.name] = MethodDefInfo(
                    class_name=class_name,
                    method_name=body.name,
                    lineno=getattr(body, "lineno", 1),
                )
        self.classes[class_name] = methods
        # Do not recurse; methods already collected

    def build(self) -> ModuleDefs:
        return ModuleDefs(file_path=self.file_path, functions=self.functions, classes=self.classes)


class CallGraphBuilder:
    def __init__(self, module_defs: ModuleDefs, ast_root: ast.AST) -> None:
        self.defs = module_defs
        self.root = ast_root
        self.edges: Set[Tuple[str, str]] = set()
        self.nodes: Set[str] = set()

    def build(self) -> None:
        # Add all nodes upfront
        for fname in self.defs.functions.keys():
            self.nodes.add(f"func:{fname}")
        for class_name, methods in self.defs.classes.items():
            for mname in methods.keys():
                self.nodes.add(f"method:{class_name}.{mname}")

        # Walk again to compute calls per function/method
        for node in self.root.body if isinstance(self.root, ast.Module) else []:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._collect_calls_in_function(node)
            elif isinstance(node, ast.ClassDef):
                for body in node.body:
                    if isinstance(body, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        self._collect_calls_in_method(node.name, body)

    def _add_edge(self, caller: str, callee: str) -> None:
        self.edges.add((caller, callee))

    def _collect_calls_in_function(self, func_node: ast.AST) -> None:
        caller = f"func:{getattr(func_node, 'name', '<anon>')}"

        class V(ast.NodeVisitor):
            def __init__(self, outer: CallGraphBuilder) -> None:
                self.outer = outer

            def visit_Call(self, node: ast.Call) -> None:  # type: ignore[override]
                try:
                    func = node.func
                    if isinstance(func, ast.Name):
                        name = func.id
                        if name in self.outer.defs.functions:
                            self.outer._add_edge(caller, f"func:{name}")
                    elif isinstance(func, ast.Attribute):
                        self._handle_attribute_call(caller, current_class=None, attr_node=func)
                finally:
                    self.generic_visit(node)

            def _handle_attribute_call(self, caller: str, current_class: Optional[str], attr_node: ast.Attribute) -> None:
                value = attr_node.value
                method_name = attr_node.attr
                # ClassName.method(...)
                if isinstance(value, ast.Name) and value.id in self.outer.defs.classes:
                    class_name = value.id
                    if method_name in self.outer.defs.classes[class_name]:
                        self.outer._add_edge(caller, f"method:{class_name}.{method_name}")
                        return
                # Unknown var.method(...) -> unique method name fallback
                candidates = self.outer.defs.method_name_to_fq.get(method_name, [])
                if len(candidates) == 1:
                    self.outer._add_edge(caller, f"method:{candidates[0]}")

        V(self).visit(func_node)

    def _collect_calls_in_method(self, class_name: str, method_node: ast.AST) -> None:
        caller = f"method:{class_name}.{getattr(method_node, 'name', '<anon>')}"

        class V(ast.NodeVisitor):
            def __init__(self, outer: CallGraphBuilder) -> None:
                self.outer = outer

            def visit_Call(self, node: ast.Call) -> None:  # type: ignore[override]
                try:
                    func = node.func
                    if isinstance(func, ast.Name):
                        name = func.id
                        if name in self.outer.defs.functions:
                            self.outer._add_edge(caller, f"func:{name}")
                    elif isinstance(func, ast.Attribute):
                        self._handle_attribute_call(caller, current_class=class_name, attr_node=func)
                finally:
                    self.generic_visit(node)

            def _handle_attribute_call(self, caller: str, current_class: Optional[str], attr_node: ast.Attribute) -> None:
                value = attr_node.value
                method_name = attr_node.attr
                # self.method(...) or cls.method(...)
                if isinstance(value, ast.Name) and value.id in {"self", "cls"} and current_class is not None:
                    methods = self.outer.defs.classes.get(current_class, {})
                    if method_name in methods:
                        self.outer._add_edge(caller, f"method:{current_class}.{method_name}")
                        return
                # ClassName.method(...)
                if isinstance(value, ast.Name) and value.id in self.outer.defs.classes:
                    class_name = value.id
                    if method_name in self.outer.defs.classes[class_name]:
                        self.outer._add_edge(caller, f"method:{class_name}.{method_name}")
                        return
                # Unknown var.method(...) -> unique method fallback
                candidates = self.outer.defs.method_name_to_fq.get(method_name, [])
                if len(candidates) == 1:
                    self.outer._add_edge(caller, f"method:{candidates[0]}")

        V(self).visit(method_node)

    def write_dot(self, out_path: Path) -> None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding="utf-8") as f:
            f.write("digraph ModuleCallGraph {\n")
            f.write("  rankdir=LR;\n")
            # Nodes
            for node in sorted(self.nodes):
                label = node
                if node.startswith("func:"):
                    label = node[len("func:"):]
                    f.write(f"  \"{node}\" [shape=box, style=filled, fillcolor=lightgray, label=\"{label}\"];\n")
                elif node.startswith("method:"):
                    label = node[len("method:"):]
                    f.write(f"  \"{node}\" [shape=ellipse, label=\"{label}\"];\n")
                else:
                    f.write(f"  \"{node}\";\n")
            # Edges
            for u, v in sorted(self.edges):
                f.write(f"  \"{u}\" -> \"{v}\";\n")
            f.write("}\n")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build a call graph for a single Python module (functions + class methods)")
    p.add_argument("--file", required=True, help="Path to the Python file to analyze")
    p.add_argument("--out-dir", required=True, help="Directory to write the DOT file")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    file_path = Path(args.file).resolve()
    out_dir = Path(args.out_dir).resolve()

    try:
        source = file_path.read_text(encoding="utf-8", errors="ignore")
        root = ast.parse(source, filename=str(file_path))
    except Exception as e:
        raise SystemExit(f"Failed to parse {file_path}: {e}")

    collector = ModuleCollector(file_path)
    collector.visit(root)
    defs = collector.build()

    builder = CallGraphBuilder(defs, root)
    builder.build()

    dot_path = out_dir / (file_path.stem + ".dot")
    builder.write_dot(dot_path)
    print(f"DOT: {dot_path}")


if __name__ == "__main__":
    main()