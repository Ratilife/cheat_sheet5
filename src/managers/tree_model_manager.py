from PySide6.QtCore import QAbstractItemModel, QModelIndex, QObject, Signal
from src.models.st_md_file_tree_model import STMDFileTreeModel
from src.models.st_md_file_tree_item import STMDFileTreeItem
from src.parsers.metadata_cache import MetadataCache
from src.parsers.file_parser_service import FileParserService
from src.parsers.content_cache import ContentCache
from src.controllers.selection_controller import TreeSelectionController
class TreeModelManager(QObject):
    model_updated = Signal(str, str)  # tab_name, file_path
    def __init__(self, parser_service: FileParserService, metadata_cache: MetadataCache, content_cache:ContentCache):
        super().__init__()
        self.parser_service = parser_service
        self.metadata_cache = metadata_cache
        self.content_cache = content_cache

        self.tab_models = {}    # кэш моделей
        self.file_to_tabs = {}  # Отслеживаем, в каких вкладках какие файлы

        # Добавляем контейнер выделения
        self.selection_controller = TreeSelectionController(content_cache)

    def connect_tree_views(self, trees_dict: dict):
        """Подключает контроллер выделения ко всем деревьям"""
        for tab_name, tree_view in trees_dict.items():
            self.selection_controller.connect_tree_view(tree_view)
            print(f"DEBUG: Контроллер подключен к дереву вкладки '{tab_name}'")

    def build_model_for_tab(self, tab_name: str, file_paths: list[str]) -> STMDFileTreeModel:
        # ✅ Реализовано: 28.08.2025
        # Сохраняем связь файлов с вкладками
        print(f"DEBUG✅: построение модели для вкладки '{tab_name}' с файлами {len(file_paths)}")
        for file_path in file_paths:
            print(f"DEBUG✅: привязка файла  {file_path} к вкладке {tab_name}")
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
        print(f"DEBUG💾: Модель для вкладки '{tab_name}' сохранена в tab_models")
        print(f"DEBUG: Теперь в tab_models: {list(self.tab_models.keys())}")
        return model

    def add_files_to_tab(self, tab_name: str, file_paths: list[str]):
        """
        Добавляет файлы в указанную вкладку
        Args:
            tab_name: имя целевой вкладки
            file_paths: список путей к файлам для добавления
        Returns:
            bool: успешность операции
        """
        # Проверяем существование модели для вкладки
        if tab_name not in self.tab_models:
            print(f"DEBUG❌: Модель для вкладки '{tab_name}' не найдена")
            return False

        # Получаем модель вкладки
        model = self.tab_models[tab_name]

        # Парсим файлы
        parsed_data_list = self._parse_content_data(file_paths)

        # Добавляем каждый файл в модель
        for file_path, parsed_data in zip(file_paths, parsed_data_list):
            # Добавляем файл в модель
            success = model.add_file(file_path, parsed_data)

            if success:
                # Обновляем связи файлов с вкладками
                if file_path not in self.file_to_tabs:
                    self.file_to_tabs[file_path] = []
                if tab_name not in self.file_to_tabs[file_path]:
                    self.file_to_tabs[file_path].append(tab_name)
                print(f"DEBUG✅: Файл '{file_path}' добавлен в вкладку '{tab_name}'")
            else:
                print(f"DEBUG❌: Не удалось добавить файл '{file_path}'")

        return True



    def update_file_in_all_tabs(self, file_path: str):
        """Обновляет файл во всех вкладках, где он присутствует"""
        if file_path not in self.file_to_tabs:
            return False

        print(f"DEBUG✅: update_file_in_all_tabs для {file_path}")
        print(f"DEBUG✅: файл в file_to_tabs: {file_path in self.file_to_tabs}")

        if file_path not in self.file_to_tabs:
            print(f"DEBUG✅: Файл {file_path} нет в  file_to_tabs")
            print(f"DEBUG✅: доступные файлы: {list(self.file_to_tabs.keys())}")
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

    def _parse_content_data(self,file_paths: list[str]) -> list:

        parser_list= []
        for file_path in file_paths:
            parser = self.parser_service.parse_and_get_type(file_path=file_path)
            # Извлекаем тип файла и данные
            parser_list.append(parser[1])

        return parser_list
    def update_model(self, tab_name: str, file_path: str):
        """Обновляет модель при получении новых данных и возвращает успешность"""
        # TODO 🚧 В разработке: 28.08.2025
        print(f"DEBUG🔄: update_model для вкладки '{tab_name}', файл '{file_path}'")

        # Проверяем существование вкладки временно для отладки
        if tab_name not in self.tab_models:
            print(f"DEBUG❌: Вкладка '{tab_name}' не найдена в tab_models!")
            print(f"DEBUG: Доступные вкладки: {list(self.tab_models.keys())}")
            return False

        if tab_name in self.tab_models:
            model = self.tab_models[tab_name]
            print(f"DEBUG: Модель для вкладки '{tab_name}' найдена")
            # Получаем полные данные из кэша
            full_data = self.content_cache.get(file_path)
            if full_data:
                print(f"DEBUG: Данные из кэша получены, обновляем элемент")
                return model.update_file_item(file_path, full_data)

        print(f"DEBUG❌: Данные для файла '{file_path}' не найдены в кэше")
        return False

    def refresh_tab_view(self, tab_name: str):
        """Принудительно обновляет view для вкладки"""
        # TODO 🚧 В разработке: 28.08.2025 мертвый код refresh_tab_view
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
    def debug_file_to_tabs(self):
        """Выводит содержимое file_to_tabs для отладки"""
        # временно проверочный метод
        print("=" * 50)
        print("DEBUG: file_to_tabs contents:")
        if not self.file_to_tabs:
            print("  EMPTY - no files linked to tabs!")
            return

        for file_path, tabs in self.file_to_tabs.items():
            print(f"  {file_path}: {tabs}")
        print("=" * 50)