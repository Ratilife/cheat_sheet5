import argparse
import ast
import datetime as dt
import fnmatch
import os
import re
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple
# ----------------------------- Структуры данных ----------------------------- #
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

    # ----------------------------- Ядро анализатора ------------------------------ #
class ProjectAnalyzer:
    """
        Анализатор Python-проекта для поиска неиспользуемого кода.

        Отвечает за:
        - Сканирование структуры проекта
        - Анализ использования кода
        - Выявление неиспользуемых определений
        - Обработку синтаксических ошибок

        Атрибуты:
            root_path: Абсолютный путь к корню проекта
            exclude_patterns: Паттерны исключаемых файлов/директорий
            ignore_names_regex: Регулярное выражение для игнорируемых имен
            include_methods: Флаг анализа методов классов
            max_file_size_bytes: Макс. размер файла в байтах (0 - без ограничений)
            python_files: Список Python-файлов проекта
            modules: Словарь с информацией о модулях
            syntax_issues: Список синтаксических ошибок
            used_definitions: Множество используемых определений
    """

    def __init__(
            self,
            root_path: str,
            exclude_patterns: List[str],
            ignore_names_regex: Optional[str],
            ignore_private: bool,
            include_methods: bool,
            max_file_size_kb: int,
    ) -> None:
        """Инициализация анализатора проекта."""

        # Нормализация и сохранение абсолютного пути к проекту
        self.root_path: str = os.path.abspath(root_path)

        # Удаление дубликатов в паттернах исключения
        self.exclude_patterns: List[str] = list(set(exclude_patterns))

        # Установка regex для игнорирования имен (по умолчанию dunder-методы)
        self.ignore_names_regex: str = ignore_names_regex or r"^__.*__$"

        # Добавление приватных имен (_*) к игнорируемым, если указан флаг
        if ignore_private:
            # Объединяем паттерны: dunder-методы ИЛИ имена, начинающиеся с _
            self.ignore_names_regex = rf"(?:{self.ignore_names_regex})|^_.*"

        # Компиляция регулярного выражения для быстрой проверки
        self.ignore_names_re = re.compile(self.ignore_names_regex)

        # Сохранение флага анализа методов классов
        self.include_methods: bool = include_methods

        # Конвертация KB в байты (0 означает отсутствие ограничения)
        self.max_file_size_bytes: int = max_file_size_kb * 1024 if max_file_size_kb > 0 else 0

        # Инициализация списка для хранения найденных Python-файлов
        self.python_files: List[str] = []

        # Словари для связи модулей и файлов
        self.module_to_file: Dict[str, str] = {}  # Имя модуля → путь к файлу
        self.file_to_module: Dict[str, str] = {}  # Путь к файлу → имя модуля

        # Хранилище информации о модулях
        self.modules: Dict[str, ModuleInfo] = {}

        # Список для записи синтаксических ошибок при анализе
        self.syntax_issues: List[SyntaxIssue] = []

        # Множество используемых определений в формате (модуль, имя)
        self.used_definitions: Set[Tuple[str, str]] = set()


