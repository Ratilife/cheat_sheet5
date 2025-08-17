"""
Анализатор вызовов методов

- Находит, где в проекте Python используется метод данного класса
- Строит график вызовов, отталкиваясь от этого метода (статический, эвристический)
- Сохраняет результаты в форматах .txt и .png (или .dot, если библиотеки рисования недоступны)

Использование:
  python3 method_call_analyzer.py \
    --project-root /path/to/project \
    --target "ClassName.method_name" \
    --output-dir ./analysis_output \
    --max-depth 5

Поддерживает целевые форматы:
- method
- ClassName.method
- module.path:ClassName.method

Ограничения:
- Эвристический статический анализ без полного вывода типа
- Динамическая диспетчеризация и метапрограммирование могут быть недоступны
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


def path_to_module(
                    project_root: Path,
                    file_path: Path
                  ) -> str:

    """Преобразует путь к файлу в Python-совместимое имя модуля.

    Конвертирует абсолютный путь к файлу в формат, пригодный для импорта,
    учитывая структуру пакетов Python. Особенности:
    - Удаляет расширение .py
    - Обрабатывает __init__.py как корень пакета
    - Преобразует разделители путей в точки

    Args:
        project_root: Корневая директория проекта (базовый путь)
        file_path: Абсолютный путь к файлу для конвертации

    Returns:
        str: Имя модуля в формате 'package.submodule'

    Raises:
        ValueError: Если file_path не находится внутри project_root

    Example:
        >>> path_to_module(Path('/project'), Path('/project/pkg/mod.py'))
        'pkg.mod'
        >>> path_to_module(Path('/project'), Path('/project/pkg/__init__.py'))
        'pkg'
    """
    # Получаем относительный путь от корня проекта
    rel = file_path.relative_to(project_root)

    # Удаляем расширение .py (или .pyi) из имени файла
    no_suffix = rel.with_suffix("")

    # Разбиваем путь на компоненты (папки и имя файла)
    parts = list(no_suffix.parts)

    # Специальная обработка __init__.py - удаляем последний компонент
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]

    # Собираем итоговое имя модуля через точки
    return ".".join(parts)


def parse_module(file_path: Path) -> Optional[ast.AST]:
    """Парсит Python-файл в абстрактное синтаксическое дерево (AST).

    Читает и анализирует содержимое Python-файла, преобразуя его в AST.
    В случае ошибок чтения или синтаксических ошибок возвращает None.

    Args:
        file_path: Путь к файлу для парсинга. Должен существовать и быть читаемым.

    Returns:
        Optional[ast.AST]: Корень AST-дерева или None при ошибке.
        Возвращаемое AST может быть:
        - ast.Module для обычных модулей
        - ast.Interactive для интерактивного кода
        - ast.Expression для одиночных выражений

    Note:
        - Использует UTF-8 кодировку с игнорированием ошибок декодирования
        - Подавляет все исключения, возвращая None в любом случае ошибки
        - Имя файла сохраняется в AST для корректных сообщений об ошибках
    """
    try:
        # Чтение содержимого файла с обработкой:
        # - Кодировка UTF-8 (стандарт для Python)
        # - Игнорирование ошибок декодирования (errors="ignore")
        source = file_path.read_text(encoding="utf-8", errors="ignore")

        # Парсинг исходного кода в AST:
        # - source: содержимое файла
        # - filename: имя файла для сообщений об ошибках
        return ast.parse(source, filename=str(file_path))

    except Exception:
        # Обработка всех возможных исключений:
        # - IOError (невозможно прочитать файл)
        # - SyntaxError (ошибки в коде)
        # - MemoryError (большой файл)
        # - Другие непредвиденные ошибки
        return None


def collect_imports(module_ast: ast.AST) -> Dict[str, str]:
    """Собирает информацию об импортах из AST модуля.

    Анализирует дерево AST и извлекает все импорты, создавая словарь
    соответствия между именами в текущем модуле и полными путями импортируемых объектов.

    Args:
        module_ast: AST-дерево модуля (результат ast.parse)

    Returns:
        Dict[str, str]: Словарь вида:
            - Ключ: имя, под которым объект доступен в модуле (алиас или оригинальное имя)
            - Значение: полный путь импортируемого объекта

    Examples:
        Для 'from package.submodule import Class as Alias' вернет {'Alias': 'package.submodule.Class'}
        Для 'import module as mod' вернет {'mod': 'module'}
    """
    # Инициализация словаря для хранения результатов
    mapping: Dict[str, str] = {}

    # Рекурсивный обход всех узлов AST
    for node in ast.walk(module_ast):
        # Обработка from ... import ... конструкций
        if isinstance(node, ast.ImportFrom):
            # Получаем имя модуля (может быть None для относительных импортов)
            module = node.module or ""

            # Обрабатываем все импортируемые объекты в конструкции
            for alias in node.names:
                # Оригинальное имя импортируемого объекта
                name = alias.name
                # Алиас (если есть) или оригинальное имя
                asname = alias.asname or alias.name
                # Формируем полный путь к объекту
                target = f"{module}.{name}" if module else name
                # Сохраняем в словарь
                mapping[asname] = target

        # Обработка простых import конструкций
        elif isinstance(node, ast.Import):
            # Обрабатываем все импорты в конструкции
            for alias in node.names:
                # Полное имя импортируемого модуля
                name = alias.name
                # Алиас (если есть) или оригинальное имя
                asname = alias.asname or alias.name
                # Сохраняем в словарь
                mapping[asname] = name

    return mapping

def discover_python_files(project_root: Path) -> List[Path]:
    """Находит все Python-файлы в проекте, исключая служебные директории.
        Рекурсивно обходит директорию проекта, собирая все файлы с расширением .py.
        Автоматически пропускает виртуальные окружения и кэш-директории Python.
        Args:
            project_root: Путь к корневой директории проекта для сканирования
        Returns:
            List[Path]: Список путей к найденным Python-файлам (относительно project_root)
                       Список отсортирован в алфавитном порядке (гарантировано rglob)
        Example:
            >>> discover_python_files(Path("/project"))
            [Path("/project/main.py"), Path("/project/utils/helpers.py")]
    """
    # Инициализируем пустой список для результатов
    files: List[Path] = []
    # Рекурсивно ищем все .py файлы в проекте (включая поддиректории)
    for path in project_root.rglob("*.py"):
        # Преобразуем путь в множество компонентов для быстрого поиска
        parts = set(path.parts)
        # Пропускаем файлы в виртуальных окружениях и кэше Python:
        # - .venv - стандартное имя виртуального окружения
        # - venv  - альтернативное имя виртуального окружения
        # - __pycache__ - директория с байткодом Python
        if any(d in parts for d in {".venv", "venv", "__pycache__"}):
            continue
        # Добавляем корректный файл в результирующий список
        files.append(path)
    # Возвращаем список найденных файлов (автоматически сортированный rglob)
    return files


def collect_classes(module_ast: ast.AST, module: str, file_path: Path) -> List[ClassInfo]:
    """Собирает информацию о классах и их методах из AST модуля.

        Анализирует AST-дерево модуля, извлекая все классы и их методы,
        и создает структурированную информацию о них.

        Args:
            module_ast: AST-дерево модуля (результат ast.parse)
            module: Имя текущего модуля (через точки, например 'package.submodule')
            file_path: Путь к файлу модуля

        Returns:
            List[ClassInfo]: Список объектов ClassInfo, содержащих:
                - Имя класса и модуля
                - Расположение в исходном коде
                - Словарь методов класса

        Raises:
            AttributeError: Если передан неверный тип AST-узла
    """
    # Инициализация списка для хранения информации о классах
    classes: List[ClassInfo] = []

    # Обход тела модуля (если это действительно модуль)
    for node in module_ast.body if isinstance(module_ast, ast.Module) else []:
        # Обрабатываем только узлы определения классов
        if isinstance(node, ast.ClassDef):
            # Получаем имя класса
            class_name = node.name

            # Словарь для хранения информации о методах класса
            methods: Dict[str, MethodRef] = {}

            # Обходим все элементы тела класса
            for body_item in node.body:
                # Нас интересуют только функции (обычные и асинхронные)
                if isinstance(body_item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    method_name = body_item.name

                    # Создаем объект MethodRef для каждого метода
                    methods[method_name] = MethodRef(
                        module=module,  # Имя текущего модуля
                        class_name=class_name,  # Имя содержащего класса
                        method_name=method_name,  # Имя метода
                        file_path=file_path,  # Путь к файлу
                        line_number=getattr(body_item, "lineno", 1),  # Номер строки или 1 по умолчанию
                    )

            # Создаем объект ClassInfo для текущего класса
            classes.append(
                ClassInfo(
                    module=module,  # Имя модуля
                    class_name=class_name,  # Имя класса
                    file_path=file_path,  # Путь к файлу
                    line_number=getattr(node, "lineno", 1),  # Номер строки определения класса
                    methods=methods,  # Словарь методов класса
                )
            )

    return classes

def build_index(project_root: Path) -> ProjectIndex:

    """Строит индекс всех классов и методов в Python-проекте.

        Анализирует структуру проекта, собирая информацию о:
        - Модулях и их AST-представлении
        - Импортах в каждом модуле
        - Классах и их методах
        - Связях между классами через импорты
        Args:
            project_root: Путь к корневой директории проекта
        Returns:
            ProjectIndex: Объект индекса со всей собранной информацией о проекте
        Raises:
            ValueError: Если project_root не является допустимым путем к директории
    """

    # Создаем пустой индекс проекта
    index = ProjectIndex()
    # Находим все Python-файлы в проекте (исключая виртуальные окружения)
    files = discover_python_files(project_root)
    # Обрабатываем каждый найденный файл
    for file_path in files:
        # Парсим файл в AST-дерево
        module_ast = parse_module(file_path)
        # Пропускаем файл если не удалось распарсить
        if module_ast is None:
            continue
        # Преобразуем путь к файлу в имя модуля (например: package.submodule)
        module = path_to_module(project_root, file_path)
        # Собираем информацию об импортах в модуле
        imports_map = collect_imports(module_ast)
        # Извлекаем все классы и их методы из AST
        class_infos = collect_classes(module_ast, module, file_path)
        # Создаем объект с информацией о модуле
        module_info = ModuleInfo(
            file_path=file_path,
            module=module,
            ast_root=module_ast,
            imports_name_to_target=imports_map,                        # Словарь импортов
            class_names_in_module={c.class_name for c in class_infos}, # Имена классов
        )
        # Добавляем информацию о модуле в индекс
        index.modules_by_file[file_path] = module_info
        # Добавляем все найденные классы в индекс
        for cls in class_infos:
            index.add_class(cls)
    # Возвращаем заполненный индекс проекта
    return index

def resolve_target(
                    index: ProjectIndex,
                    target_spec: str
                  ) -> Tuple[Optional[MethodRef], List[MethodRef]]:

    """Разрешает строковую спецификацию метода в конкретные объекты MethodRef.

        Поддерживает несколько форматов спецификации:
        - "module.path:ClassName.method" - полное квалифицированное имя
        - "ClassName.method" - поиск по имени класса и метода
        - "method" - поиск метода по имени без привязки к классу

        Args:
            index: Индекс проекта с информацией о классах и методах
            target_spec: Строковая спецификация целевого метода

        Returns:
            Tuple: (выбранный MethodRef, список всех подходящих MethodRef)
            - первый элемент может быть None если совпадений нет
            - второй элемент содержит все найденные совпадения
    """

    # Инициализация переменных для хранения компонентов спецификации
    specified_module: Optional[str] = None
    class_name: Optional[str] = None
    method_name: Optional[str] = None

    # Разбираем спецификацию на составляющие:
    # Обрабатываем часть с модулем (если есть разделитель ":")
    if ":" in target_spec:
        module_part, rest = target_spec.split(":", 1)
        specified_module = module_part
        target_spec = rest
    # Обрабатываем часть с классом и методом (если есть разделитель ".")
    if "." in target_spec:
        class_name, method_name = target_spec.split(".", 1)
    else:
        method_name = target_spec

    # Список для хранения всех подходящих методов
    matches: List[MethodRef] = []
    # Поиск по имени класса и метода
    if class_name and method_name:
        # Ищем в классах с указанным именем
        # search classes by name (and module if provided)
        for cls in index.classes_by_simple.get(class_name, []):
            # Проверяем совпадение модуля если он был указан
            if specified_module and cls.module != specified_module:
                continue
            # Если метод существует в классе - добавляем в результаты
            if method_name in cls.methods:
                matches.append(cls.methods[method_name])
    # Поиск только по имени метода (если не указан класс)
    elif method_name:
        # Проверяем все методы в проекте
        for mref in index.methods_by_fq.values():
            if mref.method_name == method_name:
                # Проверяем совпадение модуля если он был указан
                if specified_module and mref.module != specified_module:
                    continue
                matches.append(mref)
    # Выбор основного результата из найденных совпадений
    chosen: Optional[MethodRef] = None
    if matches:
        # Сортируем для детерминированного выбора: сначала по пути файла, затем по номеру строки
        matches.sort(key=lambda m: (str(m.file_path), m.line_number))
        # Берем первый элемент (наименьший в отсортированном списке)
        chosen = matches[0]
    return chosen, matches

def build_call_graph(
                        start: MethodRef,
                        index: ProjectIndex,
                        max_depth: int = 0
                    ):
    """Строит граф вызовов методов, начиная с указанного метода.

        Использует алгоритм обхода в ширину (BFS) для построения графа вызовов.
        Поддерживает ограничение глубины поиска и работает как с networkx, так и с упрощенным графом.

        Args:
            start: Начальный метод для построения графа
            index: Индекс проекта с информацией о модулях и классах
            max_depth: Максимальная глубина рекурсии (0 - без ограничений)

        Returns:
            tuple: (граф вызовов, список всех точек вызовов)
                  - граф: nx.DiGraph или SimpleDiGraph
                  - callsites: список объектов CallSite с информацией о вызовах
    """

    # Инициализируем резолвер для поиска вызовов методов
    resolver = MethodCallResolver(index)
    # Создаем граф (используем networkx если доступен, иначе упрощенную реализацию)
    graph = nx.DiGraph() if HAVE_NX else SimpleDiGraph()
    # Список для хранения информации о точках вызовов
    callsites: List[CallSite] = []

    # Множество для отслеживания посещенных методов
    visited: Set[str] = set()
    # Очередь для BFS: хранит пары (метод, текущая глубина)
    queue: List[Tuple[MethodRef, int]] = [(start, 0)]
    # Основной цикл обхода в ширину
    while queue:
        # Извлекаем текущий метод и глубину из очереди
        current, depth = queue.pop(0)
        # Пропускаем уже посещенные методы
        if current.fq_method in visited:
            continue
        # Помечаем метод как посещенный
        visited.add(current.fq_method)
        # Добавляем узел в граф
        graph.add_node(current.fq_method)
        # Получаем информацию о модуле текущего метода
        module_info = index.modules_by_file.get(current.file_path)
        if module_info is None:
            continue
        # Находим все методы, вызываемые из текущего метода
        callees = resolver.find_method_calls_in_method(current, module_info)
        # Обрабатываем каждый найденный вызов
        for callee, lineno in callees:
            # Добавляем узел вызываемого метода
            graph.add_node(callee.fq_method)
            # Добавляем ребро между методами
            graph.add_edge(current.fq_method, callee.fq_method)
            # Сохраняем информацию о точке вызова
            callsites.append(CallSite(
                                        caller=current,
                                        callee=callee,
                                        file_path=current.file_path,
                                        line_number=lineno))
            # Вычисляем следующую глубину
            next_depth = depth + 1

            # Добавляем в очередь если не достигли максимальной глубины
            if max_depth <= 0 or next_depth <= max_depth:
                queue.append((callee, next_depth))

    return graph, callsites

def find_all_usages(
                        target: MethodRef,
                        index: ProjectIndex
                    ) -> List[Tuple[Path, int, str]]:

    """Находит все использования целевого метода в проекте.

        Анализирует все классы проекта, собирая места вызовов указанного метода.
        Возвращает список найденных использований с указанием файла, номера строки
        и содержимого строки кода.

        Args:
            target: Ссылка на целевой метод, чьи использования нужно найти
            index: Индекс проекта с информацией о модулях и классах

        Returns:
            List[Tuple[Path, int, str]]: Список кортежей (путь_к_файлу, номер_строки, текст_строки),
            отсортированный по имени файла и номеру строки
    """

    # Инициализируем резолвер для поиска вызовов методов
    resolver = MethodCallResolver(index)
    # Список для хранения найденных использований
    occurrences: List[Tuple[Path, int, str]] = []

    # Обходим все модули проекта
    for module_info in index.modules_by_file.values():
        # Получаем AST корня модуля
        # выполнить итерацию по всем методам в этом модуле
        root = module_info.ast_root
        # Пропускаем если это не AST модуля (на всякий случай)
        if not isinstance(root, ast.Module):
            continue
        # Анализируем все узлы в теле модуля
        for node in root.body:
            # Нас интересуют только классы (пока игнорируем функции уровня модуля)
            if isinstance(node, ast.ClassDef):
                class_name = node.name
                # Обходим все элементы тела класса
                for body_item in node.body:
                    # Ищем только методы класса (обычные и асинхронные)
                    if isinstance(body_item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        # Создаем временную ссылку на метод-вызыватель для единообразного разрешения
                        # Создайте временный метод Ref для вызывающего объекта (для согласованного разрешения)
                        caller_ref = MethodRef(
                            module=module_info.module,
                            class_name=class_name,
                            method_name=body_item.name,
                            file_path=module_info.file_path,
                            line_number=getattr(body_item, "lineno", 1),
                        )
                        # Находим все вызовы методов из текущего метода
                        calls = MethodCallResolver(index).find_method_calls_in_method(caller_ref, module_info)
                        # Фильтруем вызовы, оставляя только обращения к целевому методу
                        for callee, lineno in calls:
                            if callee.fq_method == target.fq_method:
                                # Получаем текст строки с вызовом
                                line_text = safe_get_line(module_info.file_path, lineno)
                                occurrences.append((module_info.file_path, lineno, line_text))
            # We ignore module-level functions for now to keep focus on methods

    # sort for stable output
    occurrences.sort(key=lambda t: (str(t[0]), t[1]))
    return occurrences
def ensure_output_dir(path: Path) -> None:
    """Создает директорию для выходных файлов, если она не существует.
        Гарантирует, что указанная директория будет доступна для записи результатов анализа.
        Автоматически создает все недостающие родительские директории при необходимости.
        Args:
            path: Путь к директории, которую необходимо создать/проверить
        Returns:
            None: Метод не возвращает значения, только выполняет побочное действие
        Raises:
            OSError: В случае ошибок создания директории (например, недостаток прав)
    """
    # Создаем директорию со следующими параметрами:
    # - parents=True: создает все недостающие родительские директории
    # - exist_ok=True: не вызывает ошибку, если директория уже существует
    path.mkdir(parents=True, exist_ok=True)

def write_text_outputs(
                        output_dir: Path,
                        target: MethodRef,
                        target_spec: str,
                        usages: List[Tuple[Path, int, str]],
                        graph, callsites: List[CallSite],
                        all_matches: List[MethodRef],
                        chosen_note: Optional[str]
                      ) -> Path:

    """Создает текстовый отчет с анализом вызовов метода в формате .txt.

        Отчет включает:
            - Информацию о целевом методе
            - Альтернативные совпадения (если есть)
            - Места использования (кто вызывает целевой метод)
            - Ребра графа вызовов (исходящие вызовы из целевого метода)
            - Список всех узлов графа
            - Статистику по количеству узлов и ребер
        Args:
            output_dir: Директория для сохранения отчета
            target: Исходный целевой метод анализа
            target_spec: Строка-спецификация метода (для имени файла)
            usages: Список мест вызова целевого метода
            graph: Граф вызовов (nx.DiGraph или SimpleDiGraph)
            callsites: Список всех найденных вызовов между методами
            all_matches: Все методы, соответствующие target_spec
            chosen_note: Примечание о выборе цели (если было несколько совпадений)

        Returns:
            Path: Путь к созданному текстовому файлу
    """
    # Формируем безопасное имя файла, заменяя спецсимволы
    safe_target = target_spec.replace(":", "_").replace("/", "_").replace("\\", "_")
    # Создаем полный путь к файлу отчета
    out_path = output_dir / f"analysis_{safe_target}.txt"
    # Открываем файл на запись с UTF-8 кодировкой
    with out_path.open("w", encoding="utf-8") as f:
        # Записываем заголовок с полным именем целевого метода
        f.write(f"Target (Цель): {target.fq_method}\n")

        # Добавляем примечание, если было несколько совпадений
        if chosen_note:
            f.write(f"{chosen_note}\n")
        # Если найдены альтернативные совпадения - выводим их список
        if len(all_matches) > 1:
            f.write("\nНайдены другие совпадения с целевой спецификацией:\n")
            for m in all_matches:
                f.write(f"  - {m.fq_method} ({m.file_path}:{m.line_number})\n")

        # Раздел с местами использования целевого метода
        f.write("\nUSAGES (кто называет цель):\n")
        if not usages:
            f.write("  Не найдено никаких вариантов использования.\n")
        else:
            # Для каждого места использования выводим файл, строку и код
            for file_path, lineno, line in usages:
                f.write(f"  - {file_path}:{lineno}: {line}\n")
        # Раздел с ребрами графа (исходящие вызовы из целевого метода)
        f.write("\nCALL GRAPH EDGES (вызывающий абонент -> вызываемый абонент):\n")
        if not callsites:
            f.write("  Не найдено исходящих вызовов методов из целевого объекта (или ограничение глубины = 0).\n")
        else:
            # Для каждого вызова выводим связь между методами и местоположение
            for cs in callsites:
                f.write(f"  - {cs.caller.fq_method} -> {cs.callee.fq_method} ({cs.file_path}:{cs.line_number})\n")
        # Раздел со списком всех узлов графа
        f.write("\nNODES:\n")
        for node in sorted(graph.nodes()):
            f.write(f"  - {node}\n")
        # Заключительная статистика
        f.write("\nSUMMARY:\n")
        f.write(f"  Nodes (Узлы): {graph.number_of_nodes()}\n")
        f.write(f"  Edges (Края): {graph.number_of_edges()}\n")

    return out_path

def render_graph_png(output_dir: Path, target: MethodRef, target_spec: str, graph) -> Path:
    """Создает визуализацию графа вызовов в формате PNG или DOT (если networkx недоступен).

        Генерирует графическое представление графа вызовов, где:
        - Целевой метод выделяется желтым цветом
        - Остальные узлы отображаются синим цветом
        - При отсутствии networkx создает DOT-файл для ручной конвертации

        Args:
            output_dir: Директория для сохранения результатов
            target: Целевой метод, который будет выделен на графе
            target_spec: Строка спецификации метода (используется для имени файла)
            graph: Граф вызовов (nx.DiGraph или SimpleDiGraph)

        Returns:
            Path: Путь к созданному файлу (PNG или DOT)
    """
    # Создаем безопасное имя файла, заменяя спецсимволы
    safe_target = target_spec.replace(":", "_").replace("/", "_").replace("\\", "_")
    # Если networkx доступен, создаем PNG
    if HAVE_NX:
        # Формируем путь для PNG-файла
        png_path = output_dir / f"callgraph_{safe_target}.png"
        # Создаем фигуру с заданным размером
        plt.figure(figsize=(12, 8))
        # Вычисляем позиции узлов с фиксированным seed для воспроизводимости
        pos = nx.spring_layout(graph, seed=42, k=None)
        # Получаем список всех узлов
        nodes = list(graph.nodes())
        # Задаем цвета узлов: желтый для целевого метода, синий для остальных
        node_colors = ["#ffcc00" if n == target.fq_method else "#9ec9ff" for n in nodes]

        # Рисуем узлы графа с заданными параметрами
        nx.draw_networkx_nodes(graph, pos, node_color=node_colors, node_size=1200, alpha=0.9, linewidths=1.0, edgecolors="#333333")
        # Рисуем ребра графа с стрелками
        nx.draw_networkx_edges(graph, pos, arrows=True, arrowstyle="-|>", width=1.2, alpha=0.8)
        # Добавляем подписи узлов
        nx.draw_networkx_labels(graph, pos, font_size=8)

        # Отключаем оси координат
        plt.axis("off")
        # Оптимизируем расположение элементов
        plt.tight_layout()
        # Сохраняем график в файл с высоким DPI
        plt.savefig(png_path, dpi=180)
        # Закрываем фигуру для освобождения памяти
        plt.close()

        return png_path
    else:
        # Если networkx недоступен, создаем DOT-файл
        dot_path = output_dir / f"callgraph_{safe_target}.dot"
        with dot_path.open("w", encoding="utf-8") as f:
            # Записываем заголовок DOT-файла
            f.write("digraph CallGraph {\n")
            # Устанавливаем горизонтальную ориентацию графа
            f.write("  rankdir=LR;\n")
            # Добавляем узлы, выделяя целевой метод цветом
            for node in sorted(graph.nodes()):
                if node == target.fq_method:
                    f.write(f"  \"{node}\" [style=filled, fillcolor=gold];\n")
                else:
                    f.write(f"  \"{node}\";\n")
            # Добавляем все ребра графа
            # SimpleDiGraph имеет edges(); сеть тоже работает, но мы подключаемся только сюда if HAVE_NX == False
            for u, v in getattr(graph, "edges")():
                f.write(f"  \"{u}\" -> \"{v}\";\n")
            f.write("}\n")
        return dot_path

def main() -> None:
    parser = argparse.ArgumentParser(description="Найдите способы использования метода класса и постройте график его вызовов")
    parser.add_argument("--project-root", required=True, help="Путь к корневому каталогу проекта для анализа")
    parser.add_argument("--target", required=True, help="Метод анализа: 'Class.method', 'module:Class.method', или просто 'method'")
    parser.add_argument("--output-dir", default="./analysis_output", help="Каталог для записи выходных данных")
    parser.add_argument("--max-depth", type=int, default=5, help="Максимальная глубина графика вызовов от цели (0 = неограниченно)")

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