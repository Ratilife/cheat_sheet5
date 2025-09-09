# Менеджер редакторов (координатор)
# src/editor/editor_manager.py
from PySide6.QtCore import QObject, Signal
from .editor_factory import EditorFactory
from src.parsers.content_cache import ContentCache
from src.parsers.metadata_cache import MetadataCache
from src.parsers.background_parser import BackgroundParser,Priority

class EditorManager(QObject):
    """Менеджер для управления редакторами и их состоянием"""

    editor_ready = Signal(object, str)  # Сигнал: редактор, file_path  редактор готов
    loading_started = Signal(str)  # Сигнал: file_path                        загрузка началась
    loading_finished = Signal(str)  # Сигнал: file_path                       загрузка завершена

    def __init__(self):
        super().__init__()
        self.editor_factory = EditorFactory()
        self.content_cache = ContentCache()
        self.metadata_cache = MetadataCache()
        self.current_editor = None
        self.current_file_path = None

    def open_file(self, file_path: str, parent_widget=None):
        """Основной метод открытия файла"""
        self.loading_started.emit(file_path)
        self.current_file_path = file_path

        # 1. Проверяем кэш контента
        cached_content = self.content_cache.get(file_path)
        if cached_content:
            self._setup_editor_from_cache(file_path, cached_content, parent_widget)
        else:
            self._load_and_setup_editor(file_path, parent_widget)

    def _setup_editor_from_cache(self, file_path: str, content: dict, parent_widget):
        """Быстрая установка редактора из кэша"""
        editor = self.editor_factory.create_editor(file_path, parent_widget)
        editor.set_content(content)
        self.current_editor = editor
        self.editor_ready.emit(editor, file_path)
        self.loading_finished.emit(file_path)

    def _load_and_setup_editor(self, file_path: str, parent_widget):
        """Загрузка и настройка редактора с парсингом"""
        # Создаем редактор сразу для мгновенного отклика
        editor = self.editor_factory.create_editor(file_path, parent_widget)
        self.current_editor = editor
        self.editor_ready.emit(editor, file_path)

        # Показываем базовые метаданные из metadata_cache
        metadata = self.metadata_cache.get(file_path)
        if metadata:
            self._show_metadata_preview(editor, metadata)

        # Запускаем фоновый парсинг
        self._parse_in_background(file_path, editor)

    def _show_metadata_preview(self, editor, metadata: dict):
        """Показываем превью из метаданных"""
        preview_content = {
            'structure': metadata.get('structure', []),
            'root_name': metadata.get('root_name', '')
        }
        editor.set_content(preview_content)

    def _parse_in_background(self, file_path: str, editor):
        """Фоновый парсинг файла"""
        # Здесь интегрируемся с BackgroundParser
        self.background_parser.add_task(file_path, Priority.VISIBLE)
        # Например, через сигналы:
        # background_parser.task_finished.connect(self._on_parse_finished)
        pass

    def _on_parse_finished(self, file_path: str, parsed_data: dict):
        """Обработчик завершения парсинга"""
        if file_path == self.current_file_path and self.current_editor:
            self.current_editor.set_content(parsed_data)
            self.loading_finished.emit(file_path)