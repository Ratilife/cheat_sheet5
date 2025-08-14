from enum import Enum
from PySide6.QtCore import QObject, Signal
class Priority(Enum):
    VISIBLE = 0    # То, что видно прямо сейчас (макс. приоритет)
    PRELOAD = 1    # Предзагрузка соседних элементов
    DEEP = 2       # Остальные файлы (низкий приоритет)

class BackgroundParser(QObject):
    task_finished = Signal(str, dict)  # Сигнал с результатом

    def __init__(self, file_path, priority):
        super().__init__()
        self.file_path = file_path
        self.priority = priority
