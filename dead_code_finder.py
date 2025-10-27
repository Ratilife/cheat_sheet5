#!/usr/bin/env python3

import argparse
import ast
import datetime as dt
import fnmatch
import os
import re
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple


# ----------------------------- Data Structures ----------------------------- #

@dataclass(frozen=True)
class Symbol:
    name: str
    module: str
    file_path: str
    line: int
    kind: str  # 'function' | 'class' | 'variable' | 'method'


@dataclass(frozen=True)
class ImportBinding:
    alias: str
    type: str  # 'import' | 'from'
    module: Optional[str]  # for 'import': full module path; for 'from': source module
    name: Optional[str]  # for 'from': imported object name; else None
    level: int  # relative import level for 'from'
    line: int


@dataclass(frozen=True)
class Unreachable:
    file_path: str
    module: str
    function: str
    line: int
    reason: str


@dataclass(frozen=True)
class SyntaxIssue:
    file_path: str
    line: int
    col: int
    message: str


class ModuleInfo:
    def __init__(self, module_name: str, file_path: str, tree: ast.AST) -> None:
        self.module_name: str = module_name
        self.file_path: str = file_path
        self.tree: ast.AST = tree
        self.definitions: Dict[str, Symbol] = {}
        self.imports: Dict[str, ImportBinding] = {}
        self.used_aliases: Set[str] = set()
        self.all_exports: Set[str] = set()
        self.unreachable: List[Unreachable] = []


# ----------------------------- Analyzer Core ------------------------------ #

