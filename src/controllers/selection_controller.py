#selection_controller.py
from PySide6.QtCore import QObject, Signal, Qt, QModelIndex
from typing import Optional

from parsers.content_cache import ContentCache
from tests.managers.working_with_cache import print_all_cache_entries

class TreeSelectionController(QObject):
    """
    Контроллер для обработки выделения элементов в дереве.
    Получает контент из кэша или модели.
    """

    # Основные сигналы
    content_for_sidepanel = Signal(str, str, str)  # content_type, content, path_file      запрашиваемый данные
    content_for_editor = Signal(str, str, str, dict) # type, element_content, path, element_info
    selection_changed = Signal(dict)  # metadata: {type, name, path, has_content}                 выбранный параметр изменен
    error_occurred = Signal(str)  # error_message                                                 произошла ошибка
    content_for_element = Signal(str, str, str, dict)  # type, element_content, path, element_info

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

    def _handle_selection(self, index: QModelIndex) -> None:
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

            parent_item = getattr(item, 'parent_item', None)    # Получаем родителя
            if (parent_item and
                    hasattr(parent_item, 'item_data') and
                    len(parent_item.item_data) > 2):
                print(f'😈метод _get_file_path_for_item() : {parent_item.item_data}')
                print(f' parent_item.item_data[2]: {parent_item.item_data[2]}')
                return parent_item.item_data[2]

        # Для file и других типов используем стандартную логику
        current_item = item
        while current_item:
            if (hasattr(current_item, 'item_data') and
                    len(current_item.item_data) > 1 and
                    current_item.item_data[1] in ['file'] and
                    len(current_item.item_data) > 2):
                print(f'😅 метод _get_file_path_for_item() : {current_item.item_data}')
                print(f' current_item.item_data[2]: {current_item.item_data[2]}')
                return current_item.item_data[2]

            current_item = getattr(current_item, 'parent_item', None)

        return None
    def _get_file_path_for_item_ex(self, item: object) -> Optional[str]:
        """Рекурсивно ищет путь к файлу через цепочку родителей"""
        # TODO - мертвый код
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
        # TODO - мертвый код
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
    def _process_content(self, metadata: dict, item: object, source_name: str) -> None:
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
                template_context = self.get_template_context()
                self.content_for_editor.emit(metadata['type'], content, metadata.get('path', ''), template_context)

        except Exception as e:
            self.error_occurred.emit(f"Ошибка обработки контента: {str(e)}")
    def get_template_context(self, tab_widget = None):
        dict_selection_info = self.get_selection_info(tab_widget)
        template_name = dict_selection_info['type']
        file_path = dict_selection_info['path']
        parent_path = dict_selection_info['parent_name']
        template_id = f"{file_path}::{parent_path}::{template_name}"
        template_context = {'file_path': file_path, 'template_id': template_id,
                            'original_structure': self.content_cache.get('file_path'),
                            'element_path': self._build_element_path(dict_selection_info)}

        return template_context

    def _extract_element_content(self, metadata, item):
        """Извлекает контент только выбранного элемента"""
        file_path = self._get_file_path_for_item(item)
        if not file_path or not self.content_cache:
            return None

        # Получаем полную структуру из кэша
        full_data = self.content_cache.get(file_path)
        if not full_data:
            return None

        # Находим конкретный элемент в структуре
        target_element = self._find_element_in_structure(
            full_data,
            metadata['name'],
            metadata['type']
        )

        return target_element.get('content', '') if target_element else ''

    def _extract_content_Вопрос(self, metadata: dict, item: object) -> Optional[str]:
        """Извлекает контент из различных источников"""
        print(f'item.item_data: {item.item_data}')
        # 1. Пробуем из данных элемента
        if len(item.item_data) > 0:
            print(f'🤓☝️ 1. Пробуем из данных элемента через метод _extract_content(): {item.item_data}')

            return item.item_data[2]

        # 2. Контент не найден
        return None
    def _extract_content(self, metadata: dict, item: object) -> Optional[str]:
        """Извлекает контент из различных источников"""
        print(f'item.item_data: {item.item_data}')
        # 1. Пробуем из данных элемента
        if len(item.item_data) > 2 and item.item_data[2]:
            print(f'🤓☝️ 1. Пробуем из данных элемента через метод _extract_content(): {item.item_data}')

            return item.item_data[2]

        # 2. Пробуем из кэша (если есть путь)
        elif self.content_cache and metadata.get('path'):
            cached_data = self.content_cache.get(metadata['path'])
            print(f'🤭 2. Пробуем из кэша (если есть путь) через метод _extract_content(): {cached_data}')

            if cached_data:
                return cached_data.get('content', '') if isinstance(cached_data, dict) else str(cached_data)

        # 3. Контент не найден
        return None


    def get_selection_info(self, tab_widget) -> dict | None:
        """Получает подробную информацию о текущем выделенном элементе"""
        if not tab_widget:
            print("DEBUG: Виджет вкладок не установлен")
            return None

        current_index = tab_widget.currentIndex()
        if current_index < 0:
            return None

        tab_name = tab_widget.tabText(current_index)
        tree_view = tab_widget.widget(current_index)

        if not tree_view:
            print(f"DEBUG: Не найден tree_view для вкладки '{tab_name}'")
            return None

        if not tree_view.currentIndex().isValid():
            print(f"DEBUG: В дереве вкладки '{tab_name}' нет выделенного элемента")
            return None

        index = tree_view.currentIndex()
        parent_index = index.parent()
        model = tree_view.model()

        if not model:
            print(f"DEBUG: Модель не установлена для tree_view вкладки '{tab_name}'")
            return None

        # Получаем путь к файлу
        file_path = None
        if model.get_item_type(index) in ['file', 'markdown']:
            file_path = model.get_item_path(index)
        else:
            file_root_info = self.get_file_root_from_selection(index)
            if file_root_info:
                file_path = file_root_info['path']

        return {
            'type': model.get_item_type(index),   # тип элемента
            'path': file_path,                    # путь к элементу
            'level': model.get_item_level(index), # уровень вложенности элемента в иерархии модели
            'name': model.data(index, Qt.DisplayRole), # имя модели, где находится элемент
            'model': model,    # модель, где находится элемент
            'index': index, # индекс выбранного элемента
            'parent_index': parent_index,  # индекс родителя
            'parent_name': model.data(parent_index, Qt.DisplayRole), #  имя родителя
            'parent_type': model.get_item_type(parent_index) if parent_index.isValid() else 'root',   # Тип родителя
            'tab_name': tab_name,   # Имя вкладки
            'tree_view': tree_view  # дерево
        }

    def get_file_root_from_selection(self, index):
        """Находит корневой элемент файла по выбранному индексу"""
        current_index = index
        model = index.model()

        while current_index.isValid():
            item_path = model.get_item_path(current_index)
            if item_path:
                return {
                    'index': current_index,
                    'element': current_index.internalPointer(),
                    'type': model.get_item_type(current_index),
                    'name': model.data(current_index, Qt.DisplayRole),
                    'path': item_path
                }
            current_index = current_index.parent()
        return None

    def _build_element_path(self, selection_info):
        """Строит путь к элементу в структуре ['root', 'parent', 'element']"""
        path = ['root']

        # Используем существующую логику поиска родительской иерархии
        current = selection_info['index']
        while current.isValid():
            name = current.data(Qt.DisplayRole)
            if name:
                path.insert(1, name)  # Добавляем в начало
            current = current.parent()

        return path