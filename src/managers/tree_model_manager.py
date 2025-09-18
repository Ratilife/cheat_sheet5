from PySide6.QtCore import QAbstractItemModel, QModelIndex, QObject, Signal
from PySide6.QtWidgets import QTabWidget
from src.models.st_md_file_tree_model import STMDFileTreeModel
from src.parsers.metadata_cache import MetadataCache
from src.parsers.file_parser_service import FileParserService
from src.parsers.content_cache import ContentCache
from src.controllers.selection_controller import TreeSelectionController
class TreeModelManager(QObject):
    model_updated = Signal(str, str)  # tab_name, file_path
    def __init__(self, parser_service: FileParserService,
                 metadata_cache: MetadataCache,
                 content_cache:ContentCache,
                 tab_widget: QTabWidget = None):
        """
                Локальный менеджер моделей для конкретного набора данных

                Args:
                    parser_service: сервис парсинга файлов
                    metadata_cache: кэш метаданных
                    content_cache: кэш контента
                    tab_widget: опциональный виджет вкладок для этого менеджера
        """
        super().__init__()
        self.parser_service = parser_service
        self.metadata_cache = metadata_cache
        self.content_cache = content_cache



        # 🔽 ЛОКАЛЬНЫЕ ДАННЫЕ для этого экземпляра 🔽
        self._tab_models = {}    # кэш моделей
        self._file_to_tabs = {}  # Отслеживаем, в каких вкладках какие файлы
        self._tab_widget = tab_widget  # Локальный виджет вкладок



        # Добавляем контейнер выделения
        self.selection_controller = TreeSelectionController(content_cache)

        print(f"DEBUG: Создан ЛОКАЛЬНЫЙ TreeModelManager (id: {id(self)})")




    #🔽Добавляем методы 17.09.2025🔽
    def connect_tree_view(self, tree_view):
        """Подключает дерево к контроллеру выделения этого менеджера"""
        # TODO 🚧 В разработке: 17.09.2025 мертвый код connect_tree_view
        self.selection_controller.connect_tree_view(tree_view)
        print(f"DEBUG: Дерево подключено к локальному менеджеру (id: {id(self)})")

    def build_model_for_tab(self, tab_name: str, file_paths: list[str])-> STMDFileTreeModel:
        """Создает модель для вкладки в этом менеджере"""
        # ✅ Реализовано: 17.09.2025
        print(f"DEBUG: Создание модели для вкладки '{tab_name}' в локальном менеджере")

        # Сохраняем связи файлов с вкладками ЛОКАЛЬНО
        for file_path in file_paths:
            if file_path not in self._file_to_tabs:
                self._file_to_tabs[file_path] = []
            if tab_name not in self._file_to_tabs[file_path]:
                self._file_to_tabs[file_path].append(tab_name)

        # Создаем модель для этого менеджера
        model = STMDFileTreeModel(self.content_cache)

        for file_path in file_paths:
            data = self._get_file_data(file_path)
            if data:
                model.add_file(file_path, data)

        self._tab_models[tab_name] = model
        return model

    def add_files_to_tab(self, tab_name: str, file_paths: list[str]) -> bool:
        """Добавляет файлы в указанную вкладку этого менеджера"""
        # ✅ Реализовано: 17.09.2025
        if tab_name not in self._tab_models:
            print(f"ERROR: Вкладка '{tab_name}' не найдена в этом менеджере")
            return False

        model = self._tab_models[tab_name]
        success_count = 0

        for file_path in file_paths:
            data = self._get_file_data(file_path)
            if data and model.add_file(file_path, data):
                # Локальные связи
                if file_path not in self._file_to_tabs:
                    self._file_to_tabs[file_path] = []
                if tab_name not in self._file_to_tabs[file_path]:
                    self._file_to_tabs[file_path].append(tab_name)
                success_count += 1

        print(f"DEBUG: Добавлено {success_count} файлов в менеджер {id(self)}")
        return success_count > 0

    def update_file_in_tabs(self, file_path: str) -> bool:
        """Обновляет файл во вкладках ЭТОГО менеджера"""
        # ✅ Реализовано: 17.09.2025
        if file_path not in self._file_to_tabs:
            return False

        data = self.content_cache.get(file_path)
        if not data:
            return False

        updated = False
        for tab_name in self._file_to_tabs[file_path]:
            if tab_name in self._tab_models:
                if self._tab_models[tab_name].update_file_item(file_path, data):
                    updated = True
                    self.model_updated.emit(tab_name, file_path)

        return updated

    def get_model(self, tab_name=None):
        """
        Возвращает модель(и) деревьев

        Args:
            tab_name (str, optional):
                - Если указано: возвращает модель для конкретной вкладки
                - Если None: возвращает словарь всех моделей {tab_name: model}
        """
        # ✅ Реализовано: 02.09.2025
        if tab_name:
            return self._tab_models.get(tab_name)
        else:
            return self._tab_models  # возвращаем весь словарь

    def get_tabs_for_file(self, file_path: str) -> list[str]:
        """Возвращает вкладки этого менеджера, содержащие файл"""
        # ✅ Реализовано: 17.09.2025
        return self._file_to_tabs.get(file_path, [])

    def set_tab_widget(self, tab_widget: QTabWidget):
        """Устанавливает локальный виджет вкладок для этого менеджера"""
        # ✅ Реализовано: 17.09.2025
        self._tab_widget = tab_widget


    def get_active_tab_name(self) -> str | None:
        """Возвращает активную вкладку локального виджета"""
        # ✅ Реализовано: 17.09.2025
        if self._tab_widget and self._tab_widget.count() > 0:
            current_index = self._tab_widget.currentIndex()
            if current_index >= 0:
                return self._tab_widget.tabText(current_index)
        return None

    # 🔽 ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ 🔽
    def _get_file_data(self, file_path: str) -> dict:
        """Получает данные файла для этого менеджера"""
        # ✅ Реализовано: 17.09.2025
        full_data = self.content_cache.get(file_path)
        if full_data:
            return full_data

        metadata = self.metadata_cache.get(file_path)
        if not metadata:
            metadata = self.parser_service.parse_metadata(file_path)
            self.metadata_cache.set(
                file_path,
                metadata,
                file_type=metadata.get('type')
            )

        return metadata

    def debug_info(self):
        """Выводит отладочную информацию об этом менеджере"""
        # ✅ Реализовано: 17.09.2025
        print("=" * 50)
        print(f"ЛОКАЛЬНЫЙ TreeModelManager (id: {id(self)})")
        print(f"Модели: {list(self._tab_models.keys())}")
        print(f"Файлов: {len(self._file_to_tabs)}")
        print(f"Виджет: {'есть' if self._tab_widget else 'нет'}")
        print("=" * 50)
    #🔽Конец добавления методов 17.09.2025🔽


    def connect_tree_views(self, trees_dict: dict):                 #TODO 17/09/2025 изменить переписуем TreeModelManager
        """Подключает контроллер выделения ко всем деревьям"""
        for tab_name, tree_view in trees_dict.items():
            self.selection_controller.connect_tree_view(tree_view)
            print(f"DEBUG: Контроллер подключен к дереву вкладки '{tab_name}'")

    def add_files_to_tab_old(self, tab_name: str, file_paths: list[str]):
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
        model = self._tab_models[tab_name]

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

    def update_file_in_all_tabs(self, file_path: str):                  #TODO 17/09/2025 изменить переписуем TreeModelManager ? ПОДУМАТЬ
        """Обновляет файл во всех вкладках, где он присутствует"""
        if file_path not in self._file_to_tabs:
            return False

        print(f"DEBUG✅: update_file_in_all_tabs для {file_path}")
        print(f"DEBUG✅: файл в file_to_tabs: {file_path in self._file_to_tabs}")

        if file_path not in self._file_to_tabs:
            print(f"DEBUG✅: Файл {file_path} нет в  file_to_tabs")
            print(f"DEBUG✅: доступные файлы: {list(self._file_to_tabs.keys())}")
            return False

        full_data = self.content_cache.get(file_path)
        if not full_data:
            return False

        updated = False
        for tab_name in self._file_to_tabs[file_path]:
            if self.update_model(tab_name, file_path):           #TODO 17/09/2025 изменить переписуем TreeModelManager
                updated = True
                self.model_updated.emit(tab_name, file_path)

        return updated
    def _parse_metadata(self, file_path: str) -> dict:                  #TODO 17/09/2025 изменить переписуем TreeModelManager
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
        if tab_name not in self._tab_models:
            print(f"DEBUG❌: Вкладка '{tab_name}' не найдена в tab_models!")
            print(f"DEBUG: Доступные вкладки: {list(self._tab_models.keys())}")
            return False

        if tab_name in self._tab_models:
            model = self._tab_models[tab_name]
            print(f"DEBUG: Модель для вкладки '{tab_name}' найдена")
            # Получаем полные данные из кэша
            full_data = self.content_cache.get(file_path)
            if full_data:
                print(f"DEBUG: Данные из кэша получены, обновляем элемент")
                return model.update_file_item(file_path, full_data)

        print(f"DEBUG❌: Данные для файла '{file_path}' не найдены в кэше")
        return False






