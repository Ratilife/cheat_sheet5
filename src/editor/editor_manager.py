# Менеджер редакторов (координатор)

from PySide6.QtCore import QObject, Signal
from .editor_factory import EditorFactory


class EditorManager(QObject):
    """Менеджер для управления редакторами и их состоянием"""

    editor_changed = Signal(object)  # Сигнал при смене редактора
    content_modified = Signal(bool)  # Сигнал при изменении содержимого