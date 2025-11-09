from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTabWidget,
                               QTreeWidget, QApplication,
                               QMenu, QLabel, QPushButton, )
from PySide6.QtGui import QAction, QCursor

from src.utils.cache_manager import get_content_cache
from src.managers.dynamic_tabs import DynamicTabManager
from src.observers.file_watcher import FileWatcher
from src.observers.my_base_observer import MyBaseObserver
from widgets.md.markdown_viewer_widget import MarkdownViewer
from PySide6.QtCore import Qt, QRect, QSize, QTimer
from src.managers.ui_manager import UIManager
from src.managers.toolbar_manager import ToolbarManager
from src.operation.file_operations import FileOperations
from src.managers.tree_model_manager import TreeModelManager
from src.parsers.background_parser import BackgroundParser,Priority
from src.parsers.file_parser_service import FileParserService
from src.parsers.metadata_cache import MetadataCache
from src.ui.file_editor import FileEditorWindow
class SidePanelObserver(MyBaseObserver):
    # ✅ Реализовано: 29.06.2025
    def __init__(self):
        super().__init__()
class SidePanel(QWidget):
    # TODO 🚧 В разработке: 30.08.2025
    def __init__(self, parent=None):
        super().__init__(parent, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        # Базовая минимальная инициализация
        self.observer = SidePanelObserver()
        self.file_operation = FileOperations()

        self._template_name = "Тут будет текст"

        # Установите минимальные размеры и флаги
        self.setMinimumWidth(300)
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        # Создайте placeholder для быстрого показа
        self._setup_loading_ui()

        # Отложите тяжелую инициализацию
        QTimer.singleShot(0, self._delayed_full_init)

    def _setup_loading_ui(self):
        """Быстрый UI placeholder с индикатором загрузки"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Простой индикатор загрузки
        loading_label = QLabel("Загрузка боковой панели...")
        loading_label.setAlignment(Qt.AlignCenter)
        loading_label.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                padding: 20px;
                color: #666;
                font-size: 12px;
            }
        """)

        layout.addWidget(loading_label)
        self.setLayout(layout)

    def _delayed_full_init(self):
        """Полная инициализация после показа окна"""
        try:
            # Очищаем предыдущие состояния
            self._cleanup_previous_state()
            # 1. Получите данные для вкладок
            self.tab_names = self.file_operation.fetch_file_heararchy()
            if not isinstance(self.tab_names, dict):
                self.tab_names = {"Documents": []}

            # Проверка наличия файла saved_files.json и внесение данных файла в self.tab_names
            self.tab_names = self.file_operation.extend_dict_with_file('saved_files.json',self.tab_names)

            # 2. Инициализируйте менеджеры
            self._init_managers()

            # 3. Инициализируйте наблюдателей
            self._init_observers()

            # 4. Создайте основной UI (заменит placeholder)
            self._init_ui()

            # 5. Подключите сигналы
            self._connect_signals()

            # 6. Подключение сигналов контейнеров
            self._connect_selection_signals()

            # 7. Создайте вкладки с деревьями
            self._create_tabs_with_trees(self.tab_names)

            # 8. Инициализируйте меню позиционирования
            self._init_position_menu()

            # 9. Настройте прикрепление к краям
            self._setup_screen_edge_docking()

            # 10. Отладочная информация
            self.tree_model_manager.debug_info()

            # 11. ПОКАЗАТЬ панель после инициализации
            self.show()

            # 12. Регистрируем с высоким приоритетом
            # Сначала удаляем старую регистрацию, если есть


            self.tab_manager.register_tab_widget(
                "side_panel",
                self.tab_widget,
                priority=100  # Высокий приоритет
            )  #TODO 17/09/2025 изменить переписуем TreeModelManager


        except Exception as e:
            print(f"Ошибка при инициализации SidePanel: {e}")
            import traceback
            traceback.print_exc()

            # В случае ошибки покажите сообщение
            self._show_error_ui(str(e))

    def _cleanup_previous_state(self):
        """Очищает состояние от предыдущего экземпляра"""
        if hasattr(self, 'tree_model_manager'):
            # Удаляем модели этого окна
            for tab_name in list(self.tree_model_manager.tab_models.keys()):
                if tab_name in getattr(self, 'tab_names', {}):
                    del self.tree_model_manager.tab_models[tab_name]

            # Очищаем связи файлов с вкладками
            for file_path in list(self.tree_model_manager.file_to_tabs.keys()):
                if file_path in self.tree_model_manager.file_to_tabs:
                    self.tree_model_manager.file_to_tabs[file_path] = [
                        tab for tab in self.tree_model_manager.file_to_tabs[file_path]
                        if tab not in getattr(self, 'tab_names', {})
                    ]
                    if not self.tree_model_manager.file_to_tabs[file_path]:
                        del self.tree_model_manager.file_to_tabs[file_path]

    def _show_error_ui(self, error_message):
        """Показать UI с ошибкой"""
        # Очистить текущий layout
        if self.layout():
            QWidget().setLayout(self.layout())

        layout = QVBoxLayout(self)

        error_label = QLabel(f"Ошибка загрузки:\n{error_message}")
        error_label.setAlignment(Qt.AlignCenter)
        error_label.setStyleSheet("""
                QLabel {
                    background-color: #ffe6e6;
                    padding: 20px;
                    color: #d32f2f;
                    font-size: 12px;
                    border: 1px solid #d32f2f;
                }
        """)

        retry_button = QPushButton("Повторить")
        retry_button.clicked.connect(self._delayed_full_init)

        layout.addWidget(error_label)
        layout.addWidget(retry_button)
        self.setLayout(layout)

    def _init_ui(self):
        """Инициализация пользовательского интерфейса (заменяет placeholder)"""
        # Полностью очищаем предыдущий UI
        self._cleanup_ui()

        # Создать основной layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # ... остальной код _init_ui без изменений
        self.ui = UIManager()
        self.tree_manager = None

        self.splitter = self.ui.create_splitter(Qt.Vertical,
                                                sizes=[300, 100],
                                                handle_width=5,
                                                handle_style="QSplitter::handle { background: #ccc; }")

        # Создаем toolbar manager
        self.toolbar_manager = ToolbarManager( tree_manager=self.tree_model_manager,
                                               close=self.close,
                                               showMinimized=self.showMinimized)

        # Создаем панель заголовка
        title_layout = self.toolbar_manager.get_title_layout()
        main_layout.addWidget(title_layout)

        # Создаем виджет вкладок
        self.tab_widget = self.tab_manager.tab_widget
        self.tab_widget.setTabPosition(QTabWidget.West)
        main_layout.addWidget(self.tab_widget)

        # Отображение template_name
        template_label = QLabel(f"Шаблон: {self.template_name}")
        template_label.setStyleSheet("""
                    QLabel {
                        background-color: #e0e0e0;
                        padding: 5px;
                        color: #555;
                        font-size: 10px;
                        border-bottom: 1px solid #ccc;
                    }
                """)
        template_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(template_label)

        # Нижняя панель
        self.content_viewer = MarkdownViewer()
        self.splitter.addWidget(self.content_viewer)
        main_layout.addWidget(self.splitter)

        self.setLayout(main_layout)

    def _cleanup_ui(self):
        """Очистка всех UI компонентов"""
        # Удаляем все дочерние виджеты
        for child in self.findChildren(QWidget):
            if child != self:  # Не удаляем себя
                child.deleteLater()

        # Удаляем layout
        if self.layout():
            QWidget().setLayout(self.layout())


    def _init_managers(self)->None:
        """Инициализация всех менеджеров и сервисов"""
        # ✅ Реализовано: 20.08.2025
        # 1. Создаем кэш (синглтон)
        self.metadata_cache = MetadataCache()
        self.content_cache = get_content_cache() # Инициализация кэша

        # 2. Создаем парсер сервис
        self.parser_service = FileParserService()

        # 3. Создаем менеджер моделей с зависимостями
        self.tree_model_manager = TreeModelManager(
            parser_service=self.parser_service,
            metadata_cache=self.metadata_cache,
            content_cache=self.content_cache
        )
        print("SidePanel: Инициализация BackgroundParser")
        # 4. Создаем фоновый парсер
        self.background_parser = BackgroundParser.instance(
            parser_service=self.parser_service,
            content_cache=self.content_cache
        )

        # 5. Создаем менеджер вкладок
        self.tab_manager = DynamicTabManager()
        # 6. Сразу подключаем сигнал, который должен работать ДО создания UI
        self.tab_manager.tab_created.connect(self._on_fill_tab_tree)

    def _init_observers(self)->None:
        """Инициализация наблюдателей"""
        self.file_watcher = FileWatcher()
        self.file_watcher.file_updated.connect(self._on_file_updated)
        self.file_watcher.file_deleted.connect(self._on_file_deleted)
        self.file_watcher.dir_changed.connect(self._on_dir_changed)

    def _connect_signals(self):
        print("=" * 50)
        print("ПОДКЛЮЧЕНИЕ СИГНАЛОВ - НАЧАЛО")

        try:
            # Проверяем существование менеджеров
            print(f"tab_manager exists: {hasattr(self, 'tab_manager')}")
            print(f"background_parser exists: {hasattr(self, 'background_parser')}")

            if hasattr(self, 'tab_manager'):
                print("Подключаем tab_created...")
                print(f"Type of tab_created: {type(self.tab_manager.tab_created)}")
                print(f"Has connect: {hasattr(self.tab_manager.tab_created, 'connect')}")

                #self.tab_manager.tab_created.connect(self._on_fill_tab_tree)
                #print("tab_created подключен!")

            if hasattr(self, 'background_parser'):
                print("Подключаем task_finished...")
                self.background_parser.task_finished.connect(self._on_parsing_done)
                print("task_finished подключен!")
            if hasattr(self, 'tree_model_manager'):
                print("Подключаем model_updated...")
                self.tree_model_manager.model_updated.connect(self._on_model_updated)
                print("model_updated подключен!")

            self.toolbar_manager.editor_toggled.connect(self._open_editor)

        except Exception as e:
            print(f"ОШИБКА при подключении сигналов: {e}")
            import traceback
            traceback.print_exc()

        print("ПОДКЛЮЧЕНИЕ СИГНАЛОВ - КОНЕЦ")
        print("=" * 50)

    def _connect_selection_signals(self):
        """Подключает сигналы контроллера выделения"""
        controller = self.tree_model_manager.selection_controller

        controller.content_for_sidepanel.connect(self.on_display_content)
        controller.selection_changed.connect(self.on_update_selection_status)
        controller.error_occurred.connect(self.on_show_selection_error)

        # Устанавливаем источник для контроллера
        controller.current_source = "sidepanel"
        print("Сигналы контроллера выделения подключены")

    def _create_tabs_with_trees(self, tab_name: dict):
        """Создает вкладки с отложенной загрузкой деревьев"""
        self.tab_manager.create_tabs(tab_name)
        # Подключаем контейнер к деревьям
        #self.tree_model_manager.connect_tree_views(self.tab_manager.trees)

        for tab_name, tree_view in self.tab_manager.trees.items():
            self.tree_model_manager.selection_controller.connect_tree_view(tree_view, "sidepanel")

        # Вместо немедленной загрузки всех деревьев,
        # загружаем только первую активную вкладку
        if self.tab_manager.tab_widget.count() > 0:
            current_index = self.tab_manager.tab_widget.currentIndex()
            current_tab_name = self.tab_manager.tab_widget.tabText(current_index)
            self._load_tab_data(current_tab_name)

        # Подключаем загрузку при переключении вкладок
        self.tab_manager.tab_widget.currentChanged.connect(self._on_tab_changed)

    #----Обработка сигналов
    def _on_tab_changed(self, index):
        """Загружает данные только для активной вкладки"""
        if index >= 0:
            tab_name = self.tab_manager.tab_widget.tabText(index)
            self._load_tab_data(tab_name)

    def _on_file_deleted(self, path):
        """Реагирует на удаление файла."""
        # TODO 🚧 В разработке: 08.08.2025
        pass

    def _on_file_updated(self,path):
        """Реагирует на изменение файла."""
        # TODO 🚧 В разработке: 08.08.2025
        pass

    def _on_dir_changed(self):
        # TODO 🚧 В разработке: 10.08.2025
        pass

    def on_display_content(self, content_type, content, source):
        """Отображает контент в редакторе"""
        # TODO 🚧 В разработке: 30.08.2025
        # Проверяем, активно ли это окно
        if not self.isVisible():
            return

        try:
            # Очищаем предыдущее содержимое
            self.content_viewer.set_content("") # используем метод MarkdownViewer

            # Обработка разных типов элементов
            if content_type == 'template':
                self.content_viewer.set_content(content)
                self.content_viewer.set_view_mode("text")  # <-- Устанавливаем текстовый режим для ST файлов
            elif content_type == 'markdown':
                self.content_viewer.set_content(content)
                self.content_viewer.set_view_mode("markdown")  # <-- Устанавливаем markdown режим для MD файлов
        except Exception as e:
            print(f"Ошибка предпросмотра в SidePanel: {e}")

    def on_update_selection_status(self, metadata):
        """Обновляет статус выделения"""
        # TODO 🚧 В разработке: 30.08.2025 - забыл зачем нужен этот метод on_update_selection_status
        pass

    def on_show_selection_error(self, error_message):
        """Показывает ошибку выделения"""
        print(f"Ошибка выделения: {error_message}")

    def _on_fill_tab_tree(self, tab_name: str, tree: QTreeWidget):
        """Заполняет дерево файлов для указанной вкладки с метаданными.

        Метод выполняет инициализацию и отображение древовидной структуры файлов
        для конкретной вкладки, включая загрузку метаданных и фоновый парсинг.

        Args:
            tab_name (str): Название вкладки, для которой заполняется дерево
            tree (QTreeWidget): Виджет дерева, который нужно заполнить

        Workflow:
            1. Проверяет существование вкладки в системе
            2. Загружает список файлов, связанных с вкладкой
            3. Строит модель метаданных для отображения в дереве
            4. Инициирует фоновый парсинг для файлов, отсутствующих в кэше

        Notes:
            - Использует кэширование для избежания повторного парсинга файлов
            - Запускает асинхронные задачи для обработки больших файлов
            - Включает расширенное логирование для отладки

        Raises:
            Exception: Ловит и логирует любые ошибки в процессе заполнения дерева
        """
        # Для проверки
        print(f"DEBUG: _on_fill_tab_tree вызывается для вкладки: {tab_name}")

        try:
            if tab_name not in self.tab_names:
                print(f"DEBUG: tab {tab_name} not found in tab_names")
                return

            # 1. Получаем пути файлов для этой вкладки
            file_paths = self.tab_names[tab_name]
            print(f"DEBUG: Найдено {len(file_paths)} файловдля вкладки {tab_name}")

            # Проверяем, что менеджер моделей инициализирован
            if not hasattr(self, 'tree_model_manager'):
                print("ОШИБКА: tree_model_manager не инициализирован!")
                return

            # 2. Запрашиваем модель с метаданными
            model = self.tree_model_manager.build_model_for_tab(tab_name, file_paths)

            # 3. Привязываем модель к дереву
            if model:
                tree.setModel(model)
                print(f"Модель установлена для {tab_name}")

            # 4. Запускаем фоновый парсинг
            for file_path in file_paths:
                print(f"DEBUG: Обрабатывающий файл: {file_path}")

                # Проверяем кэш
                cached_data = self.content_cache.get(file_path)
                if not cached_data:
                    print(f"DEBUG: Файл {file_path} отсутствующий в content_cache, добавляется в синтаксический анализатор")

                    # ПРОВЕРКА ПЕРЕД ДОБАВЛЕНИЕМ ЗАДАЧИ
                    print(f"background_parser тип: {type(self.background_parser)}")
                    print(f"background_parser.add_task имеет connect: {hasattr(self.background_parser, 'add_task')}")

                    try:
                        self.background_parser.add_task(file_path, Priority.VISIBLE)
                        print(f"DEBUG: Задача, добавленная для {file_path}")
                    except Exception as e:
                        print(f"ОШИБКА при добавлении задачи: {e}")
                        import traceback
                        traceback.print_exc()
                else:
                    print(f"DEBUG: Файл {file_path} уже находится в кэше")

        except Exception as e:
            print(f"Ошибка при заполнении дерева для вкладки {tab_name}: {e}")

            traceback.print_exc()

    def _on_parsing_done(self, file_path: str, parsed_data: dict,*args, **kwargs):
        """Обработчик завершения фонового парсинга"""
        print(f"🚨🚨🚨 _on_parsing_done ВЫЗВАН! args: {args}, kwargs: {kwargs}")
        print(f"🌤️Парсинг завершен для: {file_path}")

        #  Обновляем ВО ВСЕХ вкладках через менеджер моделей
        updated = self.tree_model_manager.update_file_in_tabs(file_path)   # TODO 18/09/2025 тут начинается ошибка _on_parsing_done -> self.tree_model_manager.update_file_in_all_tabs(file_path)

        if not updated:
            print(f"Предупреждение: файл {file_path} не найден в активных моделях")
            print(f"DEBUG: Файл {file_path} Существует в кэше: {file_path in self.content_cache._cache}")
    def _on_model_updated(self, tab_name: str, file_path: str):
        """Обновляет view для конкретной вкладки после изменения модели"""
        print(f"DEBUG✅: _on_model_updated вызывается для вкладки {tab_name}, файла {file_path}")
        if tab_name in self.tab_manager.trees:
            tree_view = self.tab_manager.trees[tab_name]

            # Проверяем, не удален ли C++ объект (для PySide6)
            try:
                # Простая проверка - пытаемся получить свойство объекта
                if not tree_view.objectName():
                    pass  # Просто проверяем доступность объекта
            except RuntimeError as e:
                if "already deleted" in str(e):
                    print(f"Дерево для вкладки {tab_name} было удалено")
                    # Удаляем ссылку из словаря
                    del self.tab_manager.trees[tab_name]
                    return
                else:
                    raise e
            # Обновляем всю модель для этой вкладки
            tree_view.viewport().update()

            # Или если нужно обновить конкретные элементы:
            model = tree_view.model()
            if model:
                model.refresh_view()

    #----------------------

    def _load_tab_data(self, tab_name):
        """Загружает данные для конкретной вкладки"""
        if tab_name not in self.tab_names:
            return

        file_paths = self.tab_names[tab_name]
        if not file_paths:
            return

        # Получаем дерево для этой вкладки
        tree_view = self.tab_manager.trees.get(tab_name)
        if tree_view and not tree_view.model():
            # Создаем модель только если она еще не создана
            model = self.tree_model_manager.build_model_for_tab(tab_name, file_paths)
            if model:
                tree_view.setModel(model)

                # Запускаем фоновый парсинг для этой вкладки
                for file_path in file_paths:
                    if not self.content_cache.get(file_path):
                        self.background_parser.add_task(file_path, Priority.VISIBLE)

    def _open_editor(self):
        """Открыть окно редактора файла"""
        # ✅ Реализовано: 02.09.2025
        editor_window = FileEditorWindow(self)
        # Центрируем окно на экране
        self._center_window(editor_window)
        editor_window.show()

    def _center_window(self, window):
        """Центрирует окно на активном мониторе"""
        # Получаем монитор, на котором находится курсор
        cursor_pos = QCursor.pos()
        screen = QApplication.screenAt(cursor_pos)

        if not screen:
            # Если не нашли монитор, используем основной
            screen = QApplication.primaryScreen()

        screen_geometry = screen.availableGeometry()

        # Вычисляем центральную позицию
        x = screen_geometry.x() + (screen_geometry.width() - window.width()) // 2
        y = screen_geometry.y() + (screen_geometry.height() - window.height()) // 2

        # Устанавливаем позицию окна
        window.move(x, y)

    # Метод инициализации контекстного меню

    def _init_position_menu(self):
        """
        Инициализирует контекстное меню управления положением боковой панели и настраивает связанные действия и обработчики.

        Основные шаги метода:
        1. Создаёт выпадающее меню (`QMenu`) с заголовком "Позиция панели".
        2. Создаёт три действия (`QAction`) с возможностью установки флажка:
            - "Закрепить слева" (`self.pin_left_action`): позволяет закрепить панель у левого края экрана. Подключается к обработчику `self._dock_to_left`.
            - "Закрепить справа" (`self.pin_right_action`): позволяет закрепить панель у правого края экрана. Подключается к обработчику `self._dock_to_right`.
            - "Свободное перемещение" (`self.float_action`): переводит панель в плавающий режим, когда её можно свободно перемещать. Подключается к обработчику `self._enable_floating`.
        3. Добавляет все созданные действия в меню (`self.position_menu.addActions`).
        4. Устанавливает для панели политику отображения собственного контекстного меню (`Qt.CustomContextMenu`).
        5. Подключает обработчик события вызова контекстного меню (`self.customContextMenuRequested.connect(self.show_context_menu)`), чтобы при вызове меню показывалось именно это меню с действиями управления позиционированием.

        В результате метод формирует удобное и интуитивно понятное меню, позволяющее пользователю быстро менять положение панели или переводить её в плавающий режим через контекстное меню.

        """
        # ✅ Реализовано: 30.06.2025
        # Создаем меню с заголовком
        self.position_menu = QMenu("Позиция панели", self)

        # Создаем действие "Закрепить слева"
        self.pin_left_action = QAction("Закрепить слева", self, checkable=True)
        # Подключаем обработчик
        self.pin_left_action.triggered.connect(self._dock_to_left)

        # Создаем действие "Закрепить справа"
        self.pin_right_action = QAction("Закрепить справа", self, checkable=True)
        # Подключаем обработчик
        self.pin_right_action.triggered.connect(self._dock_to_right)

        # Создаем действие "Свободное перемещение"
        self.float_action = QAction("Свободное перемещение", self, checkable=True)
        # Подключаем обработчик
        self.float_action.triggered.connect(self._enable_floating)

        # Добавляем действия в меню
        self.position_menu.addActions([self.pin_left_action, self.pin_right_action, self.float_action])
        # Устанавливаем политику контекстного меню
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        # Подключаем обработчик показа контекстного меню
        self.customContextMenuRequested.connect(self.show_context_menu) #TODO нет метода show_context_menu

    def _dock_to_left(self):
        """
        Закрепляет боковую панель у левого края экрана и обновляет связанные параметры интерфейса.

        Действия метода:
        1. Устанавливает атрибут `self.dock_position` в значение "left", что переводит панель в режим закрепления слева.
        2. Вызывает метод `self.update_dock_position()`, который обновляет геометрию и размеры панели для корректного расположения у левого края экрана с учетом всех ограничений и отступов.
        3. Обновляет состояние чекбоксов меню с помощью метода `self._update_menu_checks()`, чтобы визуальное отображение меню соответствовало текущему положению панели.

        Такой подход гарантирует синхронизацию состояния интерфейса и положения панели после закрепления слева.
        """
        # ✅ Реализовано: 30.06.2025
        self.dock_position = "left"
        self.update_dock_position()
        self._update_menu_checks()

        # Метод для закрепления панели справа
    def _dock_to_right(self):
        """
        Перемещает боковую панель к правому краю экрана и обновляет все связанные параметры интерфейса.

        Действия метода:
        1. Устанавливает режим расположения панели (`self.dock_position`) в значение "right", что означает закрепление панели у правого края экрана.
        2. Вызывает метод `self.update_dock_position()`, который обновляет геометрию и размеры панели в соответствии с новым положением. Панель фиксируется по ширине и высоте и располагается вплотную к правому краю с учетом отступа.
        3. Обновляет состояние чекбоксов в меню с помощью метода `self._update_menu_checks()`, чтобы визуально отразить текущее положение панели для пользователя.

        Такой порядок гарантирует, что интерфейс пользователя и состояние панели всегда синхронизированы после изменения положения.
        """
        # ✅ Реализовано: 30.06.2025
        self.dock_position = "right"
        self.update_dock_position()
        self._update_menu_checks()

    # Метод для включения свободного перемещения
    def _enable_floating(self):

        # TODO 🚧 В разработке: 11.08.2025
        self.dock_position = "float"
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        self.setWindowTitle("Боковая панель")  # Устанавливаем заголовок окна
        # Снимаем фиксированные размеры и задаем допустимый диапазон
        self.setMinimumSize(200, 200)  # Минимальный размер
        self.setMaximumSize(16777215, 16777215)  # Максимальный (практически неограничен)

        self.show()

        # Устанавливаем начальные размеры и позицию
        screen = QApplication.primaryScreen().availableGeometry()
        self.setGeometry(QRect(
                    screen.right() - 350,  # X координата (немного левее правого края)
                    screen.top() + 100,  # Y координата (немного ниже верхнего края)
                    300,  # Ширина
                    screen.height() - 200  # Высота (меньше высоты экрана)
                    ))
        # Снимаем фиксированные размеры


        self._update_menu_checks()

    # Метод обновления позиции панели

    def update_dock_position(self):
        """
        Обновляет положение и размер боковой панели в зависимости от выбранного режима закрепления относительно экрана.

        Метод определяет текущий режим расположения панели (`self.dock_position`) и изменяет её геометрию и ограничения размеров в соответствии с этим режимом:

         - Если панель закреплена слева (`"left"`):
            - Панель располагается у левого края экрана с учётом отступа (`self.dock_margin`).
            - Высота панели равна высоте рабочего пространства экрана, ширина фиксируется на 300 пикселей.
            - Высота также фиксируется — панель не может быть изменена по высоте пользователем.
            - Если панель закреплена справа (`"right"`):
            - Панель располагается у правого края экрана с учётом ширины панели и отступа.
            - Высота и ширина фиксированы аналогично левому положению.
         - Если панель в плавающем режиме (`"float"`):
            - Для панели снимаются ограничения по максимальному размеру, устанавливается минимальный размер (200x200 пикселей).
            - Фиксация размеров отключается, что позволяет пользователю свободно изменять размеры панели.

        Такой подход обеспечивает согласованное и ожидаемое поведение пользовательского интерфейса для различных режимов отображения панели.


        """
        # ✅ Реализовано: 30.06.2025
        # Получаем геометрию экрана
        screen = QApplication.primaryScreen().availableGeometry()
        # Если панель должна быть слева
        if self.dock_position == "left":
            self.setGeometry(QRect(
                screen.left() + self.dock_margin,  # X координата
                screen.top(),  # Y координата
                300,  # Ширина
                screen.height()  # Высота
            ))
            self.setFixedWidth(300)  # Фиксируем ширину в закрепленном режиме
            self.setFixedHeight(screen.height())  # Фиксируем высоту
            # Если панель должна быть справа
        elif self.dock_position == "right":
            self.setGeometry(QRect(
                screen.right() - 300 - self.dock_margin,  # X координата
                screen.top(),  # Y координата
                300,  # Ширина
                screen.height()  # Высота
            ))
            self.setFixedWidth(300)  # Фиксируем ширину в закрепленном режиме
            self.setFixedHeight(screen.height())  # Фиксируем высоту
            # Для режима float не устанавливаем фиксированные размеры
        elif self.dock_position == "float":
            self.setMinimumSize(200, 200)
            self.setMaximumSize(16777215, 16777215)
            self.setFixedSize(QSize())  # Снимаем фиксированные размеры

    # Метод обновления состояния пунктов меню
    def _update_menu_checks(self):
        """
            Обновляет состояние чекбоксов (флажков) в меню управления положением боковой панели.

            Для каждой из возможных позиций панели (слева, справа, плавающее положение) устанавливает соответствующий чекбокс в активное состояние, если текущая позиция панели совпадает c данной.
            Это обеспечивает корректное отображение состояния меню в зависимости от текущего положения боковой панели пользователя.

            - Если панель закреплена слева, активируется пункт 'Pin Left'.
            - Если панель закреплена справа, активируется пункт 'Pin Right'.
            - Если панель находится в плавающем режиме, активируется пункт 'Float'.

            Таким образом, метод синхронизирует визуальное состояние пунктов меню с реальным положением панели.

        """
        # ✅ Реализовано: 30.06.2025
        self.pin_left_action.setChecked(self.dock_position == "left")
        self.pin_right_action.setChecked(self.dock_position == "right")
        self.float_action.setChecked(self.dock_position == "float")

    def show_context_menu(self, pos):
        # ✅ Реализовано: 11.08.2025
        # Показываем меню в указанной позиции
        self.position_menu.exec(self.mapToGlobal(pos))

    def _setup_screen_edge_docking(self):
        """Настройка прикрепления к краям экрана"""
        # ✅ Реализовано: 30.06.2025
        # Позиция по умолчанию - справа
        self.dock_position = "right"  # left/right/float
        # Отступ от края экрана
        self.dock_margin = 5

        self.setWindowFlags(self.windowFlags())
        # Обновляем позицию
        self.update_dock_position()
        # Устанавливаем прозрачность окна
        self.setWindowOpacity(0.9)

    def set_manedger(self,tree_model_manager:TreeModelManager):
        self.tree_model_manager = tree_model_manager

    @property
    def template_name(self):
        """Возвращает имя шаблона (только для чтения)"""
        return self._template_name

    def closeEvent(self, event):
        """Обработчик закрытия окна с полной очисткой ресурсов"""
        try:
            print("Начинаем очистку SidePanel...")

            # 1. Отключаем все сигналы
            self._disconnect_all_signals()

            # 2. НЕ останавливаем BackgroundParser - это синглтон!
            # Он используется другими компонентами приложения

            # 3. Останавливаем файловый вотчер (корректно)
            if hasattr(self, 'file_watcher'):
                try:
                    # Правильный способ остановки FileWatcher
                    if hasattr(self.file_watcher, 'stop_watching'):
                        self.file_watcher.stop_watching()
                    self.file_watcher.deleteLater()
                except Exception as e:
                    print(f"Ошибка при остановке file_watcher: {e}")

            # 4. Очищаем TreeModelManager от ссылок на этот экземпляр
            if hasattr(self, 'tree_model_manager'):
                try:
                    # Удаляем регистрацию tab_widget
                    if 'side_panel' in self.tree_model_manager.tab_widgets:
                        del self.tree_model_manager.tab_widgets['side_panel']

                    # Удаляем приоритет
                    if hasattr(self.tree_model_manager, 'widget_priorities'):
                        self.tree_model_manager.widget_priorities = [
                            name for name in self.tree_model_manager.widget_priorities
                            if name != 'side_panel'
                        ]

                    # Удаляем модели этого окна
                    tabs_to_remove = []
                    current_tab_names = getattr(self, 'tab_names', {})
                    for tab_name in list(self.tree_model_manager.tab_models.keys()):
                        if tab_name in current_tab_names:
                            tabs_to_remove.append(tab_name)

                    for tab_name in tabs_to_remove:
                        del self.tree_model_manager.tab_models[tab_name]

                    # Очищаем связи файлов с вкладками этого окна
                    if hasattr(self.tree_model_manager, 'file_to_tabs'):
                        for file_path in list(self.tree_model_manager.file_to_tabs.keys()):
                            if file_path in self.tree_model_manager.file_to_tabs:
                                self.tree_model_manager.file_to_tabs[file_path] = [
                                    tab for tab in self.tree_model_manager.file_to_tabs[file_path]
                                    if tab not in current_tab_names
                                ]
                                if not self.tree_model_manager.file_to_tabs[file_path]:
                                    del self.tree_model_manager.file_to_tabs[file_path]
                except Exception as e:
                    print(f"Ошибка при очистке TreeModelManager: {e}")

            # 5. Очищаем менеджер вкладок (корректно)
            if hasattr(self, 'tab_manager'):
                try:
                    # Вместо cleanup() очищаем вручную
                    if hasattr(self.tab_manager, 'trees'):
                        for tree_name, tree in list(self.tab_manager.trees.items()):
                            try:
                                # Отключаем сигналы от деревьев
                                if hasattr(tree, 'clicked'):
                                    try:
                                        tree.clicked.disconnect()
                                    except:
                                        pass
                                tree.deleteLater()
                            except:
                                pass
                        self.tab_manager.trees.clear()

                    if hasattr(self.tab_manager, 'tab_widget'):
                        try:
                            # Отключаем сигналы от tab_widget
                            if hasattr(self.tab_manager.tab_widget, 'currentChanged'):
                                try:
                                    self.tab_manager.tab_widget.currentChanged.disconnect()
                                except:
                                    pass
                            self.tab_manager.tab_widget.deleteLater()
                        except:
                            pass
                except Exception as e:
                    print(f"Ошибка при очистке tab_manager: {e}")

            # 6. Очищаем toolbar manager
            if hasattr(self, 'toolbar_manager'):
                try:
                    if hasattr(self.toolbar_manager, 'editor_toggled'):
                        try:
                            self.toolbar_manager.editor_toggled.disconnect()
                        except:
                            pass
                    self.toolbar_manager.deleteLater()
                except Exception as e:
                    print(f"Ошибка при очистке toolbar_manager: {e}")

            # 7. Очищаем UI компоненты
            self._cleanup_ui_components()

            # 8. Удаляем все дочерние виджеты
            for child in self.findChildren(QWidget):
                if child != self:
                    try:
                        child.deleteLater()
                    except:
                        pass

            # 9. Очищаем layout
            if self.layout():
                try:
                    QWidget().setLayout(self.layout())
                except:
                    pass

            # 10. Очищаем ссылки на менеджеры
            if hasattr(self, 'tree_model_manager'):
                self.tree_model_manager = None
            if hasattr(self, 'tab_manager'):
                self.tab_manager = None
            if hasattr(self, 'toolbar_manager'):
                self.toolbar_manager = None
            if hasattr(self, 'file_watcher'):
                self.file_watcher = None

            # 11. Очищаем кэш контента для этого экземпляра (только файлы этого окна)
            #FIXME - 21/09/2025 Это костыль. проблема тут. Данные из кэш мешают повторно открыться окну
            if hasattr(self, 'content_cache') and hasattr(self, 'tab_names'):
                try:
                    for tab_name, file_paths in self.tab_names.items():
                        for file_path in file_paths:
                            if self.content_cache.get(file_path):
                                self.content_cache.remove(file_path)
                except Exception as e:
                    print(f"Ошибка при очистке кэша контента: {e}")
            #---Конец пророблеме тут

            print("🚨🚨🚨SidePanel закрыт, ресурсы очищены🚨🚨🚨")

        except Exception as e:
            print(f"Критическая ошибка при закрытии SidePanel: {e}")
            import traceback
            traceback.print_exc()

        finally:
            # Всегда принимаем событие закрытия
            event.accept()

    def _disconnect_all_signals(self):
        """Отключает все подключенные сигналы"""
        try:
            if hasattr(self, 'background_parser'):
                try:
                    self.background_parser.task_finished.disconnect(self._on_parsing_done)
                except:
                    pass

            if hasattr(self, 'tree_model_manager'):
                try:
                    self.tree_model_manager.model_updated.disconnect(self._on_model_updated)
                except:
                    pass

            if hasattr(self, 'tab_manager') and hasattr(self.tab_manager, 'tab_created'):
                try:
                    self.tab_manager.tab_created.disconnect(self._on_fill_tab_tree)
                except:
                    pass

            if hasattr(self, 'file_watcher'):
                try:
                    self.file_watcher.file_updated.disconnect(self._on_file_updated)
                    self.file_watcher.file_deleted.disconnect(self._on_file_deleted)
                    self.file_watcher.dir_changed.disconnect(self._on_dir_changed)
                except:
                    pass

            if hasattr(self, 'toolbar_manager') and hasattr(self.toolbar_manager, 'editor_toggled'):
                try:
                    self.toolbar_manager.editor_toggled.disconnect(self._open_editor)
                except:
                    pass

            # Отключаем сигналы контроллера выделения
            if hasattr(self, 'tree_model_manager') and hasattr(self.tree_model_manager, 'selection_controller'):
                controller = self.tree_model_manager.selection_controller
                try:
                    controller.content_for_sidepanel.disconnect(self.on_display_content)
                    controller.selection_changed.disconnect(self.on_update_selection_status)
                    controller.error_occurred.disconnect(self.on_show_selection_error)
                except:
                    pass

        except Exception as e:
            print(f"Ошибка при отключении сигналов: {e}")

    def _cleanup_ui_components(self):
        """Очищает все UI компоненты"""
        # Очищаем content_viewer
        if hasattr(self, 'content_viewer'):
            try:
                self.content_viewer.set_content("")
                self.content_viewer.deleteLater()
            except:
                pass

        # Очищаем splitter
        if hasattr(self, 'splitter'):
            try:
                self.splitter.deleteLater()
            except:
                pass

        # Очищаем tab_widget
        if hasattr(self, 'tab_widget'):
            try:
                self.tab_widget.deleteLater()
            except:
                pass

        # Очищаем деревья
        if hasattr(self, 'tab_manager') and hasattr(self.tab_manager, 'trees'):
            for tree in self.tab_manager.trees.values():
                try:
                    tree.deleteLater()
                except:
                    pass
            self.tab_manager.trees.clear()

