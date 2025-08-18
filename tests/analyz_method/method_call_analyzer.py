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

@dataclass(frozen=True)  # Делает класс неизменяемым (immutable) и автоматически генерирует методы __init__, __repr__ и др.
class MethodRef:
    """Класс-контейнер для хранения информации о методе класса.

    Содержит полную идентификационную информацию о методе:
    - Модуль, в котором находится метод
    - Класс, которому принадлежит метод
    - Имя самого метода
    - Местоположение в исходном коде

    Атрибуты:
        module (str): Имя модуля (через точки, например 'package.submodule')
        class_name (str): Имя класса, содержащего метод
        method_name (str): Имя метода
        file_path (Path): Полный путь к файлу с исходным кодом
        line_number (int): Номер строки с определением метода

    Свойства:
        fq_method: Полное квалифицированное имя метода
        fq_class: Полное квалифицированное имя класса

    Note:
        Класс является неизменяемым (frozen=True) для безопасности в многопоточной среде
        и использования в качестве ключа словаря.
    """
    module: str           # Имя модуля (формат с точками)
    class_name: str       # Имя содержащего класса
    method_name: str      # Имя метода
    file_path: Path       # Абсолютный путь к файлу
    line_number: int      # Номер строки определения метода

    @property
    def fq_method(self) -> str:
        """Возвращает полное квалифицированное имя метода.

        Формат: 'модуль:класс.метод'
        Пример: 'utils.helpers:RequestParser.validate'

        Returns:
            str: Строка в формате 'module:class.method'
        """
        return f"{self.module}:{self.class_name}.{self.method_name}"

    @property
    def fq_class(self) -> str:
        """Возвращает полное квалифицированное имя класса.

        Формат: 'модуль:класс'
        Пример: 'utils.helpers:RequestParser'

        Returns:
            str: Строка в формате 'module:class'
        """
        return f"{self.module}:{self.class_name}"

@dataclass  # Декоратор для автоматической генерации базовых методов класса
class ClassInfo:
    """Класс для хранения метаинформации о классе в проекте.

    Содержит полные данные о расположении и структуре класса:
    - Модуль, в котором объявлен класс
    - Список методов класса
    - Физическое расположение в исходном коде

    Attributes:
        module (str): Имя модуля в формате package.submodule
        class_name (str): Имя класса
        file_path (Path): Абсолютный путь к файлу с исходным кодом
        line_number (int): Номер строки с объявлением класса
        methods (Dict[str, MethodRef]): Словарь методов класса:
            - Ключ: имя метода
            - Значение: объект MethodRef с деталями метода

    Note:
        Иммутабельный класс (frozen=False по умолчанию) - поля можно изменять.
        Для использования в множествах или как ключа словаря добавьте @dataclass(frozen=True).
    """
    module: str           # [1] Имя модуля через точки (например 'utils.helpers')
    class_name: str       # [2] Лексическое имя класса (как в исходном коде)
    file_path: Path       # [3] Полный путь к файлу (например PosixPath('/project/utils.py'))
    line_number: int      # [4] Номер строки с ключевым словом 'class'
    methods: Dict[str, MethodRef]  # [5] Словарь методов:
                                   #     - 'method_name' → MethodRef
                                   #     - Где MethodRef содержит детали реализации

