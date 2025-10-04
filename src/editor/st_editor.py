# Редактор для .st файлов
from typing import Optional
from PySide6.QtWidgets import QWidget

from observers.file_watcher import FileWatcher
from src.editor.base_editor import BaseFileEditor
from PySide6.QtCore import Signal
class STEditor(BaseFileEditor):
    # Новые сигналы для работы с FileWatcher
    external_update_detected = Signal(str)  # Обнаружено внешнее изменение
    file_conflict_detected = Signal(str, str)  # Конфликт изменений (наш, внешний)
    file_became_readonly = Signal(str)  # Файл стал доступен только для чтения
    watching_status_changed = Signal(bool)  # Изменение статуса отслеживания

    def __init__(self, parent: Optional[QWidget] = None, file_watcher: Optional[FileWatcher] = None):
        super().__init__(parent=parent)
        # Сохраняем переданный FileWatcher или создаем новый
        self._file_watcher = file_watcher or FileWatcher()