# ----------------------------- Открытие ----------------------------- #
    def collect_python_files(self) -> None:
        """
            Собирает все Python-файлы в проекте, учитывая:
            - Исключенные директории и файлы
            - Ограничение на размер файлов
            - Построение соответствий между модулями и путями

            Алгоритм:
            1. Рекурсивно обходит директории проекта
            2. Фильтрует исключенные пути
            3. Проверяет размер файлов (если задано ограничение)
            4. Строит карту модулей проекта
        """
        # Рекурсивный обход директорий проекта
        for dirpath, dirnames, filenames in os.walk(self.root_path):
            # Получаем относительный путь от корня проекта
            rel_dir = os.path.relpath(dirpath, self.root_path)
            # Нормализация пути для корневой директории
            if rel_dir == ".":
                rel_dir = ""

            # Фильтрация исключенных поддиректорий (изменяется in-place)
            pruned_dirnames: List[str] = []
            for d in list(dirnames):
                # Формируем относительный путь поддиректории
                rel_sub = os.path.normpath(os.path.join(rel_dir, d))
                # Пропускаем исключенные директории
                if self._is_excluded(rel_sub):
                    continue
                pruned_dirnames.append(d)
            # Модифицируем список dirnames для контроля обхода walk()
            dirnames[:] = pruned_dirnames

            # Обработка файлов в текущей директории
            for filename in filenames:
                # Пропускаем не-Python файлы
                if not filename.endswith(".py"):
                    continue
                # Формируем относительный путь файла
                rel_file = os.path.normpath(os.path.join(rel_dir, filename)) if rel_dir else filename
                # Пропускаем исключенные файлы
                if self._is_excluded(rel_file):
                    continue
                # Полный абсолютный путь к файлу
                abs_file = os.path.join(self.root_path, rel_file)
                # Проверка размера файла (если задано ограничение)
                if self.max_file_size_bytes:
                    try:
                        if os.path.getsize(abs_file) > self.max_file_size_bytes:
                            continue
                    except OSError:
                        continue
                self.python_files.append(abs_file)

        # Построение соответствий между модулями и файлами
        for file_path in self.python_files:
            # Получаем имя модуля из пути
            module_name = self._module_name_from_path(file_path)
            # Заполняем словари соответствий
            self.module_to_file[module_name] = file_path
            self.file_to_module[file_path] = module_name

    def _is_excluded(self, rel_path: str) -> bool:
        """
            Проверяет, должен ли указанный путь быть исключен из анализа.

            Использует несколько стратегий проверки:
            1. Прямое совпадение по glob-шаблону
            2. Совпадение любой части пути с шаблоном
            3. Наличие подстроки шаблона в пути

            Параметры:
                rel_path: Относительный путь для проверки (с разделителями ОС)

            Возвращает:
                bool: True если путь должен быть исключен, иначе False

            Особенности:
                - Регистронезависимая проверка
                - Обработка пустых путей
                - Поддержка разных ОС через os.sep
        """
        # Проверка на пустой путь (корневая директория)
        if not rel_path:
            return False
        # Приведение к нижнему регистру для регистронезависимого сравнения
        lowered = rel_path.lower()
        # Разбиение пути на компоненты (части между разделителями)
        parts = lowered.split(os.sep)
        # Проверка каждого паттерна исключения
        for pat in self.exclude_patterns:
            pat_lower = pat.lower()
            # 1. Проверка полного совпадения по glob-шаблону
            if fnmatch.fnmatch(lowered, pat_lower):
                return True
            # 2. Проверка точного совпадения с любой частью пути
            if pat_lower in parts:
                return True
            # 3. Проверка на вхождение подстроки (для сложных случаев)
            if pat_lower in lowered:
                return True
        # Если ни один паттерн не совпал - не исключаем
        return False

    def _module_name_from_path(self, file_path: str) -> str:
        """
         Преобразует абсолютный путь к файлу в имя Python-модуля в формате dotted notation.

         Алгоритм преобразования:
         1. Получает относительный путь от корня проекта
         2. Заменяет разделители ОС на точки
         3. Удаляет расширение .py
         4. Обрабатывает специальный случай __init__.py
         5. Удаляет ведущие точки (артефакты преобразования)

         Параметры:
             file_path: Абсолютный путь к Python-файлу

         Возвращает:
             str: Имя модуля в формате package.subpackage.module

         Пример:
             /project/root/pkg/mod.py -> "pkg.mod"
             /project/root/pkg/__init__.py -> "pkg"
         """
        # Получаем относительный путь от корня проекта
        rel = os.path.relpath(file_path, self.root_path)
        # Заменяем разделители путей на точки (для Python-нотации)
        rel = rel.replace(os.sep, ".")
        # Удаляем расширение .py если присутствует
        if rel.endswith(".py"):
            rel = rel[:-3]
        # Специальная обработка __init__.py файлов
        if rel.endswith(".__init__"):
            rel = rel[: -len(".__init__")]
        # Удаляем возможные ведущие точки (артефакты преобразования)
        return rel.lstrip(".")

    # ----------------------------- Проход синтаксического анализа -------------------------- #
    def first_pass_collect(self) -> None:
        """
        Первичный сбор информации о модулях проекта.

        Выполняет:
        1. Чтение и парсинг исходного кода файлов
        2. Обработку ошибок ввода-вывода и синтаксических ошибок
        3. Анализ AST дерева для сбора информации о:
           - Определениях (функции, классы, переменные)
           - Импортах
           - Экспортах (__all__)
           - Недостижимом коде
        4. Сохранение результатов анализа для каждого модуля

        Особенности:
        - Обрабатывает файлы последовательно
        - Продолжает работу при ошибках, фиксируя их
        - Использует visitor-паттерн для обхода AST
        """

        # Обход всех Python-файлов проекта
        for file_path in self.python_files:
            # Чтение исходного кода файла с обработкой ошибок
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    source = f.read()
            except OSError as e:
                # Фиксация ошибок ввода-вывода
                self.syntax_issues.append(
                    SyntaxIssue(file_path=file_path, line=0, col=0, message=f"IOError: {e}")
                )
                continue

            # Парсинг исходного кода в AST
            try:
                tree = ast.parse(source, filename=file_path)
            except SyntaxError as e:
                # Фиксация синтаксических ошибок с указанием позиции
                self.syntax_issues.append(
                    SyntaxIssue(
                        file_path=file_path,
                        line=getattr(e, "lineno", 0) or 0,
                        col=getattr(e, "offset", 0) or 0,
                        message=f"SyntaxError: {e.msg}",
                    )
                )
                continue

            # Получение имени модуля из ранее построенного отображения
            module_name = self.file_to_module[file_path]

            # Создание объекта с информацией о модуле
            minfo = ModuleInfo(module_name, file_path, tree)

            # Инициализация сборщика информации о модуле
            collector = _ModuleCollector(
                module_name=module_name,
                file_path=file_path,
                include_methods=self.include_methods,
                ignore_name_re=self.ignore_names_re,
            )

            # Обход AST дерева для сбора информации
            collector.visit(tree)

            # Сохранение собранных данных
            minfo.definitions = collector.definitions
            minfo.imports = collector.imports
            minfo.all_exports = collector.all_exports
            minfo.unreachable = collector.unreachable

            # Добавление информации о модуле в общее хранилище
            self.modules[module_name] = minfo

    # ----------------------------- Пропуск на использование ---------------------------- #
    def second_pass_usage(self) -> None:
        """
        Второй проход анализа - сбор информации об использовании кода.

        Основные задачи:
        1. Анализ фактического использования определений в коде
        2. Отслеживание использования:
           - Локальных имен (переменных, функций, классов)
           - Импортированных объектов
           - Атрибутов импортированных модулей
        3. Учет экспортируемых имен (__all__)
        4. Обновление множества используемых определений

        Особенности:
        - Использует visitor-паттерн для анализа AST
        - Учитывает разные виды использования кода
        - Обновляет состояние анализатора для последующего анализа
        """

        # Обход всех модулей проекта
        for module_name, minfo in self.modules.items():
            # Инициализация сборщика использования кода
            usage = _UsageCollector(
                current_module=module_name,  # Текущий анализируемый модуль
                module_to_file=self.module_to_file,  # Соответствие модулей и файлов
                modules=self.modules,  # Информация о всех модулях
            )

            # Обход AST для сбора информации об использовании
            usage.visit(minfo.tree)

            # 1. Фиксация используемых локальных определений
            for name in usage.used_local_names:
                self.used_definitions.add((module_name, name))

            # 2. Сохранение используемых алиасов импортов
            minfo.used_aliases = usage.used_import_aliases.copy()

            # 3. Обработка объектов, импортированных через 'from X import Y'
            for (src_module, name) in usage.used_foreign_defs:
                self.used_definitions.add((src_module, name))

            # 4. Обработка атрибутов импортированных модулей (import a; a.foo)
            for (src_module, name) in usage.used_foreign_attrs:
                self.used_definitions.add((src_module, name))

            # 5. Обработка экспортируемых имен (__all__)
            for name in minfo.all_exports:
                # Помечаем определение в текущем модуле как используемое
                self.used_definitions.add((module_name, name))

                # Если имя реэкспортируется через __all__, помечаем алиас как используемый
                if name in minfo.imports:
                    minfo.used_aliases.add(name)

    # ----------------------------- Отчет -------------------------------- #
    def compile_report(self) -> str:
        """
        Формирует итоговый отчет о неиспользуемом коде и проблемах в проекте.

        Структура отчета:
        1. Заголовок с метаинформацией (время, параметры сканирования)
        2. Сводная статистика по всем категориям
        3. Детализированные списки для каждой категории проблем

        Возвращает:
            str: Форматированный текстовый отчет, готовый для сохранения в файл

        Особенности:
        - Сортировка всех данных для удобства чтения
        - Группировка по типам проблем
        - Четкая структура с заголовками разделов
        """

        # Инициализация списков для хранения различных типов неиспользуемого кода
        unused_imports: List[Tuple[str, int, str]] = []  # (файл, строка, алиас)
        unused_functions: List[Symbol] = []  # Неиспользуемые функции/методы
        unused_classes: List[Symbol] = []  # Неиспользуемые классы
        unused_variables: List[Symbol] = []  # Неиспользуемые переменные
        unreachable: List[Unreachable] = []  # Недостижимый код

        # Анализ каждого модуля для выявления неиспользуемых элементов
        for module_name, minfo in sorted(self.modules.items()):
            # Проверка неиспользуемых импортов
            for alias, binding in minfo.imports.items():
                if alias not in minfo.used_aliases:
                    unused_imports.append((minfo.file_path, binding.line, alias))

            # Проверка неиспользуемых определений (функции, классы, переменные)
            for name, sym in minfo.definitions.items():
                if self.ignore_names_re.search(name):  # Пропуск исключенных имен
                    continue
                if (sym.module, sym.name) not in self.used_definitions:
                    if sym.kind == "function":
                        unused_functions.append(sym)
                    elif sym.kind == "class":
                        unused_classes.append(sym)
                    elif sym.kind == "variable":
                        unused_variables.append(sym)
                    elif sym.kind == "method":  # Методы учитываются как функции
                        unused_functions.append(sym)

            # Сбор информации о недостижимом коде
            unreachable.extend(minfo.unreachable)

        # Сортировка синтаксических ошибок по файлу и позиции
        syntax_issues_sorted = sorted(self.syntax_issues, key=lambda s: (s.file_path, s.line, s.col))

        # Формирование заголовка отчета
        now = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        header = [
            f"Отчет о неиспользуемом коде",
            f"Сгенерирован: {now}",
            f"Корневая директория: {self.root_path}",
            f"Исключенные шаблоны: {', '.join(self.exclude_patterns) if self.exclude_patterns else '(нет)'}",
            f"Регулярка для игнорирования имен: {self.ignore_names_regex}",
            "",
        ]

        sections: List[str] = []  # Список для хранения разделов отчета

        def format_list(title: str, items: List[str]) -> None:
            """Вспомогательная функция для форматирования разделов отчета"""
            sections.append(title)
            if not items:
                sections.append("  (не найдено)")
            else:
                sections.extend(items)
            sections.append("")

        # Формирование сводной статистики
        summary_lines = [
            f"Всего файлов просканировано: {len(self.modules)}",
            f"Неиспользуемых импортов: {len(unused_imports)}",
            f"Неиспользуемых функций/методов: {len(unused_functions)}",
            f"Неиспользуемых классов: {len(unused_classes)}",
            f"Неиспользуемых переменных: {len(unused_variables)}",
            f"Обнаружено недостижимого кода: {len(unreachable)}",
            f"Синтаксических ошибок: {len(syntax_issues_sorted)}",
            "",
        ]

        # Формирование детализированных разделов

        # 1. Неиспользуемые импорты
        format_list(
            "Неиспользуемые импорты (файл:строка алиас)",
            [f"  {file}:{line} {alias}" for (file, line, alias) in sorted(unused_imports)],
        )

        # 2. Неиспользуемые функции/методы
        format_list(
            "Неиспользуемые функции/методы (файл:строка имя)",
            [f"  {s.file_path}:{s.line} {s.name}" for s in
             sorted(unused_functions, key=lambda x: (x.file_path, x.line, x.name))],
        )

        # 3. Неиспользуемые классы
        format_list(
            "Неиспользуемые классы (файл:строка имя)",
            [f"  {s.file_path}:{s.line} {s.name}" for s in
             sorted(unused_classes, key=lambda x: (x.file_path, x.line, x.name))],
        )

        # 4. Неиспользуемые переменные
        format_list(
            "Неиспользуемые переменные (файл:строка имя)",
            [f"  {s.file_path}:{s.line} {s.name}" for s in
             sorted(unused_variables, key=lambda x: (x.file_path, x.line, x.name))],
        )

        # 5. Недостижимый код
        format_list(
            "Недостижимый код (файл:строка функция причина)",
            [f"  {u.file_path}:{u.line} {u.function} {u.reason}" for u in
             sorted(unreachable, key=lambda x: (x.file_path, x.line, x.function))],
        )

        # 6. Синтаксические ошибки
        format_list(
            "Синтаксические ошибки (файл:строка:колонка сообщение)",
            [f"  {s.file_path}:{s.line}:{s.col} {s.message}" for s in syntax_issues_sorted],
        )

        # Объединение всех частей отчета в одну строку
        return "\n".join(header + summary_lines + sections)

    def write_report(self, output_path: str, report_text: str) -> None:
        """
        Записывает сформированный отчет о неиспользуемом коде в файл.

        Выполняет:
        1. Проверку и создание директории для отчета (если требуется)
        2. Безопасную запись данных в файл с указанной кодировкой
        3. Обработку путей (нормализацию и преобразование в абсолютные)

        Параметры:
            output_path: Путь для сохранения отчета
            report_text: Текст отчета для сохранения

        Особенности:
        - Автоматически создает недостающие директории
        - Использует UTF-8 кодировку для корректного сохранения
        - Обрабатывает относительные и абсолютные пути
        """

        # Получаем абсолютный путь к директории для сохранения
        out_dir = os.path.dirname(os.path.abspath(output_path))

        # Создаем директорию, если она не существует
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)  # exist_ok=True предотвращает ошибку если директория уже существует

        # Записываем отчет в файл с кодировкой UTF-8
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report_text)
    # ----------------------------- Запуск (Runner) --------------------------------#
    def run(self, output_path: str) -> None:
        self.collect_python_files()
        self.first_pass_collect()
        self.second_pass_usage()
        report = self.compile_report()
        self.write_report(output_path, report)