class ProjectAnalyzer:
    def __init__(
        self,
        root_path: str,
        exclude_patterns: List[str],
        ignore_names_regex: Optional[str],
        ignore_private: bool,
        include_methods: bool,
        max_file_size_kb: int,
    ) -> None:
        self.root_path: str = os.path.abspath(root_path)
        self.exclude_patterns: List[str] = list(set(exclude_patterns))
        self.ignore_names_regex: str = ignore_names_regex or r"^__.*__$"
        if ignore_private:
            # ignore dunders and private names starting with underscore
            self.ignore_names_regex = rf"(?:{self.ignore_names_regex})|^_.*"
        self.ignore_names_re = re.compile(self.ignore_names_regex)
        self.include_methods: bool = include_methods
        self.max_file_size_bytes: int = max_file_size_kb * 1024 if max_file_size_kb > 0 else 0

        self.python_files: List[str] = []
        self.module_to_file: Dict[str, str] = {}
        self.file_to_module: Dict[str, str] = {}

        self.modules: Dict[str, ModuleInfo] = {}
        self.syntax_issues: List[SyntaxIssue] = []

        # Used across project (module, name)
        self.used_definitions: Set[Tuple[str, str]] = set()

    # ----------------------------- Discovery ----------------------------- #

    def collect_python_files(self) -> None:
        for dirpath, dirnames, filenames in os.walk(self.root_path):
            rel_dir = os.path.relpath(dirpath, self.root_path)
            # Normalize rel path for root
            if rel_dir == ".":
                rel_dir = ""

            # Apply directory excludes in-place to prune walk
            pruned_dirnames: List[str] = []
            for d in list(dirnames):
                rel_sub = os.path.normpath(os.path.join(rel_dir, d))
                if self._is_excluded(rel_sub):
                    continue
                pruned_dirnames.append(d)
            dirnames[:] = pruned_dirnames

            for filename in filenames:
                if not filename.endswith(".py"):
                    continue
                rel_file = os.path.normpath(os.path.join(rel_dir, filename)) if rel_dir else filename
                if self._is_excluded(rel_file):
                    continue
                abs_file = os.path.join(self.root_path, rel_file)
                if self.max_file_size_bytes:
                    try:
                        if os.path.getsize(abs_file) > self.max_file_size_bytes:
                            continue
                    except OSError:
                        continue
                self.python_files.append(abs_file)

        # Build module mapping
        for file_path in self.python_files:
            module_name = self._module_name_from_path(file_path)
            self.module_to_file[module_name] = file_path
            self.file_to_module[file_path] = module_name

    def _is_excluded(self, rel_path: str) -> bool:
        # Rel path uses OS sep; compare against patterns via fnmatch and substring of parts
        if not rel_path:
            return False
        lowered = rel_path.lower()
        parts = lowered.split(os.sep)
        for pat in self.exclude_patterns:
            pat_lower = pat.lower()
            # direct glob match against rel path
            if fnmatch.fnmatch(lowered, pat_lower):
                return True
            # or if any path part equals pattern
            if pat_lower in parts:
                return True
            # or substring match to catch cases like "site-packages"
            if pat_lower in lowered:
                return True
        return False

    def _module_name_from_path(self, file_path: str) -> str:
        rel = os.path.relpath(file_path, self.root_path)
        rel = rel.replace(os.sep, ".")
        if rel.endswith(".py"):
            rel = rel[:-3]
        if rel.endswith(".__init__"):
            rel = rel[: -len(".__init__")]
        # Remove leading dots that may appear if root is file's parent
        return rel.lstrip(".")

    # ----------------------------- Parsing Pass -------------------------- #

    def first_pass_collect(self) -> None:
        for file_path in self.python_files:
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    source = f.read()
            except OSError as e:
                self.syntax_issues.append(
                    SyntaxIssue(file_path=file_path, line=0, col=0, message=f"IOError: {e}")
                )
                continue

            try:
                tree = ast.parse(source, filename=file_path)
            except SyntaxError as e:
                self.syntax_issues.append(
                    SyntaxIssue(
                        file_path=file_path,
                        line=getattr(e, "lineno", 0) or 0,
                        col=getattr(e, "offset", 0) or 0,
                        message=f"SyntaxError: {e.msg}",
                    )
                )
                continue

            module_name = self.file_to_module[file_path]
            minfo = ModuleInfo(module_name, file_path, tree)

            # Traverse to collect defs, imports, __all__, and basic unreachable
            collector = _ModuleCollector(
                module_name=module_name,
                file_path=file_path,
                include_methods=self.include_methods,
                ignore_name_re=self.ignore_names_re,
            )
            collector.visit(tree)

            minfo.definitions = collector.definitions
            minfo.imports = collector.imports
            minfo.all_exports = collector.all_exports
            minfo.unreachable = collector.unreachable

            self.modules[module_name] = minfo

    # ----------------------------- Usage Pass ---------------------------- #

    def second_pass_usage(self) -> None:
        for module_name, minfo in self.modules.items():
            usage = _UsageCollector(
                current_module=module_name,
                module_to_file=self.module_to_file,
                modules=self.modules,
            )
            usage.visit(minfo.tree)

            # mark used local definitions
            for name in usage.used_local_names:
                self.used_definitions.add((module_name, name))

            # mark used import aliases
            minfo.used_aliases = usage.used_import_aliases.copy()

            # For used imported objects via "from X import y"
            for (src_module, name) in usage.used_foreign_defs:
                self.used_definitions.add((src_module, name))

            # For used attributes accessed via imported modules: `import a; a.foo`
            for (src_module, name) in usage.used_foreign_attrs:
                self.used_definitions.add((src_module, name))

            # Treat names listed in __all__ as used
            for name in minfo.all_exports:
                # mark definition in this module as used
                self.used_definitions.add((module_name, name))
                # also treat import alias as used if re-exported via __all__
                if name in minfo.imports:
                    minfo.used_aliases.add(name)

    # ----------------------------- Report -------------------------------- #

    def compile_report(self) -> str:
        unused_imports: List[Tuple[str, int, str]] = []  # (file, line, alias)
        unused_functions: List[Symbol] = []
        unused_classes: List[Symbol] = []
        unused_variables: List[Symbol] = []
        unreachable: List[Unreachable] = []

        for module_name, minfo in sorted(self.modules.items()):
            # imports
            for alias, binding in minfo.imports.items():
                if alias not in minfo.used_aliases:
                    unused_imports.append((minfo.file_path, binding.line, alias))

            # defs
            for name, sym in minfo.definitions.items():
                if self.ignore_names_re.search(name):
                    continue
                if (sym.module, sym.name) not in self.used_definitions:
                    if sym.kind == "function":
                        unused_functions.append(sym)
                    elif sym.kind == "class":
                        unused_classes.append(sym)
                    elif sym.kind == "variable":
                        unused_variables.append(sym)
                    elif sym.kind == "method":
                        unused_functions.append(sym)  # methods reported under functions if enabled

            # unreachable
            unreachable.extend(minfo.unreachable)

        # syntax issues
        syntax_issues_sorted = sorted(self.syntax_issues, key=lambda s: (s.file_path, s.line, s.col))

        now = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        header = [
            f"Dead Code Report",
            f"Generated: {now}",
            f"Root: {self.root_path}",
            f"Exclude patterns: {', '.join(self.exclude_patterns) if self.exclude_patterns else '(none)'}",
            f"Ignore names regex: {self.ignore_names_regex}",
            "",
        ]

        sections: List[str] = []

        def format_list(title: str, items: List[str]) -> None:
            sections.append(title)
            if not items:
                sections.append("  (none)")
            else:
                sections.extend(items)
            sections.append("")

        # Summary counts
        summary_lines = [
            f"Total files scanned: {len(self.modules)}",
            f"Unused imports: {len(unused_imports)}",
            f"Unused functions/methods: {len(unused_functions)}",
            f"Unused classes: {len(unused_classes)}",
            f"Unused module variables: {len(unused_variables)}",
            f"Unreachable code locations: {len(unreachable)}",
            f"Syntax issues: {len(syntax_issues_sorted)}",
            "",
        ]

        # Detail sections
        format_list(
            "Unused imports (file:line alias)",
            [f"  {file}:{line} {alias}" for (file, line, alias) in sorted(unused_imports)],
        )

        format_list(
            "Unused functions/methods (file:line name)",
            [f"  {s.file_path}:{s.line} {s.name}" for s in sorted(unused_functions, key=lambda x: (x.file_path, x.line, x.name))],
        )

        format_list(
            "Unused classes (file:line name)",
            [f"  {s.file_path}:{s.line} {s.name}" for s in sorted(unused_classes, key=lambda x: (x.file_path, x.line, x.name))],
        )

        format_list(
            "Unused module variables (file:line name)",
            [f"  {s.file_path}:{s.line} {s.name}" for s in sorted(unused_variables, key=lambda x: (x.file_path, x.line, x.name))],
        )

        format_list(
            "Unreachable code (file:line function reason)",
            [f"  {u.file_path}:{u.line} {u.function} {u.reason}" for u in sorted(unreachable, key=lambda x: (x.file_path, x.line, x.function))],
        )

        format_list(
            "Syntax issues (file:line:col message)",
            [f"  {s.file_path}:{s.line}:{s.col} {s.message}" for s in syntax_issues_sorted],
        )

        return "\n".join(header + summary_lines + sections)

    def write_report(self, output_path: str, report_text: str) -> None:
        out_dir = os.path.dirname(os.path.abspath(output_path))
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report_text)

    # ----------------------------- Runner -------------------------------- #

    def run(self, output_path: str) -> None:
        self.collect_python_files()
        self.first_pass_collect()
        self.second_pass_usage()
        report = self.compile_report()
        self.write_report(output_path, report)