@dataclass  # Автоматически генерирует методы __init__, __repr__ и другие
class ModuleInfo:
    """Контейнер для хранения метаинформации о Python-модуле.

    Содержит полную структурную информацию о модуле:
    - Физическое расположение файла
    - AST-дерево для анализа кода
    - Таблицу импортов
    - Множество имен классов в модуле

    Attributes:
        file_path: Абсолютный путь к файлу модуля
        module: Имя модуля в формате package.submodule
        ast_root: Корневой узел AST-дерева модуля
        imports_name_to_target: Соответствие импортов (что -> откуда импортировано)
        class_names_in_module: Множество имен классов, определенных в модуле

    Note:
        Для анализа динамически создаваемых классов необходимо расширять функционал.
    """
    file_path: Path
    # [1] Абсолютный путь к .py файлу
    # Пример: PosixPath('/project/src/utils/helpers.py')

    module: str
    # [2] Полное имя модуля через точки (как для импорта)
    # Пример: 'utils.helpers' для файла helpers.py в папке utils

    ast_root: ast.AST
    # [3] Корневой узел AST (обычно ast.Module)
    # Содержит полное синтаксическое дерево модуля для анализа

    imports_name_to_target: Dict[str, str]
    # [4] Словарь импортов вида {'alias': 'real.import.path'}
    # Пример: {'np': 'numpy', 'pd': 'pandas'}
    # Где:
    #   ключ - имя, используемое в коде
    #   значение - полный путь импорта

    class_names_in_module: Set[str]
    # [5] Множество имен классов, определенных в этом модуле
    # Пример: {'User', 'Database'}
    # Используется для быстрой проверки принадлежности класса модулю


class ProjectIndex:
    """Индекс проекта для хранения и быстрого поиска метаинформации о классах и методах.

    Служит централизованным хранилищем данных о структуре проекта:
    - Индексирует классы и методы по различным критериям
    - Обеспечивает быстрый доступ к данным через словари
    - Поддерживает два вида поиска классов: по полному имени и простому

    Attributes:
        classes_by_fq (Dict[str, ClassInfo]): Классы по полному имени (модуль:класс)
        classes_by_simple (Dict[str, List[ClassInfo]]): Классы по короткому имени (с дубликатами)
        methods_by_fq (Dict[str, MethodRef]): Методы по полному имени (модуль:класс.метод)
        modules_by_file (Dict[Path, ModuleInfo]): Модули по пути к файлу
    """

    def __init__(self) -> None:
        """Инициализирует пустой индекс проекта."""
        # Классы с ключом в формате "модуль:класс" (без дубликатов)
        self.classes_by_fq: Dict[str, ClassInfo] = {}

        # Классы сгруппированы по короткому имени (может быть несколько классов с одним именем)
        self.classes_by_simple: Dict[str, List[ClassInfo]] = {}

        # Все методы проекта с ключом в формате "модуль:класс.метод"
        self.methods_by_fq: Dict[str, MethodRef] = {}

        # Модули с ключом по абсолютному пути к файлу
        self.modules_by_file: Dict[Path, ModuleInfo] = {}

    def add_class(self, cls: ClassInfo) -> None:
        """Добавляет класс и его методы в индекс проекта.

        Args:
            cls (ClassInfo): Объект с информацией о классе

        Note:
            Обновляет все связанные словари:
            - classes_by_fq
            - classes_by_simple
            - methods_by_fq
        """
        # Формируем полное имя класса в формате "модуль:класс"
        fq = f"{cls.module}:{cls.class_name}"

        # Добавляем в словарь классов с полным именем
        self.classes_by_fq[fq] = cls

        # Добавляем в словарь классов с коротким именем
        # setdefault создает список при первом обращении, если ключа нет
        self.classes_by_simple.setdefault(cls.class_name, []).append(cls)

        # Индексируем все методы класса
        for method in cls.methods.values():
            # Используем полное имя метода в формате "модуль:класс.метод"
            self.methods_by_fq[method.fq_method] = method

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


@dataclass  # Автоматически генерирует методы __init__, __repr__, __eq__ и другие
class CallSite:
    """Контейнер для хранения информации о точке вызова метода.

    Фиксирует факт вызова одного метода из другого, включая:
    - Кто вызвал (caller) и какой метод был вызван (callee)
    - Где именно в коде произошел вызов (файл и строка)

    Attributes:
        caller (MethodRef): Метод, из которого произошел вызов
        callee (MethodRef): Метод, который был вызван
        file_path (Path): Файл, где находится вызов
        line_number (int): Номер строки с вызовом

    Note:
        Используется для построения графов вызовов и анализа зависимостей.
        Все поля обязательные. Для неопределенных случаев используйте None.
    """
    caller: MethodRef
    # [1] Объект-источник вызова (откуда)
    # Содержит полную информацию о методе, включая:
    # - модуль, класс, имя метода
    # - расположение в исходном коде

    callee: MethodRef
    # [2] Объект-цель вызова (куда)
    # Формат аналогичен caller, но описывает вызываемый метод
    # Пример: метод save() вызвал метод validate()

    file_path: Path
    # [3] Абсолютный путь к файлу, где находится вызов
    # Важно: указывает на место вызова (caller), а не объявления (callee)
    # Пример: Path('/project/src/utils.py')

    line_number: int
    # [4] Номер строки в файле, где происходит вызов
    # Нумерация начинается с 1
    # Используется для навигации по коду и вывода сообщений

