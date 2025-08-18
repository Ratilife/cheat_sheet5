#!/usr/bin/env python3
"""
Method Call Analyzer

- Finds where a given class method is used across a Python project
- Builds a call graph starting from that method (static, heuristic)
- Saves results to .txt and .png (or .dot if drawing libs unavailable)

Usage:
  python3 method_call_analyzer.py \
    --project-root /path/to/project \
    --target "ClassName.method_name" \
    --output-dir ./analysis_output \
    --max-depth 5

Supports target formats:
- method
- ClassName.method
- module.path:ClassName.method

Limitations:
- Heuristic static analysis without full type inference
- Dynamic dispatch and metaprogramming may not be resolved
"""

from __future__ import annotations

import argparse
import ast
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Iterable

# Optional rendering libs
try:
    import networkx as nx  # type: ignore
    import matplotlib.pyplot as plt  # type: ignore
    HAVE_NX = True
except Exception:  # pragma: no cover - env-dependent
    nx = None  # type: ignore
    plt = None  # type: ignore
    HAVE_NX = False


@dataclass(frozen=True)
class MethodRef:
    module: str
    class_name: str
    method_name: str
    file_path: Path
    line_number: int

    @property
    def fq_method(self) -> str:
        return f"{self.module}:{self.class_name}.{self.method_name}"

    @property
    def fq_class(self) -> str:
        return f"{self.module}:{self.class_name}"


@dataclass
class ClassInfo:
    module: str
    class_name: str
    file_path: Path
    line_number: int
    methods: Dict[str, MethodRef]


@dataclass
class ModuleInfo:
    file_path: Path
    module: str
    ast_root: ast.AST
    imports_name_to_target: Dict[str, str]
    class_names_in_module: Set[str]


class ProjectIndex:
    def __init__(self) -> None:
        self.classes_by_fq: Dict[str, ClassInfo] = {}
        self.classes_by_simple: Dict[str, List[ClassInfo]] = {}
        self.methods_by_fq: Dict[str, MethodRef] = {}
        self.modules_by_file: Dict[Path, ModuleInfo] = {}

    def add_class(self, cls: ClassInfo) -> None:
        fq = f"{cls.module}:{cls.class_name}"
        self.classes_by_fq[fq] = cls
        self.classes_by_simple.setdefault(cls.class_name, []).append(cls)
        for method in cls.methods.values():
            self.methods_by_fq[method.fq_method] = method


def discover_python_files(project_root: Path) -> List[Path]:
    files: List[Path] = []
    for path in project_root.rglob("*.py"):
        # Skip common virtualenv and cache dirs
        parts = set(path.parts)
        if any(d in parts for d in {".venv", "venv", "__pycache__"}):
            continue
        files.append(path)
    return files


def path_to_module(project_root: Path, file_path: Path) -> str:
    rel = file_path.relative_to(project_root)
    no_suffix = rel.with_suffix("")
    parts = list(no_suffix.parts)
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def parse_module(file_path: Path) -> Optional[ast.AST]:
    try:
        source = file_path.read_text(encoding="utf-8", errors="ignore")
        return ast.parse(source, filename=str(file_path))
    except Exception:
        return None


def collect_imports(module_ast: ast.AST) -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    for node in ast.walk(module_ast):
        if isinstance(node, ast.ImportFrom):
            # from pkg.mod import Class as Alias
            module = node.module or ""
            for alias in node.names:
                name = alias.name
                asname = alias.asname or alias.name
                target = f"{module}.{name}" if module else name
                mapping[asname] = target
        elif isinstance(node, ast.Import):
            # import pkg.mod as alias
            for alias in node.names:
                name = alias.name
                asname = alias.asname or alias.name
                mapping[asname] = name
    return mapping


