from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTabWidget,
                               QTreeWidget,QApplication,
                                QMenu)
from PySide6.QtGui import QAction

from parsers.content_cache import ContentCache
from src.managers.dynamic_tabs import DynamicTabManager
from src.observers.file_watcher import FileWatcher
from src.observers.my_base_observer import MyBaseObserver
from src.widgets.markdown_viewer_widget import MarkdownViewer
from PySide6.QtCore import Qt, QRect, QSize
from src.managers.ui_manager import UIManager
from src.managers.toolbar_manager import ToolbarManager
from src.operation.file_operations import FileOperations
from src.managers.tree_model_manager import TreeModelManager
from src.parsers.background_parser import BackgroundParser,Priority
from src.parsers.file_parser_service import FileParserService
from src.parsers.metadata_cache import MetadataCache

class SidePanelObserver(MyBaseObserver):
    # ✅ Реализовано: 29.06.2025
    def __init__(self):
        super().__init__()
class SidePanel(QWidget):
    # TODO 🚧 В разработке: 08.08.2025
        # 🏆task: Создание боковой панели;
        # 🏆task: Открыть боковую панель из стартовой панели;
    def __init__(self,parent=None):
        """
            Инициализация боковой панели с динамическими вкладками

            Args:
                tab_names: Список имен для вкладок (например, ["Documents", "Projects"])
                parent: Родительский виджет
        """
        # TODO 🚧 В разработке: 08.08.2025
        super().__init__(parent, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        # Инициализация основных атрибутов
        self.observer = SidePanelObserver()
        self.file_operation = FileOperations()

        # Получаем данные для вкладок
        self.tab_names = self.file_operation.fetch_file_heararchy()
        if not isinstance(self.tab_names, dict):
            #QMessageBox.warning(self, "Ошибка", "Некорректные данные для вкладок")  Перенести на собственый класс сообщений
            self.tab_names = {"Documents": []}  # fallback

        # Инициализация менеджеров
        self._init_managers()
        # Инициализация наблюдателей
        self._init_observers()
        # рисуем интерфейс
        self._init_ui()
        # Инициализация сигналов
        self._connect_signals()


        # Инициализация контекстного меню для управления позицией
        self._init_position_menu()
        # Настройка прикрепления к краям экрана
        self._setup_screen_edge_docking()
        self.setAttribute(Qt.WA_ShowWithoutActivating)

    def _init_ui(self)->None:
        """Инициализация пользовательского интерфейса"""
        # TODO 🚧 В разработке: 08.08.2025
        # Устанавливаем минимальную ширину панели
        self.setMinimumWidth(300)

        self.ui = UIManager()
        self.tree_manager = None # TreeManager(self.tree_view)


        # Создаем разделитель с вертикальной ориентацией
        self.splitter = self.ui.create_splitter(Qt.Vertical,
                                                sizes=[300, 100],
                                                handle_width=5,
                                                handle_style="QSplitter::handle { background: #ccc; }")

        # Создаем основной вертикальный layout
        main_layout = QVBoxLayout(self)
        # Убираем отступы у layout
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Создаем toolbar manager с правильными зависимостями
        self.toolbar_manager = ToolbarManager(self.tree_manager, self.close, self.showMinimized)

        # Создаем панель заголовка с кнопками управления
        title_layout = self.toolbar_manager.get_title_layout()
        main_layout.addWidget(title_layout)  # Добавляем панель инструментов в основной layout(макет)

        # Создаем виджет вкладок
        self.tab_widget = self.tab_manager.tab_widget
        self.tab_widget.setTabPosition(QTabWidget.West)  # Вкладки слева

        # Создаем деревья для каждой вкладки
        self._create_tabs_with_trees(self.tab_names)

        # Добавляем вкладки в основной layout
        main_layout.addWidget(self.tab_widget)

        # нижняя панель (отображение данных)
        self.content_viewer = MarkdownViewer()
        # Текстовое поле (нижняя часть)
        self.splitter.addWidget(self.content_viewer)
        # Добавляем разделитель в основной layout
        main_layout.addWidget(self.splitter)

    def _init_managers(self)->None:
        """Инициализация всех менеджеров и сервисов"""
        # ✅ Реализовано: 20.08.2025
        # 1. Создаем кэш (синглтон)
        self.metadata_cache = MetadataCache()
        self.content_cache = ContentCache()  # Инициализация кэша

        # 2. Создаем парсер сервис
        self.parser_service = FileParserService()

        # 3. Создаем менеджер моделей с зависимостями
        self.tree_model_manager = TreeModelManager(
            parser_service=self.parser_service,
            metadata_cache=self.metadata_cache,
            content_cache=self.content_cache
        )

        # 4. Создаем фоновый парсер
        self.background_parser = BackgroundParser(
            parser_service=self.parser_service,
            content_cache=self.content_cache
        )
        # 5. Создаем менеджер вкладок
        self.tab_manager = DynamicTabManager()
        # ВРЕМЕННО
        print(f"Тип tab_created: {type(self.tab_manager.tab_created)}")
        print(f"Это Signal? {hasattr(self.tab_manager.tab_created, 'connect')}")
        #------ ВРЕМЕННО КОНЕЦ
        # 6. Сразу подключаем сигнал, который должен работать ДО создания UI
        self.tab_manager.tab_created.connect(self._on_fill_tab_tree)

    def _init_observers(self)->None:
        """Инициализация наблюдателей"""
        self.file_watcher = FileWatcher()
        self.file_watcher.file_updated.connect(self._on_file_updated)
        self.file_watcher.file_deleted.connect(self._on_file_deleted)
        self.file_watcher.dir_changed.connect(self._on_dir_changed)
    def _create_tabs_with_trees(self, tab_name:dict):
        # ✅ Реализовано: 14.08.2025
        """Создает вкладки с деревьями файлов"""
        self.tab_manager.create_tabs(tab_name)

    def _connect_signals(self):
        """Подключение сигналов"""
        # ВРЕМЕННО
        print("Подключаем сигналы...")
        # ------ ВРЕМЕННО КОНЕЦ
        self.toolbar_manager.editor_toggled.connect(self._open_editor)
        self.background_parser.task_finished.connect(self._on_parsing_done)
        # ВРЕМЕННО
        print("Сигналы подключены")
        # ------ ВРЕМЕННО КОНЕЦ
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

    def _on_fill_tab_tree(self,tab_name: str, tree: QTreeWidget):
        """Заполняет дерево файлами из словаря tab_names."""
        # TODO 🚧 В разработке: 13.08.2025
        try:
            if tab_name not in self.tab_names:
                return

            # 1. Получаем пути файлов для этой вкладки
            file_paths = self.tab_names[tab_name]  # Например: ["/path/file1.st", ...]

            # 2. Запрашиваем модель с метаданными
            model = self.tree_model_manager.build_model_for_tab(tab_name, file_paths)

            # 3. Привязываем модель к дереву
            if model:
                tree.setModel(model)

            # 4. Запускаем фоновый парсинг
            for file_path in file_paths:
                # Проверяем, нет ли уже полных данных (на всякий случай)
                if not self.content_cache.get(file_path):
                    # Ставим в очередь на фоновый парсинг ТОЛЬКО те файлы,
                    # которых еще нет в content_cache
                    # ВРЕМЕННО
                    print(f"Добавляем в фоновый парсинг: {file_path}")
                    # ----------ВРЕМЕННО КОНЕЦ
                    self.background_parser.add_task(file_path, Priority.VISIBLE)
                else:
                    print(f"Не удалось создать модель для вкладки {tab_name}")
                    # ВРЕМЕННО
                    print(f"Файл уже в кэше: {file_path}")
                    # ----------ВРЕМЕННО КОНЕЦ
        except Exception as e:
            print(f"Ошибка при заполнении дерева для вкладки {tab_name}: {e}")

    def _on_parsing_done(self, file_path: str, parsed_data: dict):
        """Обработчик завершения фонового парсинга"""
        # ВРЕМЕННО
        print(f"Парсинг завершен для: {file_path}")
        print(f"Данные: {list(parsed_data.keys()) if parsed_data else 'None'}")
        #----------ВРЕМЕННО КОНЕЦ

        # 1. Сохраняем в кэш
        self.content_cache.set(file_path, parsed_data)

        # 2. Находим все вкладки, где есть этот файл
        for tab_name, file_paths in self.tab_names.items():
            if file_path in file_paths:
                # 3. Обновляем соответствующую модель
                if tab_name in self.tree_model_manager.tab_models:
                    self.tree_model_manager.update_model(tab_name, file_path)

                    # 4. Принудительно обновляем view
                    model = self.tree_model_manager.tab_models[tab_name]
                    model.layoutChanged.emit()


    def _open_editor(self):
        """Открыть окно редактора файла"""
        pass

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
        self.update_dock_position = "float"
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

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)  # <- ОТКЛЮЧАЕМ поверх всех окон
        # Обновляем позицию
        self.update_dock_position()
        # Устанавливаем прозрачность окна
        self.setWindowOpacity(0.9)

    def set_manedger(self,tree_model_manager:TreeModelManager):
        self.tree_model_manager = tree_model_manager