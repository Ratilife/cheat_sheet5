'''
Этот модуль сырой и будет менятся

'''
import os
from enum import Enum
from PySide6.QtCore import QObject, Signal, QThreadPool, QRunnable, Q_ARG, QMetaObject
from PySide6.QtGui import Qt

from parsers.file_parser_service import FileParserService
from parsers.content_cache import ContentCache


class Priority(Enum):
    """
        Приоритеты задач парсинга файлов.

        Attributes:
            VISIBLE: Максимальный приоритет - файлы, видимые пользователю в данный момент
            PRELOAD: Средний приоритет - предзагрузка соседних элементов для быстрого доступа
            DEEP: Низкий приоритет - фоновый парсинг остальных файлов
    """
    VISIBLE = 0    # То, что видно прямо сейчас (макс. приоритет)
    PRELOAD = 1    # Предзагрузка соседних элементов
    DEEP = 2       # Остальные файлы (низкий приоритет)

class ParserTask(QRunnable):
    """
    Задача для фонового выполнения парсинга файла.

    Наследуется от QRunnable для выполнения в пуле потоков Qt.
    Каждый экземпляр представляет собой задачу парсинга одного файла.
    """
    finished = Signal(str, dict)  # Добавить сигнал
    def __init__(self,file_path: str, priority: Priority, parser_service: FileParserService):
        """
                Инициализирует задачу парсинга.

                Args:
                    file_path: Полный путь к файлу для парсинга
                    priority: Приоритет задачи из перечисления Priority
                    parser_service: Сервис для выполнения парсинга файлов
        """
        super().__init__()
        self.file_path = file_path
        self.priority = priority
        self.parser_service = parser_service
        self.setAutoDelete(True)  # Автоматическое удаление после выполнения

    def run(self):
        """
        Выполняется в фоновом потоке.

        Основной метод, который вызывается пулом потоков. Выполняет парсинг файла
        и отправляет результат в главный поток через механизм сигналов Qt.

        Raises:
            Exception: Любые исключения при парсинге логируются, но не пробрасываются дальше
        """
        try:
            # 1. Логирование (для отладки)
            print(f"Парсим файл: {self.file_path} (приоритет: {self.priority.name})")

            # 2. САМАЯ ВАЖНАЯ ЧАСТЬ: Синхронный вызов парсера
            # Этот метод будет выполняться в фоновом потоке и может блокировать его надолго.
            # Это нормально, ведь ради этого мы и создали отдельный поток!
            parsed_data = self.parser_service.parse_and_get_type(self.file_path)

            # 3. Передача результата в главный поток
            # Мы не можем обновлять GUI из фонового потока.
            # Поэтому используем invokeMethod для безопасного вызова слота в главном потоке.
            self.finished.emit(self.file_path, parsed_data)  # Использовать сигнал

        except Exception as e:
            # 4. Обработка ошибок
            # Ловим все исключения, чтобы аварийно не завершать поток.
            print(f"Ошибка парсинга {self.file_path}: {str(e)}")


