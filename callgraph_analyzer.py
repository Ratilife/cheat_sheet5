#!/usr/bin/env python3
"""
Call graph and usage analyzer (per-module) for Python projects.

- Scans all .py files under a root directory (excluding common dirs)
- Builds intra-module call graphs (functions and class methods)
- Detects where methods are used within the same module
- Writes a TXT report and PNG diagrams (one per module)

Usage:
  python callgraph_analyzer.py --root /path/to/project --out ./report

Optional:
  --exclude venv .venv __pycache__ build dist
  --max-depth 12
  --png-layout spring|kamada_kawai|shell

No system Graphviz dependency; uses networkx + matplotlib (Agg backend).
"""
from __future__ import annotations

import argparse
import ast
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Iterable

# Ensure matplotlib does not require a display
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx


# ---------- Data models ----------

@dataclass
class FunctionInfo:
    qualified_name: str  # e.g., func, Class.method, outer.inner
    lineno: int
    col_offset: int
    is_method: bool = False
    class_name: Optional[str] = None


@dataclass
class ImportBinding:
    module: Optional[str]  # e.g., pkg.mod for "from pkg import mod" or "import pkg" → module=pkg
    name: Optional[str]    # imported symbol, None for plain module import
    alias: Optional[str]   # local alias name in this module


@dataclass
class ModuleInfo:
    module_name: str
    file_path: Path
    tree: ast.AST
    functions: Dict[str, FunctionInfo] = field(default_factory=dict)  # qualname -> info
    # Calls made by a given function (qualname) to other qualnames in the same module
    intra_calls: Dict[str, Set[str]] = field(default_factory=dict)
    # Reverse index: callee -> set(callers)
    intra_called_by: Dict[str, Set[str]] = field(default_factory=dict)
    # Imports seen in module: alias/name -> ImportBinding
    imports: Dict[str, ImportBinding] = field(default_factory=dict)
    # Names found in __all__ (considered exported)
    exports: Set[str] = field(default_factory=set)
    # Name usages
    used_local_names: Set[str] = field(default_factory=set)
    used_import_aliases: Set[str] = field(default_factory=set)
    used_foreign_defs: Set[str] = field(default_factory=set)
    used_foreign_attrs: Set[str] = field(default_factory=set)


# ---------- Utilities ----------

EXCLUDE_DEFAULT = {".git", "__pycache__", ".venv", "venv", "build", "dist", ".mypy_cache", ".pytest_cache"}