class SimpleDiGraph:
    """Упрощенная реализация ориентированного графа для случаев, когда networkx недоступен.

    Предоставляет базовые операции для работы с графом:
    - Добавление узлов и ребер
    - Получение списка узлов и ребер
    - Подсчет количества узлов и ребер

    Note:
        Реализация использует множества (set) для хранения данных, что обеспечивает:
        - Быструю проверку наличия элементов
        - Автоматическое устранение дубликатов
        - Эффективное хранение при большом количестве узлов

    Attributes:
        _nodes (Set[str]): Множество узлов графа
        _edges (Set[Tuple[str, str]]): Множество ребер в виде кортежей (источник, цель)
    """

    def __init__(self) -> None:
        """Инициализирует пустой граф."""
        self._nodes: Set[str] = set()            # Множество для хранения уникальных узлов
        self._edges: Set[Tuple[str, str]] = set() # Множество ребер (кортежи из двух узлов)

    def add_node(self, node: str) -> None:
        """Добавляет узел в граф.

        Args:
            node (str): Уникальный идентификатор узла
        """
        self._nodes.add(node)  # Добавление в множество гарантирует уникальность

    def add_edge(self, u: str, v: str) -> None:
        """Добавляет ориентированное ребро из узла u в узел v.

        Автоматически добавляет узлы u и v, если их нет в графе.

        Args:
            u (str): Исходный узел
            v (str): Целевой узел
        """
        self._nodes.add(u)  # Добавляем оба узла (множество игнорирует дубликаты)
        self._nodes.add(v)
        self._edges.add((u, v))  # Добавляем ребро как кортеж

    def nodes(self) -> Iterable[str]:
        """Возвращает список всех узлов графа.

        Returns:
            Iterable[str]: Список узлов в произвольном порядке
        """
        return list(self._nodes)  # Преобразуем множество в список

    def number_of_nodes(self) -> int:
        """Возвращает количество узлов в графе.

        Returns:
            int: Число уникальных узлов
        """
        return len(self._nodes)  # Используем встроенную функцию len

    def number_of_edges(self) -> int:
        """Возвращает количество ребер в графе.

        Returns:
            int: Число уникальных ребер
        """
        return len(self._edges)  # Аналогично подсчету узлов

    def edges(self) -> Iterable[Tuple[str, str]]:
        """Возвращает список всех ребер графа.

        Returns:
            Iterable[Tuple[str, str]]: Список кортежей (исходный_узел, целевой_узел)
        """
        return list(self._edges)  # Конвертируем множество ребер в список


