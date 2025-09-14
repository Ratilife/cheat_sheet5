
from PySide6.QtCore import QObject, Signal, Qt
from typing import Optional


class TreeSelectionController(QObject):
    """
    Контроллер для обработки выделения элементов в дереве.
    Получает контент из кэша или модели.
    """

    # Основные сигналы
    content_for_sidepanel = Signal(str, str, str)  # content_type, content, path_file      запрашиваемый данные
    content_for_editor = Signal(str, str, str)
    selection_changed = Signal(dict)  # metadata: {type, name, path, has_content}                 выбранный параметр изменен
    error_occurred = Signal(str)  # error_message                                                 произошла ошибка

    def __init__(self, content_cache, parent=None):
        super().__init__(parent)
        self.content_cache = content_cache
        self.current_source = ''  # Добавляем отслеживание источника
        self._connections = {}  # Словарь для хранения соединений

    def connect_tree_view(self, tree_view, source_name):
        """Подключает контроллер к дереву"""
        self.current_source = source_name  # Запоминаем источник
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
                'path': self._get_file_path_for_item(item),  # Ищем путь через объект item
                'has_selection': True
            }

            self.selection_changed.emit(metadata)      # ✅ Сигнал о изменении выделения

            # Обрабатываем контент для поддерживаемых типов
            if metadata['type'] in ['markdown', 'template']:
                self._process_content(metadata, item, self.current_source )  # ✅ Запуск обработки контента

        except Exception as e:
            self.error_occurred.emit(f"Selection error: {str(e)}")

    def _get_file_path_for_item(self, item):
        """Рекурсивно ищет путь к файлу через цепочку родителей"""
        # Для markdown всегда берем путь из родительского элемента
        if (hasattr(item, 'item_data') and
                len(item.item_data) > 1 and
                item.item_data[1] == 'markdown'):

            parent_item = getattr(item, 'parent_item', None)
            if (parent_item and
                    hasattr(parent_item, 'item_data') and
                    len(parent_item.item_data) > 2):
                return parent_item.item_data[2]

        # Для file и других типов используем стандартную логику
        current_item = item
        while current_item:
            if (hasattr(current_item, 'item_data') and
                    len(current_item.item_data) > 1 and
                    current_item.item_data[1] in ['file'] and
                    len(current_item.item_data) > 2):
                return current_item.item_data[2]

            current_item = getattr(current_item, 'parent_item', None)

        return None
    def _get_file_path_for_item_ex(self, item):
        """Рекурсивно ищет путь к файлу через цепочку родителей"""
        current_item = item

        # Сначала проверяем сам элемент
        if (hasattr(current_item, 'item_data') and
                len(current_item.item_data) > 2 and
                current_item.item_data[2] and  # Проверяем, что путь не пустой
                isinstance(current_item.item_data[2], str) and
                len(current_item.item_data[2].strip()) > 0):
            return current_item.item_data[2]  # Возвращаем путь

        # Если у текущего элемента нет пути, поднимаемся по иерархии
        current_item = getattr(current_item, 'parent_item', None)
        while current_item:
            # Проверяем, есть ли у родительского элемента путь
            if (hasattr(current_item, 'item_data') and
                    len(current_item.item_data) > 2 and
                    current_item.item_data[2] and  # Проверяем, что путь не пустой
                    isinstance(current_item.item_data[2], str) and
                    len(current_item.item_data[2].strip()) > 0):
                return current_item.item_data[2]  # Возвращаем путь

            # Переходим к следующему родителю
            current_item = getattr(current_item, 'parent_item', None)

        return None

    def _get_file_path_for_item_old(self, item):
        """Рекурсивно ищет путь к файлу через цепочку родителей"""
        current_item = item

        # Поднимаемся по иерархии пока не найдем файл или markdown
        while current_item:
            # Проверяем, является ли текущий элемент файлом или markdown
            if (hasattr(current_item, 'item_data') and
                    len(current_item.item_data) > 1 and
                    current_item.item_data[1] in ['file', 'markdown'] and
                    len(current_item.item_data) > 2):
                return current_item.item_data[2]  # Возвращаем путь

            # Переходим к родителю
            current_item = getattr(current_item, 'parent_item', None)

        return None
    def _process_content(self, metadata, item, source_name):
        """
        Получает и отправляет контент с явным указанием источника

        Args:
            metadata: Метаданные элемента {type, name, path, has_selection}
            item: Объект элемента дерева
            source_name: Идентификатор источника ('sidepanel', 'editor')
        """
        # Валидация входных параметров
        if not metadata or not isinstance(metadata, dict):
            self.error_occurred.emit("Неверные метаданные элемента")
            return

        if source_name is None:
            self.error_occurred.emit("Не указан источник для обработки контента")
            return

        try:
            # 1. Извлекаем контент
            content = self._extract_content(metadata, item)
            if content is None:
                self.error_occurred.emit(f"Контент недоступен для {metadata['name']}")
                return

            # 2. Валидация источника
            if source_name not in ['sidepanel', 'editor']:
                self.error_occurred.emit(f"Неизвестный источник: {source_name}")
                return

            # 3. Отправка в соответствующий сигнал
            if source_name == "sidepanel":
                self.content_for_sidepanel.emit(metadata['type'], content, metadata.get('path', ''))
            elif source_name == "editor":
                self.content_for_editor.emit(metadata['type'], content, metadata.get('path', ''))

        except Exception as e:
            self.error_occurred.emit(f"Ошибка обработки контента: {str(e)}")

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