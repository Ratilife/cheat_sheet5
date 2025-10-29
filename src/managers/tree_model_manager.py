from PySide6.QtCore import QAbstractItemModel, QModelIndex, QObject, Signal, Qt
from PySide6.QtWidgets import QTabWidget
from src.models.st_md_file_tree_model import STMDFileTreeModel
from src.parsers.metadata_cache import MetadataCache
from src.parsers.file_parser_service import FileParserService
from src.parsers.content_cache import ContentCache
from src.controllers.selection_controller import TreeSelectionController
from src.operation.file_operations import FileOperations
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
        self.selection_controller.connect_tree_view(tree_view,"editor")
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
        """Добавляет список файлов в указанную вкладку этого менеджера.

                Для каждого пути в списке файлов метод пытается получить данные файла
                с помощью внутреннего метода _get_file_data. Если данные успешно
                получены и файл успешно добавлен в модель вкладки (через метод add_file),
                обновляется внутренняя карта связи файлов и вкладок (_file_to_tabs).
                Возвращает True, если хотя бы один файл был успешно добавлен.

                Args:
                    tab_name (str): Имя вкладки, в которую нужно добавить файлы.
                    file_paths (list[str]): Список строк с путями к файлам для добавления.

                Returns:
                    bool: True, если хотя бы один файл был успешно добавлен, иначе False.
        """
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
            self.selection_controller.connect_tree_view(tree_view, "editor")
            print(f"DEBUG: 🏷️ Контроллер подключен к дереву вкладки '{tab_name}'")

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

    def get_selection_info(self):
        """Получает информацию о выделении используя существующие методы модели"""
        # TODO 🚧 В разработке: 13.10.2025
        # Проверяем наличие tab_widget
        if not self._tab_widget:
            print("DEBUG: Локальный виджет вкладок не установлен")
            return None

        current_index = self._tab_widget.currentIndex()
        if current_index < 0:
            return None

        tab_name = self._tab_widget.tabText(current_index)
        tree_view = self._tab_widget.widget(current_index)

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

        # Получаем путь к файлу - для всех типов элементов
        file_path = None
        if model.get_item_type(index) in ['file', 'markdown']:
            # Если элемент сам является файлом, берем путь напрямую
            file_path = model.get_item_path(index)
        else:
            # Для template, folder и других типов ищем корневой файл в иерархии
            file_root_info = self.get_file_root_from_selection(index)
            if file_root_info:
                file_path = file_root_info['path']

        return {
            'type': model.get_item_type(index),
            'path': file_path,
            'level': model.get_item_level(index),
            'name': model.data(index, Qt.DisplayRole),
            'model': model,
            'index': index,
            'parent_index': parent_index,
            'parent_name': model.data(parent_index, Qt.DisplayRole),
            'parent_type': model.get_item_type(parent_index) if parent_index.isValid() else 'root',
            'tab_name': tab_name,
            'tree_view': tree_view
        }

    def get_file_root_from_selection(self, index):
        """Находит корневой элемент файла по выбранному индексу"""
        # TODO 🚧 В разработке: 13.10.2025
        current_index = index
        model = index.model()

        # Поднимаемся по иерархии пока не найдем элемент с путем к файлу
        while current_index.isValid():
            # ✅ Проверяем есть ли у текущего элемента путь к файлу
            item_path = model.get_item_path(current_index)
            if item_path:  # Нашли элемент с путем к файлу
                return {
                    'index': current_index,  # Индекс корневого элемента
                    'element': current_index.internalPointer(),  # Сам элемент
                    'type': model.get_item_type(current_index),  # 'file' или 'markdown'
                    'name': model.data(current_index, Qt.DisplayRole),  # Имя файла
                    'path': item_path  # Полный путь к файлу
                }
            current_index = current_index.parent()

        return None

    def creating_an_element_old(self, name, element) -> None:
        # Проверяем наличие tab_widget
        if not self._tab_widget:
            print("❌ Tab widget не установлен в менеджере")
            return

        # 1) получаем информацию о выбранном элементе
        info_item_dict = self.get_selection_info()
        if not info_item_dict:
            print("❌ Не выбран элемент для создания папки")
            return

        # 2)Подготавливаем данные для папки
        element_dict = {
            'name': name,  # ⚠️ Используем ВВЕДЕННОЕ имя, а не имя выбранного элемента!
            'type': element,
            'content': ''
        }
        # 3) Получаем модель и родительский элемент
        index = info_item_dict['index']
        model = info_item_dict['model']

        # 4) Определяем КУДА добавлять папку:
        selected_type = info_item_dict['type']

        if selected_type == 'folder':
            # ✅ Добавляем ВНУТРЬ выбранной папки
            parent_index = index
            item_parent = index.internalPointer()
        elif selected_type == 'file':
            # ✅ Файл: создаем В КОРНЕ этого файла
            # Находим корневой элемент файла
            file_root_info = self.get_file_root_from_selection(index)
            if file_root_info:
                parent_index = file_root_info['index']
                item_parent = parent_index.internalPointer()
            else:
                # ✅ Добавляем РЯДОМ с выбранным элементом (в том же родителе)
                parent_index = index.parent()
                item_parent = parent_index.internalPointer() if parent_index.isValid() else model.root_item
        elif selected_type == 'template':
            # ✅ Шаблон: создаем В ТОЙ ЖЕ ПАПКЕ что и шаблон
            parent_index = index.parent()
            item_parent = parent_index.internalPointer() if parent_index.isValid() else model.root_item
        else:
            # ❌ Неизвестный тип
            print(f"❌ Неподдерживаемый тип элемента: {selected_type}")
            return

        # 5) Добавляем элемент в модель
        success = model.add_folder(element_dict, item_parent, parent_index)

        # 6) Записываем в файл новый элемент
        if success:
            # ✅ Раскрываем родительский элемент, чтобы пользователь увидел новую папку
            tree_view = info_item_dict['tree_view']

            # ✅ Исправленная строка: получаем модель правильно
            model = tree_view.model()  # Вызываем метод model() чтобы получить модель

            # ✅ Исправленный вызов: используем правильный синтаксис
            model.layoutChanged.emit()

            if parent_index.isValid():
                tree_view.expand(parent_index)

            print(f"✅ Папка '{name}' успешно создана")

            # 7) Записываем в файл новый элемент
            file_root_info = self.get_file_root_from_selection(index)
            if file_root_info:
                file_path = info_item_dict['path']
                root_index = file_root_info['index']
                #file_st_structure = self.get_structure_to_st_file( model, root_index)
                print(f"✅ Папка '{name}' успешно создана")
                #print(file_st_structure)
            else:
                print(f"❌ Не удалось создать папку '{name}'")

    def _find_parent_in_structure(self, info_item_dict: dict, element_dict:dict):
        # TODO 🚧 В разработке: 17.10.2025
        print("🔥🔥🔥🔥Заходим в кэш чтобы найти нужную структуру метод _find_parent_in_structure()🔥🔥🔥🔥")
        print(info_item_dict)
        cache_data = self.content_cache.find_point_selection(info_item_dict)
        print(f'cache_data:  {cache_data}')
        if cache_data:

            self.file_operation = FileOperations()
            # 1. Изменяем структуру в кэше
            updated_structure = self.file_operation.add_data_st_structure(cache_data,element_dict)
            print(f'updated_structure:  {updated_structure}')
            file_path = info_item_dict['path']
            # 2. Сохраняем обновленную структуру обратно в кэш
            updated_structure_tuple = 'file', updated_structure
            self.content_cache.set(file_path, updated_structure_tuple)
            # 3. Сериализуем и записываем в файл

            st_content = self.parser_service.serialize_st_structure(updated_structure)
            print(f'st_content : {st_content}')
            success = self.file_operation.file_manager.write_file(file_path, st_content)
            print(f'success = {success}')
            if success:
                print(f"✅ Файл {file_path} успешно обновлен")
            else:
                print(f"❌ Ошибка записи файла {file_path}")


    def creating_an_element(self, name, element) -> None:
        # TODO 🚧 В разработке: 16.10.2025
        # Проверяем наличие tab_widget
        if not self._tab_widget:
            print("❌ Tab widget не установлен в менеджере")
            return

        # 1) получаем информацию о выбранном элементе
        info_item_dict = self.get_selection_info()
        if not info_item_dict:
            print("❌ Не выбран элемент для создания папки")
            return

        # 2)Подготавливаем данные для папки
        element_dict = {
            'name': name,  # ⚠️ Используем ВВЕДЕННОЕ имя, а не имя выбранного элемента!
            'type': element,
            'content': ''
        }
        # 3) Получаем модель и родительский элемент
        index = info_item_dict['index']
        model = info_item_dict['model']
        file_path = info_item_dict['path']

        # 4) Определяем КУДА добавлять папку:
        selected_type = info_item_dict['type']

        if selected_type == 'folder':
            # ✅ Добавляем ВНУТРЬ выбранной папки
            parent_index = index
            item_parent = index.internalPointer()
        elif selected_type == 'file':
            # ✅ Файл: создаем В КОРНЕ этого файла
            # Находим корневой элемент файла
            file_root_info = self.get_file_root_from_selection(index)
            if file_root_info:
                parent_index = file_root_info['index']
                item_parent = parent_index.internalPointer()
            else:
                # ✅ Добавляем РЯДОМ с выбранным элементом (в том же родителе)
                parent_index = index.parent()
                item_parent = parent_index.internalPointer() if parent_index.isValid() else model.root_item
        elif selected_type == 'template':
            # ✅ Шаблон: создаем В ТОЙ ЖЕ ПАПКЕ что и шаблон
            parent_index = index.parent()
            item_parent = parent_index.internalPointer() if parent_index.isValid() else model.root_item
        else:
            # ❌ Неизвестный тип
            print(f"❌ Неподдерживаемый тип элемента: {selected_type}")
            return

        # 5) Добавляем элемент в модель
        success = model.add_folder(element_dict, item_parent, parent_index)

        # 6) Записываем в файл новый элемент
        if success:
            # ✅ Раскрываем родительский элемент, чтобы пользователь увидел новую папку
            tree_view = info_item_dict['tree_view']

            # ✅ Исправленная строка: получаем модель правильно
            model = tree_view.model()  # Вызываем метод model() чтобы получить модель

            # ✅ Исправленный вызов: используем правильный синтаксис
            model.layoutChanged.emit()

            if parent_index.isValid():
                tree_view.expand(parent_index)
            print(f'обновили UI модель переменная model')
            # 2. Получаем/создаем текущую структуру
            #current_structure = self.content_cache.get(str(file_path))
            #print(current_structure)
            self._find_parent_in_structure(info_item_dict, element_dict)

    def new_template(self, name_template) -> None:
        """Создает новый шаблон на основе выбранного элемента"""
        # TODO 🚧 В разработке: 14.10.2025
        self.creating_an_element(name_template, 'template')

    def new_folder(self, name_folder):
        """Создает новую папку на основе выбранного элемента"""
        # TODO 🚧 В разработке: 14.10.2025
        self.creating_an_element(name_folder,'folder')


    def get_structure_to_st_file(self, model, index):
        # TODO 🚧 В разработке: 13.10.2025
        # 1) Изменяем текущую структуру модели дерева в структуру st-файла
        file_structure = self.parser_service.serialize_st_structure(model, index)
        return file_structure
