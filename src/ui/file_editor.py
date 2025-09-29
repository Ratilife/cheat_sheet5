from pathlib import Path
import os

from PySide6.QtGui import QAction

from editor.base_editor import BaseFileEditor
from editor.editor_factory import EditorFactory
from src.observers.my_base_observer import MyBaseObserver
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QMainWindow, QTreeView, QTabWidget, QTextEdit, QVBoxLayout, QWidget, QSplitter,
                               QHBoxLayout, QLabel, QLineEdit, QToolBar)
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
    def __init__(self, parent = None):
        super().__init__(parent)
        self.parent = parent
        self.tree_view = QTreeView()
        # Создаем экземпляр класса для сигналов
        self.observer = FileEditorWindowObserver()

        self.template_name = "Тут будет текст"
        self.setWindowTitle("Редактор файлов")
        self.setMinimumSize(800, 500)

        self.tree_model_manager = None
        self.toolbar_manager = None
        self.toolbar_to_tree_layout = None

        self._create_editor_actions()

        if (self.parent and hasattr(self.parent, 'tree_model_manager') and
                hasattr(self.parent, 'toolbar_manager')):
            self._setup_managers(self.parent.tree_model_manager, self.parent.toolbar_manager)

        self.setAttribute(Qt.WA_DeleteOnClose)  # Важно: уничтожать объект при закрытии


    def _init_ui(self):
        """Инициализация пользовательского интерфейса"""
        main_widget = QWidget()                          # Создаем центральный виджет окна
        self.setCentralWidget(main_widget)               # Устанавливаем его как центральный виджет окна
        main_layout = QVBoxLayout(main_widget)                # Создаем вертикальный layout для основного виджета
        main_layout.setContentsMargins(5, 5, 5, 5)            # Устанавливаем минимальные отступы layout
        main_layout.setSpacing(5)                        # Устанавливаем промежуток между виджетами


        # Создаем горизонтальный разделитель для дерева и редактора
        self.main_splitter = QSplitter(Qt.Horizontal)  # Горизонтальный разделитель!

        #  Контейнер для дерева файлов (вкладок)
        tree_container = QWidget()
        tree_layout = QVBoxLayout(tree_container)
        tree_layout.setContentsMargins(0, 0, 0, 0)
        tree_layout.setSpacing(0)

        # Добавляем tab_widget с всеми вкладками
        tree_layout.addWidget(self.tab_widget)

        # Контейнер с деревом добавлен в разделитель
        self.main_splitter.addWidget(tree_container)



        # Создаем панель инструментов над деревом
        if self.toolbar_to_tree_layout:
            main_layout.addWidget(self.toolbar_to_tree_layout)



        # Контейнер для редактора и кнопок
        editor_container = QWidget()  # Контейнерный виджет
        editor_layout = QVBoxLayout(editor_container)  # Вертикальный layout
        editor_layout.setContentsMargins(0, 0, 0, 0)  # Без отступов
        editor_layout.setSpacing(0)  # Без промежутков

        # Создаем горизонтальный контейнер для панели инструментов и имени шаблона
        toolbar_template_container = QWidget()
        toolbar_template_layout = QHBoxLayout(toolbar_template_container)
        toolbar_template_layout.setContentsMargins(0, 0, 0, 0)
        toolbar_template_layout.setSpacing(5)

        # Создаем панель инструментов над редактаром
        self.editor_toolbar = self.toolbar_manager.get_editor_toolbar()
        toolbar_template_layout.addWidget(self.editor_toolbar)

        #  Поле для отображения и редактирования template_name в той же строке
        template_label = QLabel()
        self.template_edit = QLineEdit(self.template_name)
        self.template_edit.textChanged.connect(self._on_template_changed)

        # Добавляем растягивающее пространство между toolbar и template
        toolbar_template_layout.addStretch()  # Добавляем растягивающее пространство

        toolbar_template_layout.addWidget(template_label)
        toolbar_template_layout.addWidget(self.template_edit)

        #  Добавляем общий контейнер в editor_layout
        editor_layout.addWidget(toolbar_template_container)

        # Текстовый редактор и другие элементы...
        self.text_editor = QTextEdit()
        self.text_editor.setAcceptRichText(False)  # Режим plain text  Отключаем форматированный текст
        editor_layout.addWidget(self.text_editor)

        #Добавляем разделитель
        self.main_splitter.addWidget(editor_container)

        # Устанавливаем начальные пропорции (дерево 30%, редактор 70%)
        self.main_splitter.setSizes([300, 700])

        #  Разрешаем пользователю изменять размеры
        self.main_splitter.setChildrenCollapsible(False)  # Не позволяем полностью скрывать части

        # Добавляем разделитель в основной layout
        main_layout.addWidget(self.main_splitter)

        #main_layout.addWidget(self.text_editor)

        # Сохраняем ссылку на layout редактора
        self.editor_layout = editor_layout  # или тот layout, куда добавляется редактор

        # Подключаем сигналы
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        # Подключаемся к сигналу обновления моделей
        if self.tree_model_manager:
            self.tree_model_manager.model_updated.connect(self._on_model_updated)

    def _setup_managers(self, tree_model_manager, toolbar_manager):
        """Устанавливает менеджеры и инициализирует интерфейс"""
        # TODO 🚧 В разработке: 02.09.2025
        if not tree_model_manager or not toolbar_manager:
            raise ValueError("tree_model_manager и toolbar_manager обязательны")
        self.tree_model_manager = tree_model_manager
        self.toolbar_manager = toolbar_manager

        self.toolbar_to_tree_layout = self.toolbar_manager.get_above_tree_toolbar_editor()

        # Получаем ВСЕ модели из менеджера
        self.all_models = tree_model_manager.get_model()  # Это словарь {tab_name: model}

        # Создаем QTabWidget для отображения всех вкладок
        self.tab_widget = QTabWidget()

        # Словарь для хранения tree_view по именам вкладок
        self.tree_views = {}

        # Добавляем каждую модель как отдельную вкладку
        for tab_name, model in self.all_models.items():
            tree_view = QTreeView()
            tree_view.setModel(model)
            tree_view.header().hide()  # Скрываем заголовок колонки
            self.tab_widget.addTab(tree_view, tab_name)
            self.tree_views[tab_name] = tree_view  # Сохраняем ссылку

        # ПОДКЛЮЧАЕМ КОНТРОЛЛЕР К ДЕРЕВЬЯМ - ВАЖНО!
        #self.tree_model_manager.connect_tree_views(self.tree_views)

        for tab_name, tree_view in self.tree_views.items():
            self.tree_model_manager.selection_controller.connect_tree_view(tree_view, "editor")

        # ПОДКЛЮЧАЕМ СИГНАЛЫ КОНТРОЛЛЕРА
        self._connect_selection_signals()

        # Устанавливаем активную вкладку как в SidePanel
        active_info = self.parent.tab_manager.get_active_tab_info()   #TODO 17/09/2025 изменить TreeModelManager
        if active_info:
            tab_names = list(self.all_models.keys())
            if active_info['tab_name'] in tab_names:
                self.tab_widget.setCurrentIndex(tab_names.index(active_info['tab_name']))

        self._init_ui()


    def _connect_selection_signals(self):
        """Подключает сигналы контроллера выделения"""
        self.controller = self.tree_model_manager.selection_controller
        self.controller.content_for_editor.connect(self.on_display_content) #тут получаем данные
        #controller.error_occurred.connect(self.on_show_selection_error)
        self.controller.selection_changed.connect(self.on_selection_changed) # тут обработка выбранного элемента

        # Устанавливаем источник для контроллера
        self.controller.current_source = "editor"
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
        Слот-обработчик сигнала currentChanged от QTabWidget.
        Вызывается автоматически в двух случаях:
            1. ✅ При ПРЯМОМ ВЗАИМОДЕЙСТВИИ ПОЛЬЗОВАТЕЛЯ: клик на другую вкладку
            2. ✅ При ПРОГРАММНОМ ИЗМЕНЕНИИ ВКЛАДКИ: вызов tab_widget.setCurrentIndex()

            ВКЛЮЧАЯ первоначальную установку вкладки при создании окна в _setup_managers().

            Обрабатывает переключение между вкладками в FileEditorWindow
            и синхронизирует состояние с другими окнами.

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
        #active_info = self.tree_model_manager.get_active_tab_info()


        # 2. Обновление UI
        self.setWindowTitle(f"Редактор файлов - {tab_name}")

        # 3. Получаем модель для текущей вкладки
        current_model = self.all_models.get(tab_name)


        # 4. Обновление статусбара
        # TODO 05.09.2025 технически правильно, но логически неверно
        file_count = current_model.rowCount() if current_model else 0
        self.statusBar().showMessage(
            f"Вкладка: {tab_name} | Файлов: {file_count} | Готово"
        )

        # 5. Логирование для отладки
        print(f"DEBUG: Активна вкладка '{tab_name}', модель: {current_model is not None}")

    def _create_editor_actions(self):
        """Создает базовые действия для редактора"""
        # Действие "Сохранить"
        self.save_action = QAction("Сохранить", self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.triggered.connect(self._on_save_action)
        self.save_action.setEnabled(False)  # Изначально отключено

        # Действие "Отменить"
        self.undo_action = QAction("Отменить", self)
        self.undo_action.setShortcut("Ctrl+Z")
        self.undo_action.triggered.connect(self._on_undo_action)

        # Действие "Повторить"
        self.redo_action = QAction("Повторить", self)
        self.redo_action.setShortcut("Ctrl+Y")
        self.redo_action.triggered.connect(self._on_redo_action)

    def _on_save_action(self):
        """Обработчик действия Сохранить"""
        if hasattr(self, 'current_editor') and self.current_editor:
            success = self.current_editor.save()
            if success:
                print("DEBUG: Файл успешно сохранен")
            else:
                print("DEBUG: Ошибка при сохранении файла")

    def _on_undo_action(self):
        """Обработчик действия Отменить"""
        if hasattr(self, 'current_editor') and self.current_editor:
            # TODO: 29.09.2025 Реализуйте отмену в конкретных редакторах
            print("DEBUG: Действие 'Отменить'")

    def _on_redo_action(self):
        """Обработчик действия Повторить"""
        if hasattr(self, 'current_editor') and self.current_editor:
            # TODO: 29.09.2025 Реализуйте повтор в конкретных редакторах
            print("DEBUG: Действие 'Повторить'")

    def on_display_content(self, content_type, content,path_file):
        """Отображает контент в редакторе"""
        # TODO 🚧 В разработке: 30.08.2025

        # Проверяем, активно ли это окно
        if not self.isVisible():
            return

        try:
            print("👍 Работает метод on_display_content()")
            # 1. Создаем appropriate редактор через фабрику
            editor = EditorFactory.create_editor_for_type(content_type, self)

            if editor is None:
                raise ValueError(f"Не удалось создать редактор для типа: {content_type}")

            # 2. Устанавливаем контент в редактор
            editor.set_content(content)

            # 3. Заменяем текущий редактор в UI
            self._set_current_editor(editor)

            # 4. Обновляем статус
            self.statusBar().showMessage(f"Загружен контент типа: {content_type}")
        except Exception as e:
            print(f"Ошибка при отображении контента: {e}")
            self.statusBar().showMessage(f"Ошибка загрузки: {str(e)}")
            # Можно показать ошибку в редакторе
            self.text_editor.setPlainText(f"Ошибка загрузки контента:\n{str(e)}")

    '''    # Обработка разных типов элементов
        if content_type == 'template':
            pass
        elif content_type == 'markdown':
            pass
    '''


    def on_selection_changed(self, metadata):
        if not metadata.get('has_selection', False):
            return

        item_type = metadata.get('type')
        file_path = metadata.get('path')
        # Получаем контент из кэша или другим способом
        content = self._get_content_for_file(file_path, item_type)
        if content:
            self.on_display_content(content_type=item_type, content=content, path_file=file_path)

    def _get_content_for_file(self, file_path, content_type):
        """Получает контент файла для отображения"""
        try:
            # Попробуйте получить из кэша
            if hasattr(self, 'content_cache'):
                cached_data = self.content_cache.get(file_path)
                if cached_data:
                    return cached_data.get('content', '')

            # Или прочитайте файл напрямую
            if file_path and os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()

        except Exception as e:
            print(f"Ошибка чтения файла {file_path}: {e}")

        return None

    def _on_template_changed(self, text):
        """Обработчик изменения имени шаблона"""
        # ✅ Реализовано: 03.09.2025
        self.template_name = text
        print(f"Имя шаблона изменено на: {self.template_name}")

    def _connect_tree_selection(self, index):
        """Подключает сигналы выделения для активного дерева"""
        if index < 0:
            return

        # Отключаем старые соединения
        try:
            for i in range(self.tab_widget.count()):
                tree = self.tab_widget.widget(i)
                if hasattr(tree, 'selectionModel'):
                    tree.selectionModel().selectionChanged.disconnect()
        except:
            pass

        # Подключаем к активному дереву
        tree_view = self.tab_widget.widget(index)
        if hasattr(tree_view, 'selectionModel'):
            tree_view.selectionModel().selectionChanged.connect(self.on_selection_changed)

    def _set_current_editor(self, editor: BaseFileEditor):
        """
        Заменяет текущий редактор в пользовательском интерфейсе.
        Args:
            editor: Новый экземпляр редактора (наследник BaseFileEditor)
        """
        # 1. Удаляем старый редактор (если был)
        if hasattr(self, 'current_editor') and self.current_editor:
            # Отключаем все сигналы от старого редактора
            try:
                self.current_editor.modification_changed.disconnect()
            except:
                pass

            # Удаляем виджет старого редактора из layout
            old_editor_widget = self.current_editor.get_editor_widget()
            self.editor_layout.removeWidget(old_editor_widget)
            old_editor_widget.deleteLater()

        # 2. Сохраняем ссылку на новый редактор
        self.current_editor = editor

        # 3. Добавляем виджет нового редактора в layout
        editor_widget = editor.get_editor_widget()
        self.editor_layout.addWidget(editor_widget)

        # 4. Подключаем сигналы нового редактора
        editor.modification_changed.connect(self._on_editor_modified)
        # Можно подключить другие сигналы: error_occurred, validation_finished

        # 5. Обновляем UI в соответствии с состоянием нового редактора
        self._update_window_title(editor.is_modified)
        if hasattr(editor, 'get_available_actions'):
            self._update_toolbar_actions(editor.get_available_actions())
        else:
            self._update_toolbar_actions([])  # Пустой список по умолчанию

    def _update_window_title(self, is_modified: bool):
        """
        Обновляет заголовок окна в зависимости от состояния редактора

        Args:
            is_modified: Флаг модификации документа
        """
        base_title = "Редактор файлов"
        if hasattr(self, 'current_editor') and self.current_editor and self.current_editor.file_path:
            file_name = self.current_editor.file_path.name
            title = f"{base_title} - {file_name}"
        else:
            title = base_title

        if is_modified:
            title += " *"

        self.setWindowTitle(title)

    def _on_editor_modified(self, is_modified: bool):
        """Обновляет UI при изменении состояния редактора"""
        # TODO 🚧 В разработке: 05.09.2025 - проверить атктуальность _on_editor_modified
        """
            Обработчик изменения состояния редактора (модифицирован/не модифицирован)

            Args:
                is_modified: Флаг модификации
            """
        self._update_window_title(is_modified)

        # Активируем/деактивируем кнопку Сохранить
        if hasattr(self, 'save_action'):
            self.save_action.setEnabled(is_modified)

        # Можно добавить другие UI обновления здесь
        print(f"DEBUG: Состояние редактора изменено - модифицирован: {is_modified}")

    def _update_toolbar_actions(self, actions: list):
        """Обновляет панель инструментов actions редактора"""
        # TODO 🚧 В разработке: 05.09.2025 - проверить атктуальность _update_toolbar_actions

        # Проверяем существование панели инструментов
        if not hasattr(self, 'editor_toolbar') or not self.editor_toolbar:
            print("DEBUG: Панель инструментов редактора не инициализирована")
            return

        # Проверяем существование действий
        if not hasattr(self, 'save_action'):
            print("DEBUG: Действия редактора не созданы")
            return

        # Очищаем текущую панель
        self.editor_toolbar.clear()

        # Добавляем общие действия (Сохранить, Отменить)
        self.editor_toolbar.addAction(self.save_action)
        self.editor_toolbar.addAction(self.undo_action)

        # Добавляем разделитель
        self.editor_toolbar.addSeparator()

        # Добавляем специфичные actions редактора
        for action in actions:
            self.editor_toolbar.addAction(action)

    def closeEvent(self, event):
        """Обработчик события закрытия окна"""
        # Отключаем сигналы контроллера
        try:
            self.controller.content_for_editor.disconnect()
            self.controller.selection_changed.disconnect()
            # Отключаем другие сигналы, если они были подключены
        except:
            pass  # Игнорируем ошибки если сигналы не были подключены

        # Отключаем сигналы
        if hasattr(self, 'tree_model_manager'):
            try:
                self.controller.current_source = "sidepanel"
                print("Закрываем окно")
            except:
                pass  # Игнорируем ошибки если сигнал не был подключен

        # Вызываем родительский обработчик
        super().closeEvent(event)

        # Важно: подтверждаем закрытие
        event.accept()

        # Дополнительные действия при закрытии
        print("FileEditorWindow закрывается")

