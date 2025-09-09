# Редактор для .md файлов
from PySide6.QtCore import Signal, QTimer
from PySide6.QtWidgets import QWidget, QVBoxLayout
from typing import Optional
from editor.base_editor import BaseFileEditor
from observers.file_watcher import FileWatcher
from widgets.markdown_converter import MarkdownConverter
from widgets.markdown_viewer_widget import MarkdownViewer


class MarkdownEditor(BaseFileEditor):
    """
       Редактор для Markdown-файлов с поддержкой отслеживания внешних изменений.
       Наследует функциональность BaseFileEditor и добавляет специфичную для Markdown.
    """

    # Новые сигналы для работы с FileWatcher
    external_update_detected = Signal(str)          # Обнаружено внешнее изменение
    file_conflict_detected = Signal(str, str)       # Конфликт изменений (наш, внешний)
    file_became_readonly = Signal(str)              # Файл стал доступен только для чтения
    watching_status_changed = Signal(bool)          # Изменение статуса отслеживания
    def __init__(self, parent: Optional[QWidget] = None, file_watcher: Optional[FileWatcher] = None):
        """
            Инициализация редактора Markdown.

            Args:
                parent: Родительский виджет
                file_watcher: Опциональный FileWatcher для отслеживания изменений файлов
        """
        # Сохраняем переданный FileWatcher или создаем новый
        self._file_watcher = file_watcher or FileWatcher()

        # Создаем viewer для отображения Markdown (композиция!)
        self._viewer = MarkdownViewer(parent=self)

        # Флаг для временного отключения отслеживания
        self._watching_paused = False

        # Таймер для дебаунсинга множественных изменений
        self._debounce_timer = QTimer()
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.setInterval(300)  # 300ms задержка

        # Путь к файлу, который временно изменяется
        self._pending_external_update: Optional[str] = None

        # Инициализируем UI и соединения
        self._init_ui()
        self._setup_connections()

        # Устанавливаем начальное состояние
        self._update_watching_state(False)

        self.converter = MarkdownConverter()

    def _init_ui(self) -> None:
        """Инициализация пользовательского интерфейса"""
        # Основной layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Добавляем viewer в layout
        layout.addWidget(self._viewer.get_editor_widget())

        # Устанавливаем layout
        self.setLayout(layout)

    def _setup_connections(self) -> None:
        """Настройка сигналов и соединений"""
        # Подключаем таймер дебаунсинга
        self._debounce_timer.timeout.connect(self._handle_debounced_update)

        # Подключаем сигналы FileWatcher
        self._file_watcher.file_updated.connect(self._on_external_file_update)
        self._file_watcher.file_deleted.connect(self._on_external_file_deleted)
        self._file_watcher.dir_changed.connect(self._on_directory_changed)

        # Подключаем сигналы viewer к нашим обработчикам
        self._viewer.text_changed.connect(self._on_viewer_text_changed)

    def _update_watching_state(self, enabled: bool) -> None:
        """
        Обновляет состояние отслеживания и испускает сигнал
        Args:
            enabled: Включено ли отслеживание
        """
        self._watching_enabled = enabled
        self.watching_status_changed.emit(enabled)

    def get_editor_widget(self) -> QWidget:
        """
        Возвращает виджет редактора для встраивания в UI.
        Переопределяем метод базового класса.

        Returns:
            QWidget: Виджет редактора
        """
        return self