# ----------------------------- AST Visitors (Посетители) ------------------------------- #
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
        """
        Добавляет определение (функцию, класс, переменную) в коллекцию определений модуля.

        Параметры:
            name: Имя определяемого символа
            node: AST-узел с информацией о расположении
            kind: Тип определения ('function', 'class', 'variable', 'method')

        Особенности:
        - Автоматически определяет номер строки для разных типов узлов
        - Предотвращает дублирование определений
        - Сохраняет полную информацию о местоположении символа
        """

        # Определение номера строки в зависимости от типа узла
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            # Для функций и классов берем номер строки напрямую из узла
            line = node.lineno
        else:
            # Для других типов узлов пытаемся получить номер строки, по умолчанию 1
            line = getattr(node, "lineno", 1)

        # Добавление определения в словарь, если оно еще не существует
        self.definitions.setdefault(
            name,
            # Создание объекта Symbol с информацией о определении
            Symbol(
                name=name,  # Имя символа
                module=self.module_name,  # Имя текущего модуля
                file_path=self.file_path,  # Путь к файлу
                line=line,  # Номер строки
                kind=kind  # Тип определения
            ),
        )
    def _collect_all_exports(self, node: ast.Assign) -> None:
        """
        Собирает имена, экспортируемые через переменную __all__, для определения публичного API модуля.

        Обрабатывает случаи:
        - __all__ = ["name1", "name2"] (список)
        - __all__ = ("name1", "name2") (кортеж)

        Параметры:
            node: AST-узел присваивания (ast.Assign)

        Особенности:
        - Игнорирует некорректные или сложные выражения
        - Добавляет только непустые строковые имена
        - Автоматически пропускает ошибки парсинга
        """

        # Обработка присваивания __all__ в безопасном блоке try-except
        try:
            # Перебор всех целей присваивания (может быть множественное присваивание)
            for target in node.targets:
                # Проверяем, что цель - это имя __all__
                if isinstance(target, ast.Name) and target.id == "__all__":
                    # Извлекаем строковые имена из значения (списка/кортежа)
                    names = _extract_str_names(node.value)

                    # Добавляем все непустые имена в множество экспортов
                    for n in names:
                        if n:  # Проверка на непустую строку
                            self.all_exports.add(n)

        # Игнорируем любые ошибки при разборе (некорректный синтаксис и т.д.)
        except Exception:
            pass

    # ---- Visitors ---- #
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """
        Обрабатывает определение класса в AST-дереве.

        Выполняет:
        1. Регистрацию классов модульного уровня (не вложенных)
        2. Отслеживание вложенности классов для анализа методов
        3. Обход дочерних узлов класса

        Параметры:
            node: AST-узел определения класса
        """

        # Проверяем, что класс находится на уровне модуля (не вложен в функцию/класс)
        if not self._function_stack and not self._class_stack:
            # Проверяем, что имя класса не попадает под игнорируемые шаблоны
            if not self.ignore_name_re.search(node.name):
                # Регистрируем определение класса
                self._add_definition(node.name, node, "class")

        # Добавляем класс в стек для отслеживания вложенности (важно для методов)
        self._class_stack.append(node.name)

        # Рекурсивный обход дочерних узлов класса (тело класса)
        self.generic_visit(node)

        # Удаляем класс из стека после обработки всех дочерних узлов
        self._class_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """
        Обрабатывает определение обычной (не асинхронной) функции в AST-дереве.

        Перенаправляет вызов на общий метод обработки функций (_visit_function_like),
        который содержит основную логику анализа.

        Параметры:
            node: AST-узел определения функции
        """

        # Делегирование обработки в общий метод для функций
        self._visit_function_like(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """
        Обрабатывает определение асинхронной функции (async def) в AST-дереве.

        Перенаправляет вызов на общий метод обработки функций (_visit_function_like),
        обеспечивая единый подход к анализу как синхронных, так и асинхронных функций.

        Параметры:
            node: AST-узел определения асинхронной функции
        """

        # Передача узла асинхронной функции в общий обработчик
        self._visit_function_like(node)

    def _visit_function_like(self, node: ast.AST) -> None:
        """
        Базовый метод для обработки функций и методов в AST-дереве.

        Выполняет:
        1. Определение типа функции (модульная/метод)
        2. Регистрацию определений с учетом фильтров
        3. Анализ недостижимого кода внутри функции
        4. Обход тела функции

        Параметры:
            node: AST-узел функции (обычной или асинхронной)
        """

        # Получаем имя функции или используем "<anonymous>" для анонимных функций
        name = getattr(node, "name", "<anonymous>")

        # Определяем, является ли текущая функция методом класса
        is_method = bool(self._class_stack)

        # Обработка функций модульного уровня (не методов)
        if not self._function_stack and not is_method:
            # Проверяем, что имя не попадает под игнорируемые шаблоны
            if not self.ignore_name_re.search(name):
                # Регистрируем функцию модульного уровня
                self._add_definition(name, node, "function")

        # Обработка методов класса (если включен анализ методов)
        elif is_method and self.include_methods:
            # Проверяем, что имя метода не игнорируется
            if not self.ignore_name_re.search(name):
                # Регистрируем метод класса
                self._add_definition(name, node, "method")

        # Анализ недостижимого кода внутри функции:
        # 1. Добавляем текущую функцию в стек вызовов
        self._function_stack.append(name)

        # 2. Собираем информацию о недостижимом коде
        self._collect_unreachable_in_function(node)

        # 3. Рекурсивно обходим тело функции
        self.generic_visit(node)

        # 4. Удаляем функцию из стека после обработки
        self._function_stack.pop()

    def _collect_unreachable_in_function(self, node: ast.AST) -> None:
        """
        Анализирует тело функции на наличие недостижимого кода после контрольных операторов.

        Обнаруживает код, который никогда не будет выполнен из-за:
        - return (возврата из функции)
        - raise (возбуждения исключения)
        - break/continue (прерывания циклов)

        Параметры:
            node: AST-узел функции (FunctionDef/AsyncFunctionDef)
        """

        # Получаем тело функции или пустой список, если атрибута нет
        body: List[ast.stmt] = getattr(node, "body", [])

        # Флаг достижимости текущей инструкции
        reachable = True

        # Последовательный анализ всех инструкций в теле функции
        for i, stmt in enumerate(body):
            # Если код недостижим (после return/raise/break/continue)
            if not reachable:
                # Добавляем информацию о недостижимой инструкции
                self.unreachable.append(
                    Unreachable(
                        file_path=self.file_path,  # Путь к файлу
                        module=self.module_name,  # Имя модуля
                        # Имя текущей функции или <module> для верхнего уровня
                        function=self._function_stack[-1] if self._function_stack else "<module>",
                        line=getattr(stmt, "lineno", 1),  # Номер строки с fallback на 1
                        reason="after return/raise/break/continue",  # Тип причины
                    )
                )
                continue  # Пропускаем дальнейший анализ недостижимого кода

            # Проверяем, является ли инструкция "конечной" (прерывающей выполнение)
            if isinstance(stmt, (ast.Return, ast.Raise, ast.Continue, ast.Break)):
                reachable = False  # Все последующие инструкции помечаются как недостижимые

    def visit_Assign(self, node: ast.Assign) -> None:
        """
        Обрабатывает операторы присваивания в AST-дереве.

        Основные задачи:
        1. Сбор информации о переменных __all__ (экспортируемых именах модуля)
        2. Регистрация переменных модульного уровня
        3. Игнорирование локальных переменных внутри функций

        Параметры:
            node: AST-узел присваивания (ast.Assign)
        """

        # 1. Сначала проверяем, не является ли присваивание экспортом __all__
        self._collect_all_exports(node)

        # 2. Пропускаем локальные переменные внутри функций
        if self._function_stack:
            return

        # 3. Обрабатываем только переменные модульного уровня
        for target in node.targets:
            # Извлекаем все имена из целевой части присваивания
            for name in _names_from_target(target):
                # Проверяем, что имя не попадает под игнорируемые шаблоны
                if not self.ignore_name_re.search(name):
                    # Регистрируем переменную модульного уровня
                    self._add_definition(name, node, "variable")

        # 4. Продолжаем стандартный обход дочерних узлов
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        """
        Обрабатывает аннотированные присваивания (с указанием типа) в AST-дереве.

        Основные задачи:
        1. Пропуск локальных переменных внутри функций/классов
        2. Регистрация аннотированных переменных модульного уровня
        3. Фильтрация игнорируемых имен

        Параметры:
            node: AST-узел аннотированного присваивания (ast.AnnAssign)
        """

        # Пропускаем локальные переменные внутри функций и классов
        if self._function_stack or self._class_stack:
            return

        # Получаем цель присваивания (левую часть)
        target = node.target

        # Извлекаем все имена из целевой части
        for name in _names_from_target(target):
            # Проверяем, что имя не попадает под игнорируемые шаблоны
            if not self.ignore_name_re.search(name):
                # Регистрируем аннотированную переменную модульного уровня
                self._add_definition(name, node, "variable")

        # Продолжаем стандартный обход дочерних узлов
        self.generic_visit(node)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        """
        Обрабатывает операторы расширенного присваивания (+=, -= и т.д.) в AST-дереве.

        Основные задачи:
        1. Пропуск локальных операций внутри функций
        2. Регистрация переменных модульного уровня
        3. Фильтрация игнорируемых имен

        Параметры:
            node: AST-узел расширенного присваивания (ast.AugAssign)
        """

        # Пропускаем операции внутри функций (учитываем только модульный уровень)
        if self._function_stack:
            return

        # Извлекаем имена переменных из левой части операции
        for name in _names_from_target(node.target):
            # Проверяем, что имя не должно быть проигнорировано
            if not self.ignore_name_re.search(name):
                # Регистрируем переменную как определение
                self._add_definition(name, node, "variable")

        # Продолжаем стандартный обход AST
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        """
        Обрабатывает стандартные импорты модулей (import ...) в AST-дереве.

        Основные задачи:
        1. Разбор конструкции import с учетом алиасов (as)
        2. Определение базового имени модуля (первая часть точки)
        3. Сохранение информации о привязках импорта

        Параметры:
            node: AST-узел импорта (ast.Import)
        """

        # Обрабатываем каждый импорт в узле (может быть несколько через запятую)
        for alias in node.names:
            # Определяем имя для использования в коде:
            # если есть алиас (as) - используем его, иначе берем первую часть пути
            alias_name = alias.asname or alias.name.split(".")[0]

            # Создаем объект с информацией о привязке импорта
            binding = ImportBinding(
                alias=alias_name,  # Имя, используемое в коде
                type="import",  # Тип импорта (прямой)
                module=alias.name,  # Полное имя импортируемого модуля
                name=None,  # Для import нет конкретного имени
                level=0,  # Уровень относительного импорта
                line=node.lineno,  # Номер строки с импортом
            )

            # Сохраняем привязку в словаре импортов
            self.imports[alias_name] = binding

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """
        Обрабатывает импорты вида 'from ... import ...' в AST-дереве.

        Основные задачи:
        1. Пропуск импортов с '*' (не анализирует from ... import *)
        2. Обработка обычных импортов и алиасов (as)
        3. Сохранение полной информации о привязках импорта

        Параметры:
            node: AST-узел импорта (ast.ImportFrom)
        """

        # Обрабатываем каждый элемент импорта
        for alias in node.names:
            # Специальная обработка импортов с '*' - пропускаем их
            if alias.name == '*':
                continue  # Не анализируем звёздочные импорты

            # Определяем имя для использования в коде:
            # если есть алиас (as) - используем его, иначе оригинальное имя
            alias_name = alias.asname or alias.name

            # Создаем объект с информацией о привязке импорта
            binding = ImportBinding(
                alias=alias_name,  # Имя, используемое в коде
                type="from",  # Тип импорта (from-import)
                module=node.module,  # Имя модуля, из которого импортируем
                name=alias.name,  # Оригинальное имя импортируемого объекта
                level=node.level or 0,  # Уровень относительного импорта (.parent)
                line=node.lineno,  # Номер строки с импортом
            )

            # Сохраняем привязку в словаре импортов
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
        """
        Возвращает информацию о текущем анализируемом модуле.

        Возвращает:
            ModuleInfo: Объект с метаданными и аналитической информацией о модуле

        Особенности:
        - Быстрый доступ к данным модуля через кешированную ссылку
        - Использует текущее имя модуля (self.current_module) как ключ
        - Гарантирует наличие информации (не создает новый объект)
        """

        # Получение объекта ModuleInfo из словаря modules по текущему имени модуля
        return self.modules[self.current_module]

    def _resolve_from_module(self, binding: ImportBinding) -> Optional[str]:
        """
        Преобразует относительные импорты в абсолютные пути модулей.

        Параметры:
            binding: Информация о привязке импорта

        Возвращает:
            Optional[str]: Абсолютный путь модуля или None, если преобразование невозможно

        Особенности:
        - Работает только с from-импортами
        - Обрабатывает многоуровневые относительные импорты (.., ...)
        - Корректно обрабатывает комбинации относительных и абсолютных путей
        """

        # Проверяем, что это from-импорт (для обычных import не требуется преобразование)
        if binding.type != "from":
            return None

        # Получаем имя исходного модуля (может быть None или пустой строкой)
        src_module = binding.module or ""

        # Получаем уровень относительного импорта (0 = абсолютный)
        level = binding.level

        # Если импорт абсолютный - возвращаем исходное имя модуля
        if level == 0:
            return src_module or None

        # Разбиваем текущий модуль на компоненты для вычисления базового пути
        parts = self.current_module.split(".")

        # Удаляем последний компонент (имя текущего модуля) чтобы получить пакет
        if parts:
            parts = parts[:-1]

        # Вычисляем сколько уровней нужно подняться (level-1)
        ascend = max(0, level - 1)

        # Поднимаемся на нужное количество уровней вверх
        if ascend > 0:
            parts = parts[: max(0, len(parts) - ascend)]

        # Добавляем путь из исходного модуля (если он указан)
        if src_module:
            parts += src_module.split(".")

        # Собираем итоговый путь, фильтруя пустые компоненты
        resolved = ".".join([p for p in parts if p])

        # Возвращаем результат или None если путь пустой
        return resolved or None

    def visit_Name(self, node: ast.Name) -> None:
        """
        Обрабатывает использование имен (переменных, функций, классов) в AST-дереве.

        Основные задачи:
        1. Отслеживание использования локальных определений
        2. Учет использования импортированных имен
        3. Анализ внешних зависимостей (from-импорты)

        Параметры:
            node: AST-узел имени (ast.Name)
        """

        # Пропускаем, если имя используется не для чтения (например, в присваивании)
        if not isinstance(node.ctx, ast.Load):
            return

        # Получаем имя, которое используется
        name = node.id

        # Получаем информацию о текущем модуле
        minfo = self._get_current_module_info()

        # 1. Проверка использования локальных определений
        if name in minfo.definitions:
            self.used_local_names.add(name)  # Помечаем имя как использованное
            return

        # 2. Проверка использования импортированных имен
        if name in minfo.imports:
            # Добавляем алиас в использованные
            self.used_import_aliases.add(name)

            # Получаем информацию о привязке импорта
            binding = minfo.imports[name]

            # Специальная обработка from-импортов:
            if binding.type == "from" and binding.name:
                # Преобразуем относительный путь в абсолютный
                resolved_mod = self._resolve_from_module(binding)

                # Проверяем, что модуль принадлежит нашему проекту
                if resolved_mod and resolved_mod in self.module_to_file:
                    # Получаем информацию о целевом модуле
                    target_modinfo = self.modules.get(resolved_mod)

                    # Если имя определено в целевом модуле - помечаем как использованное
                    if target_modinfo and binding.name in target_modinfo.definitions:
                        self.used_foreign_defs.add((resolved_mod, binding.name))

    def visit_Attribute(self, node: ast.Attribute) -> None:
        """
        Обрабатывает обращения к атрибутам объектов в AST-дереве.

        Основные задачи:
        1. Выявление использования атрибутов импортированных модулей
        2. Проверка принадлежности модуля к проекту
        3. Фиксация факта использования атрибутов

        Параметры:
            node: AST-узел атрибута (ast.Attribute)
        """

        # Анализируем значение, к которому обращаемся через точку
        value = node.value

        # Обрабатываем только случаи, когда обращение идет через имя (не через выражение)
        if isinstance(value, ast.Name):
            alias = value.id  # Получаем имя объекта (модуля)

            # Получаем информацию о текущем модуле
            minfo = self._get_current_module_info()

            # Проверяем, является ли имя импортированным модулем
            if alias in minfo.imports:
                binding = minfo.imports[alias]  # Получаем информацию о привязке

                # Обрабатываем случай прямого импорта (import module)
                if binding.type == "import" and binding.module:
                    src_module = binding.module  # Имя исходного модуля

                    # Проверяем, что модуль принадлежит анализируемому проекту
                    if src_module in self.module_to_file:
                        # Получаем информацию о целевом модуле
                        target_modinfo = self.modules.get(src_module)

                        # Если атрибут является определением в целевом модуле
                        if target_modinfo and node.attr in target_modinfo.definitions:
                            # Фиксируем использование атрибута
                            self.used_foreign_attrs.add((src_module, node.attr))

                # Для from-импортов не выполняем анализ (слишком сложно отслеживать)
                elif binding.type == "from":
                    pass  # Намеренно пропускаем

        # Продолжаем стандартный обход дочерних узлов
        self.generic_visit(node)


    # ----------------------------- Utilities --------------------------------- #
def _extract_str_names(node: ast.AST) -> List[str]:
    """
        Извлекает список строковых констант из AST-узла.

        Обрабатывает:
        - Списки и кортежи строк
        - Отдельные строковые константы
        - Конкатенацию строк/списков через оператор +

        Параметры:
            node: AST-узел для анализа

        Возвращает:
            List[str]: Список найденных строковых значений

        Особенности:
        - Рекурсивный обход вложенных структур
        - Устойчивость к ошибкам (некорректные узлы игнорируются)
        - Поддержка разных вариантов объявления __all__
    """

    names: List[str] = []  # Инициализация списка для результатов

    try:
        # Обработка списков и кортежей
        if isinstance(node, (ast.List, ast.Tuple)):
            for elt in node.elts:  # Рекурсивный обход элементов
                names.extend(_extract_str_names(elt))

        # Обработка строковых констант
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            names.append(node.value)  # Добавление найденной строки

        # Обработка операций конкатенации (a + b)
        elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            left = _extract_str_names(node.left)  # Рекурсивный обход левой части
            right = _extract_str_names(node.right)  # Рекурсивный обход правой части
            names.extend(left + right)  # Объединение результатов

    except Exception:  # Защита от любых ошибок при разборе
        pass

    return names  # Возврат списка найденных строк


def _names_from_target(target: ast.AST) -> List[str]:
    """
    Извлекает список имен переменных из целевой части оператора присваивания.

    Обрабатывает:
    - Простые переменные (Name)
    - Кортежи и списки имен (Tuple/List)

    Параметры:
        target: AST-узел цели присваивания

    Возвращает:
        List[str]: Список найденных имен переменных

    Особенности:
    - Рекурсивный обход вложенных структур
    - Игнорирование сложных целей (атрибуты, подписки)
    - Работа только с именами верхнего уровня
    """

    names: List[str] = []  # Инициализация списка для результатов

    # Обработка простого имени переменной
    if isinstance(target, ast.Name):
        names.append(target.id)  # Добавляем идентификатор переменной

    # Обработка кортежей и списков в левой части присваивания
    elif isinstance(target, (ast.Tuple, ast.List)):
        # Рекурсивный обход всех элементов
        for elt in target.elts:
            names.extend(_names_from_target(elt))

    # Сложные цели (obj.attr, arr[index]) сознательно игнорируются
    return names  # Возвращаем список найденных имен
# ----------------------------- CLI --------------------------------------- #
def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Парсит аргументы командной строки для сканера неиспользуемого кода.

    Аргументы:
        argv: Опциональный список аргументов командной строки (по умолчанию: None,
              использует sys.argv). Полезно для тестирования.

    Возвращает:
        argparse.Namespace: Объект с распарсенными аргументами, содержащий:
            - root: Корневая директория проекта для сканирования
            - output: Путь к файлу отчета
            - exclude: Шаблоны/пути для исключения
            - ignore_names: Регулярное выражение для игнорируемых имен
            - ignore_private: Игнорировать ли приватные имена (начинающиеся с _)
            - include_methods: Проверять ли методы классов
            - max_file_size_kb: Максимальный размер .py файла для обработки (в КБ)
    """
    # Инициализация парсера аргументов с описанием скрипта
    parser = argparse.ArgumentParser(
        description=(
            "Сканирует Python проект на наличие неиспользуемого кода: "
            "неиспользуемые импорты, функции уровня модуля, классы, "
            "переменные и недостижимый код."
        )
    )

    # Аргумент --root для указания корневой директории проекта
    parser.add_argument(
        "--root",
        default=os.getcwd(),  # По умолчанию: текущая рабочая директория
        help="Корневая директория проекта для сканирования (по умолчанию: текущая директория)",
    )

    # Обязательный аргумент --output для указания файла отчета
    parser.add_argument(
        "--output",
        required=True,  # Обязательный аргумент
        help="Путь к .txt файлу для записи отчета",
    )

    # Аргумент --exclude для исключения файлов/директорий
    parser.add_argument(
        "--exclude",
        action="append",  # Позволяет указывать несколько значений
        default=[
            ".git", "__pycache__", ".venv", "venv",  # Системные директории и виртуальные окружения
            "build", "dist",  # Артефакты сборки
            ".mypy_cache", ".pytest_cache"  # Кеши инструментов
        ],
        help=(
            "Шаблоны или части путей для исключения (можно указывать несколько раз)."
            " По умолчанию исключаются common виртуальные окружения и кеш-директории."
        ),
    )

    # Аргумент --ignore-names для фильтрации имен
    parser.add_argument(
        "--ignore-names",
        default=r"^__.*__$",  # По умолчанию: игнорировать dunder-методы (__init__ и т.д.)
        help=(
            "Регулярное выражение для имен, которые следует игнорировать "
            "(по умолчанию: dunder-методы). Можно комбинировать с --ignore-private "
            "для игнорирования имен, начинающихся с _"
        ),
    )

    # Флаг --ignore-private для игнорирования приватных имен
    parser.add_argument(
        "--ignore-private",
        action="store_true",  # True, если флаг указан
        help="Также игнорировать имена, начинающиеся с подчеркивания (_)",
    )

    # Флаг --include-methods для проверки методов классов
    parser.add_argument(
        "--include-methods",
        action="store_true",  # True, если флаг указан
        help="Включать методы классов в проверку неиспользуемых функций (может давать ложные срабатывания)",
    )

    # Аргумент --max-file-size-kb для ограничения размера файлов
    parser.add_argument(
        "--max-file-size-kb",
        type=int,  # Целочисленное значение
        default=0,  # 0 = без ограничения
        help="Пропускать .py файлы размером больше указанного значения в КБ (0 = без ограничения)",
    )

    # Парсинг и возврат аргументов
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    """
    Основная функция для запуска анализатора неиспользуемого кода.
    Аргументы:
        argv: Опциональный список аргументов командной строки.
              Если None, используются sys.argv.
    Возвращает:
        int: Код возврата:
            0 - успешное выполнение
            2 - ошибка при анализе
    Выполняет:
        1. Парсинг аргументов командной строки
        2. Инициализацию анализатора проекта
        3. Запуск анализа и сохранение отчета
        4. Обработку возможных ошибок
    """
    # Парсим аргументы командной строки
    args = parse_args(argv)

    # Создаем анализатор проекта с заданными параметрами
    analyzer = ProjectAnalyzer(
        root_path=args.root,  # Корневая директория проекта
        exclude_patterns=args.exclude or [],  # Шаблоны исключения
        ignore_names_regex=args.ignore_names,  # Регулярка для игнорируемых имен
        ignore_private=args.ignore_private,  # Флаг игнорирования приватных членов
        include_methods=args.include_methods,  # Флаг включения методов классов
        max_file_size_kb=args.max_file_size_kb,  # Макс. размер файла для анализа
    )

    try:
        # Запускаем анализ и сохраняем отчет
        analyzer.run(output_path=args.output)
    except Exception as e:
        # В случае ошибки выводим сообщение и возвращаем код 2
        sys.stderr.write(f"Ошибка: {e}\n")
        return 2

    # Выводим путь к созданному отчету
    print(f"Отчет сохранен в: {os.path.abspath(args.output)}")
    # Возвращаем код успешного выполнения
    return 0


if __name__ == "__main__":
    """
        Стандартная проверка для точки входа Python-скрипта.
        Выполняется только при прямом запуске файла, а не при импорте.

        Использует SystemExit для корректного завершения программы
        с передачей кода возврата из функции main().
    """
    raise SystemExit(main())