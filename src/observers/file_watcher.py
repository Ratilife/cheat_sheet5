import os
from PySide6.QtCore import QFileSystemWatcher, Signal, QObject

class FileWatcher(QObject):
    # TODO 🚧 В разработке: 08.08.2025
        # 🏆task: Создание боковой панели;
        # 🏆task: Открыть боковую панель из стартовой панели;
        # 🏆task: Работа с деревом:
    """Отслеживает изменения файлов и уведомляет подписчиков."""
    file_updated = Signal(str)  # Файл изменён (путь)
    file_deleted = Signal(str)  # Файл удалён (путь)
    directory_changed = Signal(str)  # Путь измененной директории

    def __init__(self):
        # TODO 🚧 В разработке: 08.08.2025
        super().__init__()
        self.watcher = QFileSystemWatcher
        self.watcher.fileChanged.connect(self._handle_file_change)

    def _handle_file_change(self, path: str) -> None:
        """Обрабатывает изменение файла."""
        # TODO 🚧 В разработке: 08.08.2025
        # Проверяет, существует ли указанный путь (файл или директория) в файловой системе
        if os.path.exists(path):
            # Если путь существует, генерирует (вызывает) сигнал/событие о том, что файл был обновлён
            self.file_updated.emit(path)
        else:
            # Если путь не существует (файл был удалён), генерирует (вызывает) сигнал/событие о том, что файл был удалён
            self.file_deleted.emit(path)