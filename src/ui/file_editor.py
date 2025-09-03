from src.observers.my_base_observer import MyBaseObserver
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QMainWindow, QTreeView, QTabWidget, QTextEdit, QVBoxLayout, QWidget, QSplitter)
from src.widgets.markdown_viewer_widget import MarkdownViewer
class FileEditorWindowObserver(MyBaseObserver):
    # ✅ Реализовано: 30.06.2025
    def __init__(self):
        super().__init__()



class FileEditorWindow(QMainWindow):
    """
        Главное окно редактора файлов с поддержкой форматов .st и .md.
        Обеспечивает создание, редактирование и сохранение файлов.
    """
    def __init__(self,parent = None ):
        super().__init__(parent)
        self.parent = parent
        self.tree_view = QTreeView()
        # Создаем экземпляр класса для сигналов
        self.observer = FileEditorWindowObserver()

        self.setWindowTitle("Редактор файлов")
        self.setMinimumSize(800,500)

        if self.parent.tree_model_manager and self.parent.toolbar_manager:
            self._setup_managers(self.parent.tree_model_manager, self.parent.toolbar_manager)

    def _init_ui(self):
        """Инициализация пользовательского интерфейса"""
        main_widget = QWidget()                          # Создаем центральный виджет окна
        self.setCentralWidget(main_widget)               # Устанавливаем его как центральный виджет окна
        main_layout = QVBoxLayout(main_widget)                # Создаем вертикальный layout для основного виджета
        main_layout.setContentsMargins(5, 5, 5, 5)            # Устанавливаем минимальные отступы layout

        # Разделитель для дерева и редактора
        self.splitter = QSplitter(Qt.Vertical)  # Вертикальный разделитель

        # Создаем панель инструментов над деревом
        toolbar_to_tree_layout = self.toolbar_manager.get_above_tree_toolbar_editor()
        main_layout.addWidget(toolbar_to_tree_layout)

        # Добавляем tab_widget с всеми вкладками
        main_layout.addWidget(self.tab_widget)

        # Текстовый редактор и другие элементы...
        self.text_editor = QTextEdit()
        self.text_editor.setAcceptRichText(False)  # Режим plain text  Отключаем форматированный текст



        # Контейнер для редактора и кнопок
        editor_container = QWidget()  # Контейнерный виджет
        editor_layout = QVBoxLayout(editor_container)  # Вертикальный layout
        editor_layout.setContentsMargins(0, 0, 0, 0)  # Без отступов
        editor_layout.setSpacing(0)  # Без промежутков

        # Создаем панель инструментов над редактаром
        editor_toolbar = self.toolbar_manager.get_editor_toolbar()

        # Добавляем кнопки над редактором
        editor_layout.addWidget(editor_toolbar)
        editor_layout.addWidget(self.text_editor)




        #Добавляем разделитель
        #self.splitter.addWidget(self.tree_view)
        self.splitter.addWidget(editor_container)
        # Добавляем разделитель в основной layout
        main_layout.addWidget(self.splitter)

        #main_layout.addWidget(self.text_editor)

        # Подключаем сигналы
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        # Подключаемся к сигналу обновления моделей
        self.tree_model_manager.model_updated.connect(self._on_model_updated)

    def  _setup_managers(self, tree_model_manager, toolbar_manager):
        """Устанавливает менеджеры и инициализирует интерфейс"""
        # TODO 🚧 В разработке: 02.09.2025
        if not tree_model_manager or not toolbar_manager:
            raise ValueError("tree_model_manager и toolbar_manager обязательны")
        self.tree_model_manager = tree_model_manager
        self.toolbar_manager = toolbar_manager

        # Получаем ВСЕ модели из менеджера
        self.all_models = tree_model_manager.get_model()  # Это словарь {tab_name: model}

        # Создаем QTabWidget для отображения всех вкладок
        self.tab_widget = QTabWidget()

        # Добавляем каждую модель как отдельную вкладку
        for tab_name, model in self.all_models.items():
            tree_view = QTreeView()
            tree_view.setModel(model)
            tree_view.header().hide()  # Скрываем заголовок колонки
            self.tab_widget.addTab(tree_view, tab_name)


        # Устанавливаем активную вкладку как в SidePanel
        active_info = tree_model_manager.get_active_tab_info()
        if active_info:
            self.tab_widget.setCurrentIndex(
            list(self.all_models.keys()).index(active_info['tab_name'])
            )

        self._init_ui()

    def _connect_selection_signals(self):
        """Подключает сигналы контроллера выделения"""
        controller = self.tree_model_manager.selection_controller
        controller.content_requested.connect(self.on_display_content)
        controller.error_occurred.connect(self.on_show_selection_error)

        print("Сигналы контроллера выделения подключены")

    def _refresh_view_for_file(self, model, file_path):
        """Принудительно обновляет view для конкретного файла"""
        # TODO 🚧 В разработке: 02.09.2025 не понял этот метод
        # Ищем индекс файла в модели
        for row in range(model.rowCount()):
            index = model.index(row, 0)
            if index.isValid():
                item = index.internalPointer()
                if (item and len(item.item_data) > 2 and
                        item.item_data[2] == file_path):

                    # Обновляем конкретный элемент
                    model.dataChanged.emit(index, index)

                    # Если элемент раскрыт - обновляем всю ветку
                    if self.tree_view.isExpanded(index):
                        top_left = model.index(0, 0, index)
                        bottom_right = model.index(model.rowCount(index) - 1, 0, index)
                        model.dataChanged.emit(top_left, bottom_right)

                    print(f"DEBUG: Обновлен view для файла {file_path}")
                    return

        print(f"DEBUG: Файл {file_path} не найден для обновления view")

    def _on_model_updated(self, tab_name, file_path):
        """Обработчик обновления модели - автоматическая синхронизация!"""
        # TODO 🚧 В разработке: 02.09.2025 не понял этот метод
        print(f"DEBUG: Модель обновлена - вкладка: {tab_name}, файл: {file_path}")

        try:
            # Проверяем существование модели для этой вкладки
            if tab_name not in self.all_models:
                print(f"DEBUG: Модель для вкладки '{tab_name}' не найдена")
                return

            model = self.all_models[tab_name]

            # Если это текущая активная вкладка - обновляем view
            current_tab_index = self.tab_widget.currentIndex()
            if current_tab_index >= 0:
                current_tab_name = self.tab_widget.tabText(current_tab_index)
                if current_tab_name == tab_name:
                    self._refresh_view_for_file(model, file_path)

            # Можно добаditional логику:
            # - Обновить статусбар
            # - Показать уведомление
            # - Записать в лог

        except Exception as e:
            print(f"Ошибка в _on_model_updated: {e}")
            import traceback
            traceback.print_exc()



    def _on_tab_changed(self, index):
        """
        Обрабатывает переключение между вкладками в FileEditorWindow
        и синхронизирует состояние с другими окнами

        Args:
            index (int): Индекс новой активной вкладки
        """
        # TODO 🚧 В разработке: 02.09.2025 не понял этот метод
        # Проверяем валидность индекса
        if index < 0 or index >= self.tab_widget.count():
            return

        # Получаем имя вкладки
        tab_name = self.tab_widget.tabText(index)
        print(f"DEBUG: Переключена вкладка: {tab_name}")

        # 1. Синхронизация с TreeModelManager
        active_info = self.tree_model_manager.get_active_tab_info()
        if active_info and active_info['tab_name'] != tab_name:
            # Устанавливаем активную вкладку в менеджере
            #self.tree_model_manager.set_active_tab(tab_name)
            pass

        # 2. Обновление UI
        self.setWindowTitle(f"Редактор файлов - {tab_name}")

        # 3. Получаем модель для текущей вкладки
        current_model = self.all_models.get(tab_name)
        if current_model:
            # Обновляем содержимое редактора на основе выбранного элемента
            selected_indexes = self.tree_view.selectedIndexes()
            if selected_indexes:
                self._on_tree_selection_changed(selected_indexes[0])  # TODO тут будет ошибка
            else:
                self.text_editor.clear()

        # 4. Обновление статусбара
        file_count = current_model.rowCount() if current_model else 0
        self.statusBar().showMessage(
            f"Вкладка: {tab_name} | Файлов: {file_count} | Готово"
        )

        # 5. Логирование для отладки
        print(f"DEBUG: Активна вкладка '{tab_name}', модель: {current_model is not None}")

    def _on_tree_selection_changed(self):
        # взять данные из полного кэш
        pass

    def on_display_content(self, content_type, content):
        """Отображает контент в редакторе"""
        # TODO 🚧 В разработке: 30.08.2025

        # Очищаем предыдущее содержимое редактора


        # Обработка разных типов элементов
        if content_type == 'template':
            pass
        elif content_type == 'markdown':
            pass