class MethodCallResolver:
    """Анализатор вызовов методов в Python-коде с использованием статического анализа AST.

       Класс предназначен для:
        1. Поиска всех вызовов методов внутри заданного метода
        2. Разрешения типов переменных и классов
        3. Построения связей между методами в проекте

       Основная функциональность:
        - Анализ присваиваний для определения типов переменных (_infer_var_types)
        - Разрешение классов при вызовах конструкторов (_resolve_class_from_call)
        - Определение классов для атрибутов (_resolve_class_for_attribute)
        - Поиск ссылок на методы по их описанию (_find_method_ref)
        - Основной метод анализа вызовов (find_method_calls_in_method)

       Attributes:
        index (ProjectIndex): Индекс проекта с информацией о классах и методах
       Пример использования:
            >>> resolver = MethodCallResolver(project_index)
            >>> calls = resolver.find_method_calls_in_method(method_ref, module_info)
            >>> # calls содержит список (MethodRef, line_number) вызовов

      Note:
        - Использует Visitor-паттерн для обхода AST
        - Работает только со статически анализируемым кодом
        - Не обрабатывает динамические вызовы (getattr, eval)
        - Для работы требует предварительно построенный ProjectIndex
    """

    def __init__(self, index: ProjectIndex):
        self.index = index

    def _infer_var_types(self, func_node: ast.AST, module_info: ModuleInfo,
                         current_class: Optional[str]) -> Dict[str, Tuple[str, str]]:
        """Определяет типы переменных (классы) в теле функции/метода.

        Анализирует присваивания (Assign) и аннотированные присваивания (AnnAssign)
        для построения словаря "имя переменной → класс".

        Args:
            func_node (ast.AST): Узел AST функции/метода для анализа
            module_info (ModuleInfo): Информация о текущем модуле
            current_class (Optional[str]): Имя текущего класса (если есть)

        Returns:
            Dict[str, Tuple[str, str]]: Словарь вида:
                {"var_name": ("module", "class_name"), ...}

        Note:
            Использует Visitor-паттерн для обхода AST.
            Определяет только типы, созданные через явные вызовы конструкторов.
        """
        # Инициализация словаря для хранения результатов
        var_to_class: Dict[str, Tuple[str, str]] = {}

        # Вложенный класс Visitor для обработки узлов присваивания
        class AssignVisitor(ast.NodeVisitor):
            def visit_Assign(self_inner, node: ast.Assign) -> None:
                """Обрабатывает обычные присваивания (x = Class())."""
                try:
                    # Пытаемся определить класс из правой части присваивания
                    class_tuple = self._resolve_class_from_call(node.value, module_info)
                    if class_tuple is None:
                        return

                    # Обрабатываем все цели присваивания
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            # Сохраняем тип для простых переменных (не атрибутов)
                            var_to_class[target.id] = class_tuple
                finally:
                    # Продолжаем обход дерева
                    self_inner.generic_visit(node)

            def visit_AnnAssign(self_inner, node: ast.AnnAssign) -> None:
                """Обрабатывает аннотированные присваивания (x: Type = Class())."""
                try:
                    # Аналогично для аннотированных присваиваний
                    class_tuple = self._resolve_class_from_call(node.value, module_info)
                    if class_tuple is None:
                        return

                    target = node.target
                    if isinstance(target, ast.Name):
                        var_to_class[target.id] = class_tuple
                finally:
                    self_inner.generic_visit(node)

        # Запускаем обход AST функции
        AssignVisitor().visit(func_node)
        return var_to_class

    def _resolve_class_from_call(self, value: Optional[ast.AST], module_info: ModuleInfo) -> Optional[Tuple[str, str]]:
        """Определяет класс, создаваемый в вызове конструктора (ClassName() или module.ClassName()).

        Анализирует AST-узлы вызовов для определения:
        - Прямого создания объектов (ClassName())
        - Создания через импортированные модули (module.ClassName())

        Args:
            value (Optional[ast.AST]): Узел AST для анализа (ожидается ast.Call)
            module_info (ModuleInfo): Информация о текущем модуле (импорты, классы)

        Returns:
            Optional[Tuple[str, str]]: Кортеж (модуль, имя_класса) или None, если не удалось определить

        Examples:
            >>> resolve_class_from_call(ast.parse("User()").body[0].value, module_info)
            ('models', 'User')
            >>> resolve_class_from_call(ast.parse("db.User()").body[0].value, module_info)
            ('database.models', 'User')
        """
        # Проверяем, что передан узел вызова (Call)
        if not isinstance(value, ast.Call):
            return None

        # Получаем вызываемый объект (часть перед скобками)
        callee = value.func

        # Случай 1: Прямой вызов класса (ClassName())
        if isinstance(callee, ast.Name):
            name = callee.id  # Получаем имя класса

            # Проверяем, есть ли класс с таким именем в текущем модуле
            if name in module_info.class_names_in_module:
                return module_info.module, name

            # Проверяем импорты (возможно класс импортирован)
            imported = module_info.imports_name_to_target.get(name)
            if imported:
                # Разделяем полный путь на модуль и класс
                mod, cls = split_module_and_class(imported)
                if cls is not None:
                    return mod, cls

        # Случай 2: Вызов через модуль (module.ClassName())
        if isinstance(callee, ast.Attribute) and isinstance(callee.value, ast.Name):
            mod_alias = callee.value.id  # Алиас модуля (как используется в коде)
            cls = callee.attr  # Имя класса

            # Ищем полный путь модуля по алиасу
            imported = module_info.imports_name_to_target.get(mod_alias)
            if imported:
                # Возвращаем полный путь модуля и имя класса
                return imported, cls

        # Если ни один вариант не подошел
        return None

    def _resolve_class_for_attribute(self, value: ast.AST, module_info: ModuleInfo,
                                     current_class: Optional[str],
                                     var_types: Dict[str, Tuple[str, str]]) -> Optional[Tuple[str, str]]:
        """Определяет класс для атрибута в выражениях вида `obj.method()`.

        Анализирует AST для определения класса, к которому принадлежит атрибут (метод),
        учитывая self/cls, локальные классы, импорты и ранее определенные типы переменных.

        Args:
            value (ast.AST): Узел AST перед точкой в attribute access (obj в obj.method())
            module_info (ModuleInfo): Информация о текущем модуле (импорты, классы)
            current_class (Optional[str]): Имя текущего класса (для обработки self/cls)
            var_types (Dict[str, Tuple[str, str]]): Сопоставление переменных с их типами

        Returns:
            Optional[Tuple[str, str]]: Кортеж (модуль, имя_класса) или None, если класс не определен

        Examples:
            >>> resolve_class_for_attribute(ast.Name(id='self'), ...)
            ('current_module', 'CurrentClass')  # Для self
            >>> resolve_class_for_attribute(ast.Name(id='db'), ...)
            ('database', 'Connection')  # Если db определен как database.Connection
        """
        # Обработка self и cls - возвращаем текущий класс
        if isinstance(value, ast.Name) and value.id in {"self", "cls"} and current_class is not None:
            return module_info.module, current_class
            # [1] Если это 'self' или 'cls' внутри класса:
            #     - module_info.module: текущий модуль
            #     - current_class: имя окружающего класса

        # Обработка простых имен: ClassName.method() или var.method()
        if isinstance(value, ast.Name):
            name = value.id
            # Проверка локальных классов модуля
            if name in module_info.class_names_in_module:
                return module_info.module, name
                # [2] Класс определен в текущем модуле:
                #     - module_info.module: текущий модуль
                #     - name: имя класса

            # Проверка импортированных классов
            imported = module_info.imports_name_to_target.get(name)
            if imported:
                mod, cls = split_module_and_class(imported)
                if cls is not None:
                    return mod, cls
                    # [3] Класс импортирован (например, 'from pkg import Class'):
                    #     - mod: 'pkg'
                    #     - cls: 'Class'

            # Проверка ранее определенных типов переменных
            if name in var_types:
                return var_types[name]
                # [4] Переменная была определена ранее (например, 'db = Database()'):
                #     - var_types[name]: ('module', 'Database')

        # Обработка атрибутов: module.ClassName.method()
        if isinstance(value, ast.Attribute) and isinstance(value.value, ast.Name):
            mod_alias = value.value.id  # Алиас модуля
            cls = value.attr  # Имя класса
            imported = module_info.imports_name_to_target.get(mod_alias)
            if imported:
                return imported, cls
                # [5] Обработка вложенных импортов (например, 'import package.module as pm'):
                #     - imported: полный путь ('package.module')
                #     - cls: имя класса ('ClassName')

        # Если класс не удалось определить
        return None

    def find_method_calls_in_method(self, method: MethodRef, module_info: ModuleInfo) -> List[Tuple[MethodRef, int]]:
        """Находит все вызовы методов внутри указанного метода.

        Анализирует AST метода, чтобы определить:
        - Какие другие методы он вызывает
        - На каких строках происходят эти вызовы

        Args:
            method (MethodRef): Ссылка на анализируемый метод
            module_info (ModuleInfo): Информация о модуле, содержащем метод

        Returns:
            List[Tuple[MethodRef, int]]: Список кортежей:
                - MethodRef: информация о вызываемом методе
                - int: номер строки с вызовом

        Note:
            Учитывает только вызовы через точечную нотацию (obj.method()).
            Не обрабатывает динамические вызовы (getattr, __getattribute__).
        """
        # Получаем AST всего модуля из индекса
        root = self.index.modules_by_file[method.file_path].ast_root
        # [1] root - корневой узел AST модуля (ast.Module)

        # Инициализация переменных для поиска
        class_node: Optional[ast.ClassDef] = None  # [2] Узел класса, содержащего метод
        method_node: Optional[ast.AST] = None  # [3] Узел самого метода

        # Поиск нужного класса и метода в AST модуля
        for node in root.body if isinstance(root, ast.Module) else []:
            # [4] Обходим только если root - модуль, иначе пустой список
            if isinstance(node, ast.ClassDef) and node.name == method.class_name:
                # [5] Нашли нужный класс
                class_node = node
                for body_item in node.body:
                    # [6] Ищем метод в теле класса
                    if isinstance(body_item,
                                  (ast.FunctionDef, ast.AsyncFunctionDef)) and body_item.name == method.method_name:
                        method_node = body_item
                        break
                break

        # Если метод или класс не найдены - возвращаем пустой список
        if method_node is None or class_node is None:
            return []

        # Определяем типы переменных в методе
        var_types = self._infer_var_types(method_node, module_info, current_class=method.class_name)
        # [7] var_types: словарь {"var": ("module", "class")}

        # Список для хранения результатов
        calls: List[Tuple[MethodRef, int]] = []

        # Visitor для обработки вызовов методов
        class CallVisitor(ast.NodeVisitor):
            def visit_Call(self_inner, node: ast.Call) -> None:
                """Обрабатывает узлы вызовов (Call)."""
                try:
                    func = node.func
                    # [8] Обрабатываем только вызовы через точку (obj.method())
                    if isinstance(func, ast.Attribute):
                        # Определяем класс объекта, у которого вызывается метод
                        target_tuple = self._resolve_class_for_attribute(func.value, module_info, method.class_name,
                                                                         var_types)
                        if target_tuple is not None:
                            mod, cls = target_tuple
                            callee_method_name = func.attr  # [9] Имя вызываемого метода

                            # Ищем ссылку на вызываемый метод
                            callee_ref = self._find_method_ref(mod, cls, callee_method_name)
                            if callee_ref is not None:
                                # [10] Сохраняем метод и номер строки
                                calls.append((callee_ref, getattr(node, "lineno", method.line_number)))
                finally:
                    # [11] Продолжаем обход AST
                    self_inner.generic_visit(node)

        # Запускаем обход AST метода
        CallVisitor().visit(method_node)
        return calls

    def _find_method_ref(self, module: str, class_name: str, method_name: str) -> Optional[MethodRef]:
        """Находит ссылку на метод в индексе проекта по его полному или частичному имени.

        Ищет метод в указанном классе, используя следующие стратегии:
        1. По полному имени класса (модуль:класс)
        2. По короткому имени класса (если класс уникален в проекте)

        Args:
            module (str): Имя модуля, содержащего класс
            class_name (str): Имя класса, содержащего метод
            method_name (str): Имя искомого метода

        Returns:
            Optional[MethodRef]: Найденная ссылка на метод или None, если метод не найден

        Examples:
            >>> _find_method_ref("utils", "Logger", "log")
            MethodRef(module="utils", class_name="Logger", method_name="log", ...)
        """
        # Формируем полное имя класса в формате "модуль:класс"
        fq_class = f"{module}:{class_name}"
        # [1] Пример: "utils:Logger" для класса Logger в модуле utils

        # Пытаемся найти класс по полному имени
        cls = self.index.classes_by_fq.get(fq_class)
        # [2] classes_by_fq - словарь { "модуль:класс": ClassInfo }

        # Если класс не найден по полному имени...
        if cls is None:
            # Пробуем найти по короткому имени (без модуля)
            candidates = self.index.classes_by_simple.get(class_name, [])
            # [3] classes_by_simple - словарь { "класс": [ClassInfo1, ClassInfo2] }

            # Если есть ровно один класс с таким именем в проекте
            if len(candidates) == 1:
                cls = candidates[0]  # Берем единственный вариант
                # [4] Это позволяет находить классы без указания модуля,
                #     если имя класса уникально в проекте

        # Если класс так и не найден...
        if cls is None:
            return None  # Метод не может существовать

        # Возвращаем метод из найденного класса
        return cls.methods.get(method_name)
        # [5] methods - словарь методов класса { "имя_метода": MethodRef }