class BackgroundParser(QObject):
    """
    Менеджер фонового парсинга файлов с поддержкой приоритетов.

    Управляет очередью задач парсинга, распределяет их по потокам и обеспечивает
    безопасную коммуникацию между фоновыми потоками и главным потоком GUI.

    Attributes:
        _instance: Единственный экземпляр класса (реализация Singleton)
    """

    # Сигналы
    task_started = Signal(str, Priority)  # Начало парсинга файла
    task_finished = Signal(str, dict)  # Успешный парсинг (file_path, data)
    task_failed = Signal(str, str)  # Ошибка парсинга (file_path, error)
    queue_empty = Signal()  # Все задачи выполнены

    _instance = None

    @classmethod
    def instance(cls, parser_service=None, content_cache=None):
        """
                Возвращает единственный экземпляр класса (Singleton pattern).

                Returns:
                    BackgroundParser: Единственный экземпляр менеджера парсинга
        """
        if cls._instance is None:
            if parser_service is None or content_cache is None:
                raise ValueError("При первом вызове instance() необходимо передать parser_service и content_cache")
            cls._instance = BackgroundParser(parser_service, content_cache)
        return cls._instance

    def __init__(self, parser_service: FileParserService, content_cache: ContentCache):
        """
                Инициализирует менеджер фонового парсинга.

                Args:
                    parser_service: Сервис для парсинга различных типов файлов
                    content_cache: Кэш для хранения результатов парсинга
        """
        super().__init__()
        self.parser_service = parser_service
        self.content_cache = content_cache

        # Настройка пула потоков
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(2)  # Максимум 2 одновременных задачи

        # Очередь задач по приоритетам
        self.task_queue = {priority: [] for priority in Priority}
        self.active_tasks = 0

    def add_task(self, file_path: str, priority: Priority = Priority.PRELOAD):
        """
            Добавляет файл в очередь на парсинг.

            Проверяет существование файла и создает задачу для фонового выполнения.
            Автоматически запускает обработку очереди после добавления задачи.

            Args:
                file_path: Путь к файлу для парсинга
                priority: Приоритет задачи (по умолчанию PRELOAD)
        """
        if not file_path or not os.path.exists(file_path):
            return

        task = ParserTask(file_path, priority, self.parser_service)
        task.finished.connect(self.on_task_finished)
        self.task_queue[priority].append(task)
        self._process_queue()

    def add_tasks(self, file_paths: list, priority: Priority = Priority.PRELOAD):
        """
            Добавляет несколько файлов в очередь парсинга.

            Args:
                file_paths: Список путей к файлам для парсинга
                priority: Приоритет для всех задач (по умолчанию PRELOAD)
        """
        # TODO 🚧 В разработке: 24.08.2025 - мертвый код метод add_tasks,
        for file_path in file_paths:
            self.add_task(file_path, priority)

    def _process_queue(self):
        """
            Обрабатывает очередь задач и запускает доступные задачи.

            Проверяет доступность потоков и выбирает задачи согласно приоритету
            (от высшего к низшему). Запускает не более maxThreadCount() задач одновременно.
        """
        if self.active_tasks >= self.thread_pool.maxThreadCount():
            return  # Достигнут лимит одновременных задач

        # Ищем задачи по приоритету (от высокого к низкому)
        for priority in [Priority.VISIBLE, Priority.PRELOAD, Priority.DEEP]:
            if self.task_queue[priority]:
                task = self.task_queue[priority].pop(0)
                self.active_tasks += 1
                self.task_started.emit(task.file_path, task.priority)
                self.thread_pool.start(task)
                break
        else:
            self.queue_empty.emit()  # Очередь пуста

    def on_task_finished(self, file_path: str, parsed_data: dict):
        """
            Обработчик завершения задачи парсинга.

            Вызывается из главного потока после завершения парсинга в фоновом потоке.
            Сохраняет результаты в кэш, уменьшает счетчик активных задач и запускает
            обработку следующей задачи в очереди.

            Args:
                file_path: Путь к обработанному файлу
                parsed_data: Результаты парсинга в виде словаря
        """
        self.active_tasks -= 1

        # Сохраняем результат в кэш
        self.content_cache.set(file_path, parsed_data)

        # Уведомляем о завершении
        self.task_finished.emit(file_path, parsed_data)

        # Обрабатываем следующую задачу
        self._process_queue()

    def clear_queue(self, priority: Priority = None):
        """
                Очищает очередь задач парсинга.

                Args:
                    priority: Если указан, очищает только очередь указанного приоритета.
                             Если None, очищает все очереди всех приоритетов.
        """
        if priority:
            self.task_queue[priority].clear()
        else:
            for queue in self.task_queue.values():
                queue.clear()

    def get_queue_stats(self) -> dict:
        """
            Возвращает статистику по текущему состоянию очереди задач.

            Returns:
                dict: Словарь со статистикой, содержащий:
                    - active_tasks: количество выполняющихся задач
                    - queued_tasks: словарь с количеством задач в очереди по приоритетам
                    - max_threads: максимальное количество одновременных потоков
        """
        return {
            "active_tasks": self.active_tasks,
            "queued_tasks": {p.name: len(q) for p, q in self.task_queue.items()},
            "max_threads": self.thread_pool.maxThreadCount()
        }