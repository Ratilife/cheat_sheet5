
from PySide6.QtCore import QObject, Signal, Qt
from typing import Optional


class TreeSelectionController(QObject):
    """
    Контроллер для обработки выделения элементов в дереве.
    Получает контент из кэша или модели.
    """

    # Основные сигналы
    content_requested = Signal(str, str)  # content_type, content           запрашиваемый данные
    selection_changed = Signal(dict)  # metadata: {type, name, path, has_content}  выбранный параметр изменен
    error_occurred = Signal(str)  # error_message                                  произошла ошибка

    def __init__(self, content_cache, parent=None):
        super().__init__(parent)
        self.content_cache = content_cache

    def connect_tree_view(self, tree_view):
        """Подключает контроллер к дереву"""
        if hasattr(tree_view, 'clicked'):
            tree_view.clicked.connect(self._handle_selection)
        else:
            self.error_occurred.emit(f"Древовидное представление не поддерживает клики: {type(tree_view)}")

    def _handle_selection(self, index):
        """Обрабатывает выделение элемента"""
        try:
            if not index.isValid():
                self.selection_changed.emit({'has_selection': False})
                return

            model = index.model()               # Получаем модель дерева
            item = index.internalPointer()      # Получаем объект элемента

            # Получаем метаданные
            metadata = {
                'type': model.data(index, Qt.UserRole + 2),  # 'markdown', 'template' и т.д.
                'name': model.data(index, Qt.DisplayRole),   # Имя файла/папки
                'path': model.data(index, Qt.UserRole + 3)   # Путь к файлу
                if hasattr(model, 'get_item_path') else None,
                'has_selection': True
            }

            self.selection_changed.emit(metadata)      # ✅ Сигнал о изменении выделения

            # Обрабатываем контент для поддерживаемых типов
            if metadata['type'] in ['markdown', 'template']:
                self._process_content(metadata, item)  # ✅ Запуск обработки контента

        except Exception as e:
            self.error_occurred.emit(f"Selection error: {str(e)}")

    def _process_content(self, metadata, item):
        """Получает и отправляет контент"""
        content = self._extract_content(metadata, item)
        if content is not None:
            self.content_requested.emit(metadata['type'], content)
        else:
            self.error_occurred.emit(f"Контент, недоступный для {metadata['name']}")

    def _extract_content(self, metadata, item):
        """Извлекает контент из различных источников"""
        # 1. Пробуем из данных элемента
        if len(item.item_data) > 2 and item.item_data[2]:
            return item.item_data[2]

        # 2. Пробуем из кэша (если есть путь)
        elif self.content_cache and metadata.get('path'):
            cached_data = self.content_cache.get(metadata['path'])
            if cached_data:
                return cached_data.get('content', '') if isinstance(cached_data, dict) else str(cached_data)

        # 3. Контент не найден
        return None