def collect_classes(module_ast: ast.AST, module: str, file_path: Path) -> List[ClassInfo]:
    classes: List[ClassInfo] = []
    for node in module_ast.body if isinstance(module_ast, ast.Module) else []:
        if isinstance(node, ast.ClassDef):
            class_name = node.name
            methods: Dict[str, MethodRef] = {}
            for body_item in node.body:
                if isinstance(body_item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    method_name = body_item.name
                    methods[method_name] = MethodRef(
                        module=module,
                        class_name=class_name,
                        method_name=method_name,
                        file_path=file_path,
                        line_number=getattr(body_item, "lineno", 1),
                    )
            classes.append(
                ClassInfo(
                    module=module,
                    class_name=class_name,
                    file_path=file_path,
                    line_number=getattr(node, "lineno", 1),
                    methods=methods,
                )
            )
    return classes


def build_index(project_root: Path) -> ProjectIndex:
    index = ProjectIndex()
    files = discover_python_files(project_root)
    for file_path in files:
        module_ast = parse_module(file_path)
        if module_ast is None:
            continue
        module = path_to_module(project_root, file_path)
        imports_map = collect_imports(module_ast)
        class_infos = collect_classes(module_ast, module, file_path)
        module_info = ModuleInfo(
            file_path=file_path,
            module=module,
            ast_root=module_ast,
            imports_name_to_target=imports_map,
            class_names_in_module={c.class_name for c in class_infos},
        )
        index.modules_by_file[file_path] = module_info
        for cls in class_infos:
            index.add_class(cls)
    return index


@dataclass
class CallSite:
    caller: MethodRef
    callee: MethodRef
    file_path: Path
    line_number: int


class SimpleDiGraph:
    """Minimal directed graph replacement when networkx is unavailable."""

    def __init__(self) -> None:
        self._nodes: Set[str] = set()
        self._edges: Set[Tuple[str, str]] = set()

    def add_node(self, node: str) -> None:
        self._nodes.add(node)

    def add_edge(self, u: str, v: str) -> None:
        self._nodes.add(u)
        self._nodes.add(v)
        self._edges.add((u, v))

    def nodes(self) -> Iterable[str]:
        return list(self._nodes)

    def number_of_nodes(self) -> int:
        return len(self._nodes)

    def number_of_edges(self) -> int:
        return len(self._edges)

    def edges(self) -> Iterable[Tuple[str, str]]:
        return list(self._edges)


class MethodCallResolver:
    def __init__(self, index: ProjectIndex):
        self.index = index

    def _infer_var_types(self, func_node: ast.AST, module_info: ModuleInfo, current_class: Optional[str]) -> Dict[str, Tuple[str, str]]:
        var_to_class: Dict[str, Tuple[str, str]] = {}

        class AssignVisitor(ast.NodeVisitor):
            def visit_Assign(self_inner, node: ast.Assign) -> None:  # type: ignore[override]
                try:
                    class_tuple = self._resolve_class_from_call(node.value, module_info)
                    if class_tuple is None:
                        return
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            var_to_class[target.id] = class_tuple
                finally:
                    self_inner.generic_visit(node)

            def visit_AnnAssign(self_inner, node: ast.AnnAssign) -> None:  # type: ignore[override]
                try:
                    class_tuple = self._resolve_class_from_call(node.value, module_info)
                    if class_tuple is None:
                        return
                    target = node.target
                    if isinstance(target, ast.Name):
                        var_to_class[target.id] = class_tuple
                finally:
                    self_inner.generic_visit(node)

        AssignVisitor().visit(func_node)
        return var_to_class

    def _resolve_class_from_call(self, value: Optional[ast.AST], module_info: ModuleInfo) -> Optional[Tuple[str, str]]:
        if not isinstance(value, ast.Call):
            return None
        callee = value.func
        # Name: ClassName(...)
        if isinstance(callee, ast.Name):
            name = callee.id
            if name in module_info.class_names_in_module:
                return module_info.module, name
            imported = module_info.imports_name_to_target.get(name)
            if imported:
                mod, cls = split_module_and_class(imported)
                if cls is not None:
                    return mod, cls
        # Attribute: module_alias.ClassName(...)
        if isinstance(callee, ast.Attribute) and isinstance(callee.value, ast.Name):
            mod_alias = callee.value.id
            cls = callee.attr
            imported = module_info.imports_name_to_target.get(mod_alias)
            if imported:
                # imported is full module path
                return imported, cls
        return None

    def _resolve_class_for_attribute(self, value: ast.AST, module_info: ModuleInfo, current_class: Optional[str], var_types: Dict[str, Tuple[str, str]]) -> Optional[Tuple[str, str]]:
        # self or cls => current class
        if isinstance(value, ast.Name) and value.id in {"self", "cls"} and current_class is not None:
            return module_info.module, current_class
        # Name: ClassName.method() or var.method()
        if isinstance(value, ast.Name):
            name = value.id
            if name in module_info.class_names_in_module:
                return module_info.module, name
            imported = module_info.imports_name_to_target.get(name)
            if imported:
                mod, cls = split_module_and_class(imported)
                if cls is not None:
                    return mod, cls
            if name in var_types:
                return var_types[name]
        # Attribute: module_alias.ClassName.method()
        if isinstance(value, ast.Attribute) and isinstance(value.value, ast.Name):
            mod_alias = value.value.id
            cls = value.attr
            imported = module_info.imports_name_to_target.get(mod_alias)
            if imported:
                return imported, cls
        return None

    def find_method_calls_in_method(self, method: MethodRef, module_info: ModuleInfo) -> List[Tuple[MethodRef, int]]:
        root = self.index.modules_by_file[method.file_path].ast_root
        class_node: Optional[ast.ClassDef] = None
        method_node: Optional[ast.AST] = None

        for node in root.body if isinstance(root, ast.Module) else []:
            if isinstance(node, ast.ClassDef) and node.name == method.class_name:
                class_node = node
                for body_item in node.body:
                    if isinstance(body_item, (ast.FunctionDef, ast.AsyncFunctionDef)) and body_item.name == method.method_name:
                        method_node = body_item
                        break
                break

        if method_node is None or class_node is None:
            return []

        var_types = self._infer_var_types(method_node, module_info, current_class=method.class_name)
        calls: List[Tuple[MethodRef, int]] = []

        class CallVisitor(ast.NodeVisitor):
            def visit_Call(self_inner, node: ast.Call) -> None:  # type: ignore[override]
                try:
                    func = node.func
                    if isinstance(func, ast.Attribute):
                        target_tuple = self._resolve_class_for_attribute(func.value, module_info, method.class_name, var_types)
                        if target_tuple is not None:
                            mod, cls = target_tuple
                            callee_method_name = func.attr
                            callee_ref = self._find_method_ref(mod, cls, callee_method_name)
                            if callee_ref is not None:
                                calls.append((callee_ref, getattr(node, "lineno", method.line_number)))
                finally:
                    self_inner.generic_visit(node)

        CallVisitor().visit(method_node)
        return calls

    def _find_method_ref(self, module: str, class_name: str, method_name: str) -> Optional[MethodRef]:
        fq_class = f"{module}:{class_name}"
        cls = self.index.classes_by_fq.get(fq_class)
        if cls is None:
            # try match by class name only if unique
            candidates = self.index.classes_by_simple.get(class_name, [])
            if len(candidates) == 1:
                cls = candidates[0]
        if cls is None:
            return None
        return cls.methods.get(method_name)


def split_module_and_class(qualified: str) -> Tuple[str, Optional[str]]:
    # "a.b.Class" -> ("a.b", "Class") or "Class" -> ("", "Class")
    parts = qualified.split(".")
    if len(parts) == 1:
        return "", parts[0]
    return ".".join(parts[:-1]), parts[-1]


def resolve_target(index: ProjectIndex, target_spec: str) -> Tuple[Optional[MethodRef], List[MethodRef]]:
    specified_module: Optional[str] = None
    class_name: Optional[str] = None
    method_name: Optional[str] = None

    if ":" in target_spec:
        module_part, rest = target_spec.split(":", 1)
        specified_module = module_part
        target_spec = rest
    if "." in target_spec:
        class_name, method_name = target_spec.split(".", 1)
    else:
        method_name = target_spec

    matches: List[MethodRef] = []
    if class_name and method_name:
        # search classes by name (and module if provided)
        for cls in index.classes_by_simple.get(class_name, []):
            if specified_module and cls.module != specified_module:
                continue
            if method_name in cls.methods:
                matches.append(cls.methods[method_name])
    elif method_name:
        # any method with that name
        for mref in index.methods_by_fq.values():
            if mref.method_name == method_name:
                if specified_module and mref.module != specified_module:
                    continue
                matches.append(mref)

    chosen: Optional[MethodRef] = None
    if matches:
        # choose deterministically: by file path then line
        matches.sort(key=lambda m: (str(m.file_path), m.line_number))
        chosen = matches[0]
    return chosen, matches


def build_call_graph(start: MethodRef, index: ProjectIndex, max_depth: int = 0):
    resolver = MethodCallResolver(index)
    graph = nx.DiGraph() if HAVE_NX else SimpleDiGraph()
    callsites: List[CallSite] = []

    visited: Set[str] = set()
    queue: List[Tuple[MethodRef, int]] = [(start, 0)]

    while queue:
        current, depth = queue.pop(0)
        if current.fq_method in visited:
            continue
        visited.add(current.fq_method)

        graph.add_node(current.fq_method)
        module_info = index.modules_by_file.get(current.file_path)
        if module_info is None:
            continue

        callees = resolver.find_method_calls_in_method(current, module_info)
        for callee, lineno in callees:
            graph.add_node(callee.fq_method)
            graph.add_edge(current.fq_method, callee.fq_method)
            callsites.append(CallSite(caller=current, callee=callee, file_path=current.file_path, line_number=lineno))
            next_depth = depth + 1
            if max_depth <= 0 or next_depth <= max_depth:
                queue.append((callee, next_depth))

    return graph, callsites


def find_all_usages(target: MethodRef, index: ProjectIndex) -> List[Tuple[Path, int, str]]:
    resolver = MethodCallResolver(index)
    occurrences: List[Tuple[Path, int, str]] = []

    for module_info in index.modules_by_file.values():
        # iterate through all methods in this module
        root = module_info.ast_root
        if not isinstance(root, ast.Module):
            continue

        for node in root.body:
            if isinstance(node, ast.ClassDef):
                class_name = node.name
                for body_item in node.body:
                    if isinstance(body_item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        # Build a temporary MethodRef for caller (for consistent resolution)
                        caller_ref = MethodRef(
                            module=module_info.module,
                            class_name=class_name,
                            method_name=body_item.name,
                            file_path=module_info.file_path,
                            line_number=getattr(body_item, "lineno", 1),
                        )
                        # Resolve calls in this method
                        calls = MethodCallResolver(index).find_method_calls_in_method(caller_ref, module_info)
                        for callee, lineno in calls:
                            if callee.fq_method == target.fq_method:
                                line_text = safe_get_line(module_info.file_path, lineno)
                                occurrences.append((module_info.file_path, lineno, line_text))
            # We ignore module-level functions for now to keep focus on methods

    # sort for stable output
    occurrences.sort(key=lambda t: (str(t[0]), t[1]))
    return occurrences


def safe_get_line(file_path: Path, lineno: int) -> str:
    try:
        with file_path.open("r", encoding="utf-8", errors="ignore") as f:
            for i, line in enumerate(f, start=1):
                if i == lineno:
                    return line.rstrip("\n")
    except Exception:
        pass
    return ""


def ensure_output_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_text_outputs(output_dir: Path, target: MethodRef, target_spec: str, usages: List[Tuple[Path, int, str]], graph, callsites: List[CallSite], all_matches: List[MethodRef], chosen_note: Optional[str]) -> Path:
    safe_target = target_spec.replace(":", "_").replace("/", "_").replace("\\", "_")
    out_path = output_dir / f"analysis_{safe_target}.txt"

    with out_path.open("w", encoding="utf-8") as f:
        f.write(f"Target: {target.fq_method}\n")
        if chosen_note:
            f.write(f"{chosen_note}\n")
        if len(all_matches) > 1:
            f.write("\nOther matches found for the target specification:\n")
            for m in all_matches:
                f.write(f"  - {m.fq_method} ({m.file_path}:{m.line_number})\n")

        f.write("\nUSAGES (who calls target):\n")
        if not usages:
            f.write("  No usages found.\n")
        else:
            for file_path, lineno, line in usages:
                f.write(f"  - {file_path}:{lineno}: {line}\n")

        f.write("\nCALL GRAPH EDGES (caller -> callee):\n")
        if not callsites:
            f.write("  No outgoing method calls found from the target (or depth limit = 0).\n")
        else:
            for cs in callsites:
                f.write(f"  - {cs.caller.fq_method} -> {cs.callee.fq_method} ({cs.file_path}:{cs.line_number})\n")

        f.write("\nNODES:\n")
        for node in sorted(graph.nodes()):
            f.write(f"  - {node}\n")

        f.write("\nSUMMARY:\n")
        f.write(f"  Nodes: {graph.number_of_nodes()}\n")
        f.write(f"  Edges: {graph.number_of_edges()}\n")

    return out_path


def render_graph_png(output_dir: Path, target: MethodRef, target_spec: str, graph) -> Path:
    safe_target = target_spec.replace(":", "_").replace("/", "_").replace("\\", "_")
    if HAVE_NX:
        png_path = output_dir / f"callgraph_{safe_target}.png"

        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(graph, seed=42, k=None)

        nodes = list(graph.nodes())
        node_colors = ["#ffcc00" if n == target.fq_method else "#9ec9ff" for n in nodes]

        nx.draw_networkx_nodes(graph, pos, node_color=node_colors, node_size=1200, alpha=0.9, linewidths=1.0, edgecolors="#333333")
        nx.draw_networkx_edges(graph, pos, arrows=True, arrowstyle="-|>", width=1.2, alpha=0.8)
        nx.draw_networkx_labels(graph, pos, font_size=8)

        plt.axis("off")
        plt.tight_layout()
        plt.savefig(png_path, dpi=180)
        plt.close()

        return png_path
    else:
        # Fallback: write Graphviz DOT file
        dot_path = output_dir / f"callgraph_{safe_target}.dot"
        with dot_path.open("w", encoding="utf-8") as f:
            f.write("digraph CallGraph {\n")
            f.write("  rankdir=LR;\n")
            for node in sorted(graph.nodes()):
                if node == target.fq_method:
                    f.write(f"  \"{node}\" [style=filled, fillcolor=gold];\n")
                else:
                    f.write(f"  \"{node}\";\n")
            # SimpleDiGraph has edges(); networkx also does, but we only reach here if HAVE_NX == False
            for u, v in getattr(graph, "edges")():
                f.write(f"  \"{u}\" -> \"{v}\";\n")
            f.write("}\n")
        return dot_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Find usages of a class method and build its call graph")
    parser.add_argument("--project-root", required=True, help="Path to the project root to analyze")
    parser.add_argument("--target", required=True, help="Method to analyze: 'Class.method', 'module:Class.method', or just 'method'")
    parser.add_argument("--output-dir", default="./analysis_output", help="Directory to write outputs")
    parser.add_argument("--max-depth", type=int, default=5, help="Max call graph depth from target (0 = unlimited)")

    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    output_dir = Path(args.output_dir).resolve()
    ensure_output_dir(output_dir)

    index = build_index(project_root)
    chosen, matches = resolve_target(index, args.target)
    if chosen is None:
        msg = (
            "Не удалось найти метод по спецификации. Попробуйте формат 'Class.method' или 'module.path:Class.method'."
        )
        raise SystemExit(msg)

    chosen_note: Optional[str] = None
    if len(matches) > 1:
        chosen_note = "ВНИМАНИЕ: найдено несколько совпадений, используется первое по алфавиту местоположения. Уточните --target через module:Class.method."

    usages = find_all_usages(chosen, index)
    graph, callsites = build_call_graph(chosen, index, max_depth=args.max_depth)

    txt_path = write_text_outputs(output_dir, chosen, args.target, usages, graph, callsites, matches, chosen_note)
    vis_path = render_graph_png(output_dir, chosen, args.target, graph)

    print(f"Text report: {txt_path}")
    if vis_path.suffix == ".png":
        print(f"Graph PNG:   {vis_path}")
    else:
        print(f"Graph DOT:   {vis_path}  (конвертируйте в PNG: dot -Tpng {vis_path} -o {vis_path.with_suffix('.png')})")


if __name__ == "__main__":
    main()