def discover_python_files(root: Path, excludes: Set[str]) -> List[Path]:
    python_files: List[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        # In-place prune excluded directories
        dirnames[:] = [d for d in dirnames if d not in excludes and not d.startswith('.')]
        for filename in filenames:
            if filename.endswith('.py'):
                python_files.append(Path(dirpath) / filename)
    return python_files


def module_name_from_path(root: Path, file_path: Path) -> str:
    try:
        rel = file_path.relative_to(root)
    except Exception:
        rel = file_path.name
    if isinstance(rel, Path):
        parts = list(rel.parts)
    else:
        parts = [str(rel)]
    if parts and parts[-1].endswith('.py'):
        parts[-1] = parts[-1][:-3]
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(p for p in parts if p)


# ---------- First pass: collect definitions and imports ----------

class _ModuleCollector(ast.NodeVisitor):
    def __init__(self, module: ModuleInfo) -> None:
        self.module = module
        self.current_class_stack: List[str] = []
        super().__init__()

    # Definitions
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # type: ignore[override]
        self._add_function_like(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:  # type: ignore[override]
        self._add_function_like(node)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:  # type: ignore[override]
        self.current_class_stack.append(node.name)
        self.generic_visit(node)
        self.current_class_stack.pop()

    # __all__ exports
    def visit_Assign(self, node: ast.Assign) -> None:  # type: ignore[override]
        targets = node.targets
        if any(isinstance(t, ast.Name) and t.id == "__all__" for t in targets):
            names = set()
            lit = node.value
            if isinstance(lit, (ast.List, ast.Tuple, ast.Set)):
                for elt in lit.elts:
                    if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                        names.add(elt.value)
            self.module.exports |= names
        self.generic_visit(node)

    # Imports
    def visit_Import(self, node: ast.Import) -> None:  # type: ignore[override]
        for alias in node.names:
            asname = alias.asname or alias.name
            binding = ImportBinding(module=alias.name, name=None, alias=asname)
            self.module.imports[asname] = binding
        # no generic_visit; import has no children we care about

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:  # type: ignore[override]
        if node.module is None:
            return
        for alias in node.names:
            if alias.name == '*':
                continue
            asname = alias.asname or alias.name
            binding = ImportBinding(module=node.module, name=alias.name, alias=asname)
            self.module.imports[asname] = binding
        # no generic_visit

    def _add_function_like(self, node: ast.AST) -> None:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            is_method = len(self.current_class_stack) > 0
            qualname = node.name
            class_name: Optional[str] = None
            if is_method:
                class_name = ".".join(self.current_class_stack)
                qualname = f"{class_name}.{node.name}"
            info = FunctionInfo(
                qualified_name=qualname,
                lineno=node.lineno,
                col_offset=node.col_offset,
                is_method=is_method,
                class_name=class_name,
            )
            self.module.functions[qualname] = info
            # ensure presence in call maps
            self.module.intra_calls.setdefault(qualname, set())
            self.module.intra_called_by.setdefault(qualname, set())


# ---------- Second pass: collect usages and calls ----------

class _UsageCollector(ast.NodeVisitor):
    def __init__(self, module: ModuleInfo):
        self.module = module
        # Track current function/method qualified name while visiting
        self.current_function_stack: List[str] = []
        # Simple symbol table to track local assignments to function names (limited)
        self.local_aliases_stack: List[Dict[str, str]] = []
        super().__init__()

    # Function scopes
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # type: ignore[override]
        self._enter_function(node)
        self.generic_visit(node)
        self._exit_function()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:  # type: ignore[override]
        self._enter_function(node)
        self.generic_visit(node)
        self._exit_function()

    def visit_ClassDef(self, node: ast.ClassDef) -> None:  # type: ignore[override]
        self.generic_visit(node)

    # Name and attribute usage
    def visit_Name(self, node: ast.Name) -> None:  # type: ignore[override]
        if node.id in self.module.functions:
            self.module.used_local_names.add(node.id)
        if node.id in self.module.imports:
            self.module.used_import_aliases.add(node.id)
        # Aliases to function names inside current function
        if self.local_aliases_stack:
            alias_map = self.local_aliases_stack[-1]
            if node.id in alias_map:
                self._add_call_edge_from_current(alias_map[node.id])
        # Proceed
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:  # type: ignore[override]
        # Collect foreign attribute uses like pkg.symbol or self.method
        base_name = None
        if isinstance(node.value, ast.Name):
            base_name = node.value.id
        if base_name and base_name in self.module.imports:
            self.module.used_foreign_attrs.add(f"{base_name}.{node.attr}")
        # Detect self.method() within a class method
        # The call addition happens in visit_Call; here we just walk
        self.generic_visit(node)

    # Track simple assignments to alias functions within a function body
    def visit_Assign(self, node: ast.Assign) -> None:  # type: ignore[override]
        try:
            if self.local_aliases_stack and isinstance(node.value, ast.Name):
                callee = self._resolve_name_to_qualname(node.value.id)
                if callee:
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            self.local_aliases_stack[-1][target.id] = callee
        finally:
            self.generic_visit(node)

    # Calls
    def visit_Call(self, node: ast.Call) -> None:  # type: ignore[override]
        callee_qual = self._resolve_call_qualname(node.func)
        if callee_qual:
            self._add_call_edge_from_current(callee_qual)
        self.generic_visit(node)

    # Helpers
    def _enter_function(self, node: ast.AST) -> None:
        qualname = None
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            qualname = node.name
        # Walk up to see if within a class
        parent_class = self._get_enclosing_class_name(node)
        if parent_class:
            qualname = f"{parent_class}.{qualname}"
        if qualname is None:
            qualname = "<unknown>"
        self.current_function_stack.append(qualname)
        self.local_aliases_stack.append({})
        # Ensure function exists in registry (in case of odd constructs)
        self.module.intra_calls.setdefault(qualname, set())
        self.module.intra_called_by.setdefault(qualname, set())

    def _exit_function(self) -> None:
        self.current_function_stack.pop()
        self.local_aliases_stack.pop()

    def _get_enclosing_class_name(self, node: ast.AST) -> Optional[str]:
        # Walk parent links would help; since ast doesn't provide them, we heuristically
        # reconstruct from function name present in module.functions
        # We rely on pre-collected functions list
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # first try as a method
            for fn in self.module.functions.values():
                if fn.lineno == node.lineno and fn.col_offset == node.col_offset and fn.is_method:
                    return fn.class_name
        return None

    def _add_call_edge_from_current(self, callee_qual: str) -> None:
        if not self.current_function_stack:
            return
        caller = self.current_function_stack[-1]
        # Restrict to intra-module calls
        if callee_qual in self.module.functions:
            self.module.intra_calls.setdefault(caller, set()).add(callee_qual)
            self.module.intra_called_by.setdefault(callee_qual, set()).add(caller)

    def _resolve_call_qualname(self, func: ast.AST) -> Optional[str]:
        # Resolve different call node types to a function qualified name
        # Case: direct name f()
        if isinstance(func, ast.Name):
            # local alias first
            if self.local_aliases_stack and func.id in self.local_aliases_stack[-1]:
                return self.local_aliases_stack[-1][func.id]
            return self._resolve_name_to_qualname(func.id)
        # Case: attribute like obj.method()
        if isinstance(func, ast.Attribute):
            # self.method() inside a method → Class.method
            if isinstance(func.value, ast.Name) and func.value.id == 'self':
                # Find current class context
                current = self.current_function_stack[-1] if self.current_function_stack else None
                if current and '.' in current:
                    class_name = current.split('.')[0]
                    candidate = f"{class_name}.{func.attr}"
                    if candidate in self.module.functions:
                        return candidate
            # ClassName.method() static/clsmethod like
            if isinstance(func.value, ast.Name):
                class_name = func.value.id
                candidate = f"{class_name}.{func.attr}"
                if candidate in self.module.functions:
                    return candidate
            # pkg.symbol() via import alias → foreign, ignore as intra
            if isinstance(func.value, ast.Name) and func.value.id in self.module.imports:
                self.module.used_foreign_attrs.add(f"{func.value.id}.{func.attr}")
                return None
        return None

    def _resolve_name_to_qualname(self, name: str) -> Optional[str]:
        # Prefer exact function/method names in module scope first
        if name in self.module.functions:
            return name
        # Could be an unqualified function referenced inside a method; already covered by exact
        # Could be an imported alias
        if name in self.module.imports:
            return None
        return None


# ---------- Report generation ----------

def render_tree_lines(roots: List[str], edges: Dict[str, Set[str]], max_depth: int = 20) -> List[str]:
    lines: List[str] = []

    def dfs(node: str, prefix: str, visited: Set[str], depth: int) -> None:
        if depth > max_depth:
            lines.append(f"{prefix}… (depth limit)")
            return
        children = sorted(list(edges.get(node, set())))
        for idx, child in enumerate(children):
            connector = "└─>" if idx == len(children) - 1 else "├─>"
            lines.append(f"{prefix}{connector} {child}()")
            if child in visited:
                lines.append(f"{prefix}    ↩ (cycle to {child})")
                continue
            visited.add(child)
            new_prefix = f"{prefix}    " if idx == len(children) - 1 else f"{prefix}│   "
            dfs(child, new_prefix, visited, depth + 1)
            visited.remove(child)

    for root in sorted(roots):
        lines.append(f"{root}()")
        dfs(root, "    ", {root}, 1)
        lines.append("")
    return lines


def choose_roots(module: ModuleInfo) -> List[str]:
    # Roots = functions/methods that are not called by any other function in the same module
    candidates = set(module.functions.keys())
    called = set(module.intra_called_by.keys())
    called_nonempty = {k for k, v in module.intra_called_by.items() if v}
    roots = sorted(list(candidates - called_nonempty))
    if not roots:
        return sorted(list(candidates))
    return roots


def build_text_report(modules: List[ModuleInfo], max_depth: int) -> str:
    out_lines: List[str] = []
    out_lines.append("Project Callgraph Report (intra-module)\n")
    for mod in sorted(modules, key=lambda m: m.module_name):
        out_lines.append(mod.module_name or "<module>")
        out_lines.append("")
        roots = choose_roots(mod)
        tree = render_tree_lines(roots, mod.intra_calls, max_depth=max_depth)
        out_lines.extend([f"  {line}" if line else "" for line in tree])
        # Method usage summary
        method_callers: List[Tuple[str, List[str]]] = []
        for qual, info in mod.functions.items():
            if info.is_method:
                callers = sorted(list(mod.intra_called_by.get(qual, set())))
                method_callers.append((qual, callers))
        if method_callers:
            out_lines.append("  Method usages:")
            for qual, callers in sorted(method_callers):
                if callers:
                    out_lines.append(f"    - {qual}() ⇐ used by: {', '.join(callees_with_parens(callers))}")
                else:
                    out_lines.append(f"    - {qual}() ⇐ used by: <none>")
        out_lines.append("\n")
    return "\n".join(out_lines)


def callees_with_parens(names: Iterable[str]) -> List[str]:
    return [f"{n}()" for n in names]


# ---------- PNG rendering ----------

def draw_module_graph(module: ModuleInfo, out_path: Path, layout: str = "spring") -> None:
    G = nx.DiGraph()
    for qual in module.functions.keys():
        G.add_node(qual, is_method=module.functions[qual].is_method)
    for caller, callees in module.intra_calls.items():
        for callee in callees:
            G.add_edge(caller, callee)

    if len(G) == 0:
        return

    plt.figure(figsize=(max(8, len(G) * 0.6), max(6, len(G) * 0.5)))
    if layout == "spring":
        pos = nx.spring_layout(G, seed=42)
    elif layout == "kamada_kawai":
        pos = nx.kamada_kawai_layout(G)
    elif layout == "shell":
        pos = nx.shell_layout(G)
    else:
        pos = nx.spring_layout(G, seed=42)

    node_colors = ["tab:orange" if G.nodes[n].get("is_method") else "tab:blue" for n in G.nodes]
    nx.draw_networkx_nodes(G, pos, node_size=800, node_color=node_colors, edgecolors="black")
    nx.draw_networkx_labels(G, pos, font_size=8)
    nx.draw_networkx_edges(G, pos, arrows=True, arrowstyle="-|>", arrowsize=12, width=1.2)
    plt.axis("off")
    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=200)
    plt.close()


# ---------- Orchestrator ----------

def analyze_project(root: Path, out_dir: Path, excludes: Set[str], max_depth: int, png_layout: str) -> Tuple[List[ModuleInfo], Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    py_files = discover_python_files(root, excludes)

    modules: List[ModuleInfo] = []
    # First pass: parse and collect definitions/imports
    for path in py_files:
        try:
            src = path.read_text(encoding="utf-8", errors="ignore")
        except Exception as exc:
            print(f"[warn] Cannot read {path}: {exc}", file=sys.stderr)
            continue
        try:
            tree = ast.parse(src, filename=str(path))
        except SyntaxError as exc:
            print(f"[warn] SyntaxError in {path}: {exc}", file=sys.stderr)
            continue
        module_name = module_name_from_path(root, path)
        mod = ModuleInfo(module_name=module_name, file_path=path, tree=tree)
        _ModuleCollector(mod).visit(tree)
        modules.append(mod)

    # Second pass: usages and calls (intra)
    for mod in modules:
        _UsageCollector(mod).visit(mod.tree)

    # Report
    text_report = build_text_report(modules, max_depth)
    txt_path = out_dir / "callgraph_report.txt"
    txt_path.write_text(text_report, encoding="utf-8")

    # PNGs per module
    png_root = out_dir / "png"
    for mod in modules:
        safe_name = mod.module_name.replace("/", "_").replace("\\", "_").replace(".", "_") or "module"
        png_path = png_root / f"{safe_name}.png"
        draw_module_graph(mod, png_path, layout=png_layout)

    return modules, txt_path, png_root


# ---------- CLI ----------

def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Intra-module call graph and usage analyzer")
    p.add_argument("--root", type=str, default=str(Path.cwd()), help="Root directory to scan")
    p.add_argument("--out", type=str, default=str(Path.cwd() / Path("callgraph_report")), help="Output directory for reports")
    p.add_argument("--exclude", nargs="*", default=list(EXCLUDE_DEFAULT), help="Directory names to exclude")
    p.add_argument("--max-depth", type=int, default=20, help="Max depth for call tree in TXT report")
    p.add_argument("--png-layout", type=str, choices=["spring", "kamada_kawai", "shell"], default="spring", help="Layout algorithm for PNG diagrams")
    return p.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    root = Path(args.root).resolve()
    out_dir = Path(args.out).resolve()
    excludes = set(args.exclude) | EXCLUDE_DEFAULT

    print(f"[info] Scanning root: {root}")
    print(f"[info] Excludes: {sorted(excludes)}")
    print(f"[info] Output: {out_dir}")

    modules, txt_path, png_root = analyze_project(root, out_dir, excludes, args.max_depth, args.png_layout)
    print(f"[info] Analyzed modules: {len(modules)}")
    print(f"[info] Wrote TXT: {txt_path}")
    print(f"[info] Wrote PNGs to: {png_root}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())