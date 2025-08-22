from PySide6.QtCore import QAbstractItemModel, QModelIndex, QObject, Signal
from src.models.st_md_file_tree_model import STMDFileTreeModel
from src.models.st_md_file_tree_item import STMDFileTreeItem
from src.parsers.metadata_cache import MetadataCache
from src.parsers.file_parser_service import FileParserService
class TreeModelManager(QObject):
    def __init__(self, parser_service: FileParserService, metadata_cache: MetadataCache):
        super().__init__()
        self.parser_service = parser_service
        self.metadata_cache = metadata_cache
        self.tab_models = {}
    def build_skeleton_model(self, file_paths: list) -> STMDFileTreeModel:
        """Создает модель только с метаданными файлов"""
        root_item = STMDFileTreeItem(["Root", "folder"])


        for path in file_paths:
            # Получаем метаданные (из кэша или парсим)
            metadata = self.metadata_cache.get(path) or self._parse_metadata(path)

            # Создаем элемент дерева
            item = STMDFileTreeItem([
                metadata["name"],
                metadata["type"],
                path  # Полный путь для последующего парсинга
            ], root_item)
            root_item.appendChild(item)

        self.model = STMDFileTreeModel(root_item)

        return self.model

    def _parse_metadata(self, file_path: str) -> dict:
        """Парсит метаданные файла (вызывает FileParserService)"""
        return self.parser_service.parse_metadata(file_path)