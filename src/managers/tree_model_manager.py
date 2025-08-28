from PySide6.QtCore import QAbstractItemModel, QModelIndex, QObject, Signal
from src.models.st_md_file_tree_model import STMDFileTreeModel
from src.models.st_md_file_tree_item import STMDFileTreeItem
from src.parsers.metadata_cache import MetadataCache
from src.parsers.file_parser_service import FileParserService
from src.parsers.content_cache import ContentCache
class TreeModelManager(QObject):

    def __init__(self, parser_service: FileParserService, metadata_cache: MetadataCache, content_cache:ContentCache):
        super().__init__()
        self.parser_service = parser_service
        self.metadata_cache = metadata_cache
        self.content_cache = content_cache
        self.tab_models = {}

    def build_model_for_tab(self, tab_name: str, file_paths: list[str]) -> STMDFileTreeModel:
        # ✅ Реализовано: 26.08.2025
        # 1. СОЗДАЕМ модель (в её конструкторе УЖЕ создан корневой элемент)
        model = STMDFileTreeModel(self.content_cache)

        for file_path in file_paths:
            # 1. В первую очередь проверяем "богатый" кэш
            full_data = self.content_cache.get(file_path)
            if full_data:
                # Используем полные данные для построения элемента
                model.add_file(file_path, full_data)
                continue
            # 2. Если полных данных нет, проверяем "легкий" кэш метаданных
            metadata = self.metadata_cache.get(file_path)
            if not metadata:
                # 3. Если данных нет вообще, парсим метаданные синхронно (это должно быть быстро)
                metadata = self._parse_metadata(file_path)
                # Кэшируем результат для будущего использования!
                self.metadata_cache.set(file_path, metadata, file_type=metadata.get('type'))
            # 4. Используем метаданные (из кэша или только что распарсенные)
            model.add_file(file_path, metadata)

        self.tab_models[tab_name] = model
        return model


    def _parse_metadata(self, file_path: str) -> dict:
        """Парсит метаданные файла (вызывает FileParserService)"""
        return self.parser_service.parse_metadata(file_path)

    def update_model(self, tab_name: str, file_path: str):
        """ООбновляет модель при получении новых данных и возвращает успешность"""
        # ✅ Реализовано: 28.08.2025
        if tab_name in self.tab_models:
            model = self.tab_models[tab_name]
            # Получаем полные данные из кэша
            full_data = self.content_cache.get(file_path)
            if full_data:
                return model.update_file_item(file_path, full_data)
        return False

    def refresh_tab_models(self, tab_names: list):
        """
        Обновляет представления для указанных вкладок

        Args:
            tab_names: Список имен вкладок для обновления
        """
        for tab_name in tab_names:
            if tab_name in self.tab_models:
                model = self.tab_models[tab_name]
                model.refresh_view()

    # Если нужно обновлять конкретные элементы(Нужно определится)
    def refresh_file_in_tabs(self, file_path: str):
        """Обновляет конкретный файл во всех вкладках"""
        # TODO 🚧 В разработке: 28.08.2025 мертвый код refresh_file_in_tabs
        for tab_name, model in self.tab_models.items():
            model.refresh_item(file_path)
    # ------------(Нужно определится)