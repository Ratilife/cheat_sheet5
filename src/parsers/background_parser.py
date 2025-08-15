from enum import Enum
from PySide6.QtCore import QObject, Signal, QThreadPool,QRunnable
from PySide6.QtGui import Qt

from parsers.file_parser_service import FileParserService


class Priority(Enum):
    VISIBLE = 0    # То, что видно прямо сейчас (макс. приоритет)
    PRELOAD = 1    # Предзагрузка соседних элементов
    DEEP = 2       # Остальные файлы (низкий приоритет)

class ParserTask(QRunnable):
    """Задача для фонового выполнения"""
    def __init__(self, file_path, priority):
        super().__init__()
        self.file_path = file_path
        self.priority = priority

    def run(self):
        try:
            data = FileParserService().parse_full_content(self.file_path)  # TODO 15.08.2025 parse_full_content нет этого метода в классе FileParserService
            BackgroundParser.instance().task_finished.emit(self.file_path, data)
        except Exception as e:
            print(f"Ошибка парсинга {self.file_path}: {str(e)}")

class BackgroundParser(QObject):
    task_finished = Signal(str, dict)  # Сигнал с результатом

    def __init__(self):
        super().__init__()
        self.thread_pool = QThreadPool.globalInstance()
        self.thread_pool.setMaxThreadCount(2)  # Не более 2 потоков
        self.task_queue = {
            Priority.VISIBLE: [],
            Priority.PRELOAD: [],
            Priority.DEEP: []
        }

    def add_task(self, file_path, priority):
        """Добавляет задачу в очередь"""
        task = ParserTask(file_path, priority)
        self.task_queue[priority].append(task)
        self._process_queue()

    def _process_queue(self):
        """Запускает задачи из очереди с учетом приоритетов"""
        for priority in Priority:
            if self.task_queue[priority]:
                task = self.task_queue[priority].pop(0)
                self.thread_pool.start(task)
                break