# ----------------------------- AST Visitors ------------------------------- #

class _ModuleCollector(ast.NodeVisitor):
    def __init__(
        self,
        module_name: str,
        file_path: str,
        include_methods: bool,
        ignore_name_re: re.Pattern,
    ) -> None:
        self.module_name = module_name
        self.file_path = file_path
        self.include_methods = include_methods
        self.ignore_name_re = ignore_name_re

        self.definitions: Dict[str, Symbol] = {}
        self.imports: Dict[str, ImportBinding] = {}
        self.all_exports: Set[str] = set()
        self.unreachable: List[Unreachable] = []

        self._class_stack: List[str] = []
        self._function_stack: List[str] = []

    # ---- Helpers ---- #

    def _add_definition(self, name: str, node: ast.AST, kind: str) -> None:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            line = node.lineno
        else:
            line = getattr(node, "lineno", 1)
        self.definitions.setdefault(
            name,
            Symbol(name=name, module=self.module_name, file_path=self.file_path, line=line, kind=kind),
        )

    def _collect_all_exports(self, node: ast.Assign) -> None:
        # Handle __all__ = ["a", "b"] or tuple
        try:
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    names = _extract_str_names(node.value)
                    for n in names:
                        if n:
                            self.all_exports.add(n)
        except Exception:
            pass

    # ---- Visitors ---- #

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        if not self._function_stack and not self._class_stack:
            # module-level class
            if not self.ignore_name_re.search(node.name):
                self._add_definition(node.name, node, "class")
        # Push class to allow tracking methods if enabled
        self._class_stack.append(node.name)
        self.generic_visit(node)
        self._class_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_function_like(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_function_like(node)

    def _visit_function_like(self, node: ast.AST) -> None:
        name = getattr(node, "name", "<anonymous>")
        is_method = bool(self._class_stack)
        if not self._function_stack and not is_method:
            # module-level function
            if not self.ignore_name_re.search(name):
                self._add_definition(name, node, "function")
        elif is_method and self.include_methods:
            if not self.ignore_name_re.search(name):
                self._add_definition(name, node, "method")

        # Unreachable code (simple): after return/raise/break/continue in top-level of function body
        self._function_stack.append(name)
        self._collect_unreachable_in_function(node)
        self.generic_visit(node)
        self._function_stack.pop()

    def _collect_unreachable_in_function(self, node: ast.AST) -> None:
        body: List[ast.stmt] = getattr(node, "body", [])
        reachable = True
        for i, stmt in enumerate(body):
            if not reachable:
                self.unreachable.append(
                    Unreachable(
                        file_path=self.file_path,
                        module=self.module_name,
                        function=self._function_stack[-1] if self._function_stack else "<module>",
                        line=getattr(stmt, "lineno", 1),
                        reason="after return/raise/break/continue",
                    )
                )
                continue
            if isinstance(stmt, (ast.Return, ast.Raise, ast.Continue, ast.Break)):
                reachable = False

    def visit_Assign(self, node: ast.Assign) -> None:
        # __all__
        self._collect_all_exports(node)
        if self._function_stack:
            return
        # module-level variable names
        for target in node.targets:
            for name in _names_from_target(target):
                if not self.ignore_name_re.search(name):
                    self._add_definition(name, node, "variable")
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if self._function_stack or self._class_stack:
            return
        target = node.target
        for name in _names_from_target(target):
            if not self.ignore_name_re.search(name):
                self._add_definition(name, node, "variable")
        self.generic_visit(node)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        if self._function_stack:
            return
        for name in _names_from_target(node.target):
            if not self.ignore_name_re.search(name):
                self._add_definition(name, node, "variable")
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        # import pkg.sub as alias -> alias or pkg
        for alias in node.names:
            alias_name = alias.asname or alias.name.split(".")[0]
            binding = ImportBinding(
                alias=alias_name,
                type="import",
                module=alias.name,
                name=None,
                level=0,
                line=node.lineno,
            )
            self.imports[alias_name] = binding

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        for alias in node.names:
            # Ignore star imports for unused-import reporting; they pollute namespace
            if alias.name == '*':
                continue
            alias_name = alias.asname or alias.name
            binding = ImportBinding(
                alias=alias_name,
                type="from",
                module=node.module,
                name=alias.name,
                level=node.level or 0,
                line=node.lineno,
            )
            self.imports[alias_name] = binding


class _UsageCollector(ast.NodeVisitor):
    def __init__(
        self,
        current_module: str,
        module_to_file: Dict[str, str],
        modules: Dict[str, ModuleInfo],
    ) -> None:
        self.current_module = current_module
        self.module_to_file = module_to_file
        self.modules = modules

        self.used_local_names: Set[str] = set()
        self.used_import_aliases: Set[str] = set()
        self.used_foreign_defs: Set[Tuple[str, str]] = set()  # (module, name) from `from x import name`
        self.used_foreign_attrs: Set[Tuple[str, str]] = set()  # (module, attr) from `import x; x.attr`

    # Helpers

    def _get_current_module_info(self) -> ModuleInfo:
        return self.modules[self.current_module]

    def _resolve_from_module(self, binding: ImportBinding) -> Optional[str]:
        # Resolve relative imports to absolute module path where possible
        if binding.type != "from":
            return None
        src_module = binding.module or ""
        level = binding.level
        if level == 0:
            return src_module or None
        # Compute base package of current module
        parts = self.current_module.split(".")
        # remove the last part (the module name) to get package
        if parts:
            parts = parts[:-1]
        ascend = max(0, level - 1)
        if ascend > 0:
            parts = parts[: max(0, len(parts) - ascend)]
        if src_module:
            parts += src_module.split(".")
        resolved = ".".join([p for p in parts if p])
        return resolved or None

    def visit_Name(self, node: ast.Name) -> None:
        if not isinstance(node.ctx, ast.Load):
            return
        name = node.id
        minfo = self._get_current_module_info()

        # local definitions
        if name in minfo.definitions:
            self.used_local_names.add(name)
            return

        # imported aliases
        if name in minfo.imports:
            self.used_import_aliases.add(name)
            binding = minfo.imports[name]
            # `from X import y` -> mark y in X as used if X is part of project
            if binding.type == "from" and binding.name:
                resolved_mod = self._resolve_from_module(binding)
                if resolved_mod and resolved_mod in self.module_to_file:
                    # Check if definition exists in that module
                    target_modinfo = self.modules.get(resolved_mod)
                    if target_modinfo and binding.name in target_modinfo.definitions:
                        self.used_foreign_defs.add((resolved_mod, binding.name))

    def visit_Attribute(self, node: ast.Attribute) -> None:
        # Handle `import a; a.foo` where `a` is an imported module within project
        value = node.value
        if isinstance(value, ast.Name):
            alias = value.id
            minfo = self._get_current_module_info()
            if alias in minfo.imports:
                binding = minfo.imports[alias]
                if binding.type == "import" and binding.module:
                    src_module = binding.module
                    # If imported module is within project, and has a definition with this attr, mark used
                    if src_module in self.module_to_file:
                        target_modinfo = self.modules.get(src_module)
                        if target_modinfo and node.attr in target_modinfo.definitions:
                            self.used_foreign_attrs.add((src_module, node.attr))
                elif binding.type == "from":
                    # Accessing attribute off imported object; we cannot reliably resolve
                    pass
        self.generic_visit(node)


# ----------------------------- Utilities --------------------------------- #

def _names_from_target(target: ast.AST) -> List[str]:
    names: List[str] = []
    if isinstance(target, ast.Name):
        names.append(target.id)
    elif isinstance(target, (ast.Tuple, ast.List)):
        for elt in target.elts:
            names.extend(_names_from_target(elt))
    # ignore attributes and subscripts at module level for simplicity
    return names


def _extract_str_names(node: ast.AST) -> List[str]:
    # Extract list of string constants from list/tuple/const expressions
    names: List[str] = []
    try:
        if isinstance(node, (ast.List, ast.Tuple)):
            for elt in node.elts:
                names.extend(_extract_str_names(elt))
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            names.append(node.value)
        elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            # concatenate lists or strings
            left = _extract_str_names(node.left)
            right = _extract_str_names(node.right)
            names.extend(left + right)
    except Exception:
        pass
    return names


# ----------------------------- CLI --------------------------------------- #

def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Scan a Python project for potentially dead code: unused imports,"
            " module-level functions, classes, variables, and simple unreachable code."
        )
    )
    parser.add_argument(
        "--root",
        default=os.getcwd(),
        help="Root directory of the project to scan (default: current working directory)",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to .txt report file to write",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[
            ".git",
            "__pycache__",
            ".venv",
            "venv",
            "build",
            "dist",
            ".mypy_cache",
            ".pytest_cache",
        ],
        help=(
            "Glob or path fragments to exclude (can be passed multiple times)."
            " Defaults include common virtualenv and cache folders."
        ),
    )
    parser.add_argument(
        "--ignore-names",
        default=r"^__.*__$",
        help=(
            "Regex for names to ignore in dead-code reporting (default: dunder names)."
            " You can combine with --ignore-private to also ignore names starting with _"
        ),
    )
    parser.add_argument(
        "--ignore-private",
        action="store_true",
        help="Also ignore names starting with underscore (_)",
    )
    parser.add_argument(
        "--include-methods",
        action="store_true",
        help="Include class methods in the unused-function check (may produce false positives)",
    )
    parser.add_argument(
        "--max-file-size-kb",
        type=int,
        default=0,
        help="Skip .py files larger than this size in KB (0 = no limit)",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)

    analyzer = ProjectAnalyzer(
        root_path=args.root,
        exclude_patterns=args.exclude or [],
        ignore_names_regex=args.ignore_names,
        ignore_private=args.ignore_private,
        include_methods=args.include_methods,
        max_file_size_kb=args.max_file_size_kb,
    )

    try:
        analyzer.run(output_path=args.output)
    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        return 2

    print(f"Report written to: {os.path.abspath(args.output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())