def split_module_and_class(qualified: str) -> Tuple[str, Optional[str]]:
    """Разделяет полное имя класса на модуль и имя класса.

    Обрабатывает строки двух форматов:
    1. Полное квалифицированное имя ("пакет.модуль.Класс")
    2. Простое имя класса ("Класс")

    Args:
        qualified (str): Строка с именем класса, возможно содержащая путь модуля.
            Примеры: "utils.helpers.Logger", "UserModel"

    Returns:
        Tuple[str, Optional[str]]: Кортеж из двух элементов:
            - str: Путь к модулю (пустая строка если не указан)
            - Optional[str]: Имя класса (None если строка пустая)

    Examples:
        >>> split_module_and_class("utils.Logger")
        ("utils", "Logger")
        >>> split_module_and_class("User")
        ("", "User")
    """
    # Разбиваем строку по точкам на компоненты
    parts = qualified.split(".")
    # [1] Пример:
    #     Вход: "a.b.Class" → parts = ["a", "b", "Class"]
    #     Вход: "Class" → parts = ["Class"]

    # Обработка случая с простым именем класса (без модуля)
    if len(parts) == 1:
        return "", parts[0]
        # [2] Возвращаем:
        #     - Пустую строку вместо модуля
        #     - Единственный элемент как имя класса

    # Обработка полного пути (модуль + класс)
    return ".".join(parts[:-1]), parts[-1]
    # [3] Возвращаем:
    #     - Все элементы кроме последнего, объединенные точками (модуль)
    #     - Последний элемент (имя класса)


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


