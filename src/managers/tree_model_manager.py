
from PySide6.QtCore import QAbstractItemModel, QModelIndex, QObject
from src.models.st_md_file_tree_model import STMDFileTreeModel
from src.models.st_md_file_tree_item import STMDFileTreeItem

import os
class TreeModelManager(QObject):
    """
      Фасад для работы с моделью дерева файлов. Инкапсулирует:
      - Добавление/удаление элементов
      - Парсинг файлов
      - Взаимодействие с DeleteManager
      """

    def __init__(self, parser_service):
        # TODO 🚧 В разработке: 12.07.2025
        super().__init__()
        self.parser_service = parser_service
        self.tab_models = {}  # Кэш моделей по именам вкладок

    def create_tree_model(self, file_paths: list) -> QAbstractItemModel:
        """Создает модель дерева для списка файлов"""
        # TODO 🚧 В разработке: 13.07.2025
        # 1. Создаем корневой элемент
        root_item = STMDFileTreeItem(["Root", "folder"])

        # 2. Создаем модель
        model = STMDFileTreeModel(root_item)

        # 3. Добавляем файлы в модель
        for file_path in file_paths:
            self._add_file_to_model(model, file_path)

        return model

    def create_models_from_tabs(self, tab_data: dict) -> dict:
        """
        Создает модели деревьев для всех вкладок
        Args:
            tab_data (dict): Словарь {имя_вкладки: [список_файлов]}
        Returns:
            dict: Созданные модели {имя_вкладки: модель}
        """
        # TODO 🚧 В разработке: 13.07.2025
        models = {}
        for tab_name, file_paths in tab_data.items():
            models[tab_name] = self.create_tree_model(file_paths)
        self.tab_models.update(models)
        return models

    def get_model(self, tab_name: str) -> QAbstractItemModel:
        """
        Возвращает модель для указанной вкладки
        Args:
            tab_name (str): Имя вкладки
        Returns:
            QAbstractItemModel: Модель дерева или None если не найдена
        """
        # TODO 🚧 В разработке: 13.07.2025 - мертвый код
        return self._models_cache.get(tab_name)

    def refresh_model(self, tab_name: str, new_file_paths: list) -> bool:
        """
        Обновляет модель для вкладки
        Args:
            tab_name (str): Имя вкладки
            new_file_paths (list): Новый список файлов
        Returns:
            bool: True если обновление прошло успешно
        """
        # TODO 🚧 В разработке: 13.07.2025 - мертвый код
        if tab_name in self._models_cache:
            self._models_cache[tab_name] = self._create_single_model(new_file_paths)
            return True
        return False

    def _create_single_model(self, file_paths: list) -> STMDFileTreeModel:
        """
        Создает одну модель дерева для списка файлов
        Args:
            file_paths (list): Список путей к файлам
        Returns:
            STMDFileTreeModel: Готовая модель дерева
        """
        # TODO 🚧 В разработке: 13.07.2025

        # 1. Создаем корневой элемент
        root_item = STMDFileTreeItem(["Root", "folder"])
        model = STMDFileTreeModel(root_item)

        # 2. Добавляем файлы в модель
        for file_path in file_paths:
            if os.path.exists(file_path):
                self._add_file_to_model(model, file_path)

        return model

    def _add_file_to_model(self, model: STMDFileTreeModel, file_path: str):
        """
        Добавляет файл в модель дерева
        Args:
            model (STMDFileTreeModel): Целевая модель
            file_path (str): Путь к файлу
        """
        # TODO 🚧 В разработке: 13.07.2025
        try:
            # 1. Парсим файл
            file_type, parsed_data = self.parser_service.parse_and_get_type(file_path)
            file_name = os.path.basename(file_path)

            # 2. Создаем элемент для файла
            file_item = STMDFileTreeItem(
                [file_name, file_type, file_path],
                model.rootItem
            )

            # 3. Добавляем структуру файла
            if file_type == "markdown":
                self._add_md_structure(file_item, parsed_data)
            elif file_type == "file":  # ST-файл
                self._add_st_structure(file_item, parsed_data)

            # 4. Добавляем в модель
            model.beginInsertRows(QModelIndex(), model.rowCount(), model.rowCount())
            model.rootItem.appendChild(file_item)
            model.endInsertRows()

        except Exception as e:
            print(f"Ошибка добавления файла {file_path}: {str(e)}")

    def _add_md_structure(self, parent_item: STMDFileTreeItem, parsed_data: dict):
        """Добавляет структуру Markdown-файла"""
        for section in parsed_data.get('structure', []):
            section_item = STMDFileTreeItem(
                [section['name'], 'section', section.get('content', '')],
                parent_item
            )
            parent_item.appendChild(section_item)

    def _add_st_structure(self, parent_item: STMDFileTreeItem, parsed_data: dict):
        """Добавляет структуру ST-файла"""
        for item in parsed_data.get('structure', []):
            self._add_st_item(parent_item, item)

    def _add_st_item(self, parent_item: STMDFileTreeItem, item_data: dict):
        """Рекурсивно добавляет элементы ST-структуры"""
        item = STMDFileTreeItem(
            [item_data['name'], item_data['type']],
            parent_item
        )

        if item_data['type'] == 'folder' and 'children' in item_data:
            for child in item_data['children']:
                self._add_st_item(item, child)

        parent_item.appendChild(item)