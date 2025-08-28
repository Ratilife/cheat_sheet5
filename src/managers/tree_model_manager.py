from PySide6.QtCore import QAbstractItemModel, QModelIndex, QObject, Signal
from src.models.st_md_file_tree_model import STMDFileTreeModel
from src.models.st_md_file_tree_item import STMDFileTreeItem
from src.parsers.metadata_cache import MetadataCache
from src.parsers.file_parser_service import FileParserService
from src.parsers.content_cache import ContentCache
class TreeModelManager(QObject):
    model_updated = Signal(str, str)  # tab_name, file_path
    def __init__(self, parser_service: FileParserService, metadata_cache: MetadataCache, content_cache:ContentCache):
        super().__init__()
        self.parser_service = parser_service
        self.metadata_cache = metadata_cache
        self.content_cache = content_cache

        self.tab_models = {}    # кэш моделей
        self.file_to_tabs = {}  # Отслеживаем, в каких вкладках какие файлы

    def build_model_for_tab(self, tab_name: str, file_paths: list[str]) -> STMDFileTreeModel:
        # ✅ Реализовано: 28.08.2025
        # Сохраняем связь файлов с вкладками
        for file_path in file_paths:
            if file_path not in self.file_to_tabs:
                self.file_to_tabs[file_path] = []
            if tab_name not in self.file_to_tabs[file_path]:
                self.file_to_tabs[file_path].append(tab_name)

        # Создаем модель
        model = STMDFileTreeModel(self.content_cache)

        for file_path in file_paths:
            full_data = self.content_cache.get(file_path)
            if full_data:
                model.add_file(file_path, full_data)
            else:
                metadata = self.metadata_cache.get(file_path)
                if not metadata:
                    metadata = self._parse_metadata(file_path)
                    self.metadata_cache.set(file_path, metadata,
                                            file_type=metadata.get('type'))
                model.add_file(file_path, metadata)

        self.tab_models[tab_name] = model
        return model

    def update_file_in_all_tabs(self, file_path: str):
        """Обновляет файл во всех вкладках, где он присутствует"""
        if file_path not in self.file_to_tabs:
            return False

        full_data = self.content_cache.get(file_path)
        if not full_data:
            return False

        updated = False
        for tab_name in self.file_to_tabs[file_path]:
            if self.update_model(tab_name, file_path):
                updated = True
                self.model_updated.emit(tab_name, file_path)

        return updated
    def _parse_metadata(self, file_path: str) -> dict:
        """Парсит метаданные файла (вызывает FileParserService)"""
        return self.parser_service.parse_metadata(file_path)

    def update_model(self, tab_name: str, file_path: str):
        """Обновляет модель при получении новых данных и возвращает успешность"""
        # TODO 🚧 В разработке: 28.08.2025
        if tab_name in self.tab_models:
            model = self.tab_models[tab_name]
            # Получаем полные данные из кэша
            full_data = self.content_cache.get(file_path)
            if full_data:
                return model.update_file_item(file_path, full_data)
        return False

    def refresh_tab_view(self, tab_name: str):
        """Принудительно обновляет view для вкладки"""
        if tab_name in self.tab_models:
            model = self.tab_models[tab_name]
            # Обновляем всю модель
            model.beginResetModel()
            model.endResetModel()

    # Если нужно обновлять конкретные элементы(Нужно определится)
    def refresh_file_in_tabs(self, file_path: str):
        """Обновляет конкретный файл во всех вкладках"""
        # TODO 🚧 В разработке: 28.08.2025 мертвый код refresh_file_in_tabs
        for tab_name, model in self.tab_models.items():
            model.refresh_item(file_path)
    # ------------(Нужно определится)