def safe_get_line(file_path: Path, lineno: int) -> str:
    """Безопасно извлекает строку из файла по номеру строки.

    Читает указанный файл и возвращает содержимое запрошенной строки,
    гарантируя обработку ошибок и возврат пустой строки в случае проблем.

    Args:
        file_path (Path): Путь к файлу для чтения
        lineno (int): Номер строки (начинается с 1)

    Returns:
        str: Содержимое строки без символа переноса или пустая строка при ошибке

    Note:
        - Автоматически обрабатывает ошибки чтения файла
        - Игнорирует ошибки кодировки (errors="ignore")
        - Не бросает исключения при невозможности прочитать файл
    """
    try:
        # Открываем файл в режиме чтения с:
        # - Кодировкой UTF-8 (стандарт для Python)
        # - Игнорированием ошибок декодирования
        with file_path.open("r", encoding="utf-8", errors="ignore") as f:
            # Читаем файл построчно с нумерацией строк (начиная с 1)
            for i, line in enumerate(f, start=1):
                # При совпадении номера строки возвращаем её содержимое
                if i == lineno:
                    # Удаляем символ переноса строки в конце
                    return line.rstrip("\n")
    except Exception:
        # Перехватываем ВСЕ возможные исключения:
        # - FileNotFoundError (файл не существует)
        # - PermissionError (нет прав на чтение)
        # - IsADirectoryError (передана директория)
        # - Другие непредвиденные ошибки
        pass

    # Возвращаем пустую строку если:
    # - Строка не найдена
    # - Возникла ошибка при чтении
    # - Файл не существует
    return ""

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