import os
from pathlib import Path

from PySide6.QtGui import QAction

from editor.base_editor import BaseFileEditor
from editor.editor_factory import EditorFactory
from editor.st_editor import STEditor
from src.observers.my_base_observer import MyBaseObserver
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QMainWindow, QTreeView, QTabWidget, QVBoxLayout, QWidget, QSplitter,
                               QHBoxLayout, QLabel, QLineEdit, QSizePolicy, QInputDialog)
from operation.file_operations import FileOperations
from tests.managers.working_with_cache import get_cache


class FileEditorWindowObserver(MyBaseObserver):
    # ✅ Реализовано: 30.06.2025
    def __init__(self):
        super().__init__()



class FileEditorWindow(QMainWindow):
    """
        Главное окно редактора файлов с поддержкой форматов .st и .md.
        Обеспечивает создание, редактирование и сохранение файлов.
    """
    tab_changed = Signal(str, int)  # имя_вкладки, индекс

    def __init__(self, parent = None):
        super().__init__(parent)
        self.parent = parent
        self.tree_view = QTreeView()
        # Создаем экземпляр класса для сигналов
        self.observer = FileEditorWindowObserver()

        self.file_operations = FileOperations()

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

        # Перехватываем сигналы тут
        self._setup_connections()

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
        #self.text_editor = QTextEdit()
        #self.text_editor.setAcceptRichText(False)  # Режим plain text  Отключаем форматированный текст
        #editor_layout.addWidget(self.text_editor)

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

        # Создаем редактор по умолчанию при открытии окна
        default_editor = STEditor(self)
        self._set_current_editor(default_editor)



    def _setup_managers(self, tree_model_manager, toolbar_manager):
        """Устанавливает менеджеры и инициализирует интерфейс"""
        # TODO 🚧 В разработке: 02.09.2025
        if not tree_model_manager or not toolbar_manager:
            raise ValueError("tree_model_manager и toolbar_manager обязательны")
        self.tree_model_manager = tree_model_manager
        self.toolbar_manager = toolbar_manager

        self.toolbar_to_tree_layout = self.toolbar_manager.get_above_tree_toolbar_editor()

        # Подключаем обработчик запроса активного редактора
        self.tree_model_manager.request_active_editor.disconnect()
        self.tree_model_manager.request_active_editor.connect(self._provide_active_editor)

        # Устанавливаем текущий редактор как активный
        if hasattr(self, 'current_editor'):
            self.tree_model_manager.set_active_editor(self.current_editor)

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
        self.tree_model_manager.set_tab_widget(self.tab_widget)

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

    def _provide_active_editor(self):
        """Предоставляет активный редактор по запросу TreeModelManager"""
        if hasattr(self, 'current_editor') and self.current_editor:
            self.tree_model_manager.set_active_editor(self.current_editor)
        else:
            self.tree_model_manager.clear_active_editor()

    def _connect_selection_signals(self):
        """Подключает сигналы контроллера выделения"""
        self.controller = self.tree_model_manager.selection_controller
        self.controller.content_for_editor.connect(self.on_display_content) #тут получаем данные
        #controller.error_occurred.connect(self.on_show_selection_error)
        self.controller.selection_changed.connect(self.on_selection_changed) # тут обработка выбранного элемента

        # Устанавливаем источник для контроллера
        self.controller.current_source = "editor"
        print("Сигналы контроллера выделения подключены")

        self.tab_changed.connect(self.handle_tab_change)

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

    def _setup_markdown_layout(self, editor, content):
        """Настраивает layout для markdown-редактора с HTML-представлением"""
        # 1. Удаляем старый редактор если есть
        if hasattr(self, 'current_editor') and self.current_editor:
            try:
                self.current_editor.modification_changed.disconnect()
            except:
                pass

            old_editor_widget = self.current_editor.get_editor_widget()
            self.editor_layout.removeWidget(old_editor_widget)
            old_editor_widget.deleteLater()

        # 2. Сохраняем ссылку на редактор
        self.current_editor = editor

        # 3. Создаем вертикальный разделитель
        editor_splitter = QSplitter(Qt.Vertical)

        # 4. Верхняя часть - текстовый редактор
        self.text_editor.setPlainText(content)  # Устанавливаем контент

        # 5. Нижняя часть - HTML-представление из редактора
        html_viewer = editor.get_editor_widget()  # Получаем HTML-виджет

        # 6. Добавляем в разделитель
        editor_splitter.addWidget(self.text_editor)
        editor_splitter.addWidget(html_viewer)

        # 7. Настраиваем пропорции (текстовый редактор - 60%, HTML - 40%)
        editor_splitter.setSizes([600, 400])
        editor_splitter.setChildrenCollapsible(False)

        # 8. Добавляем разделитель в layout редактора
        # Сначала очищаем editor_layout
        for i in reversed(range(self.editor_layout.count())):
            widget = self.editor_layout.itemAt(i).widget()
            if widget:
                self.editor_layout.removeWidget(widget)
                if widget != self.text_editor:  # Не удаляем text_editor
                    widget.deleteLater()

        # Добавляем разделитель
        self.editor_layout.addWidget(editor_splitter)

        # 9. Подключаем сигналы
        editor.modification_changed.connect(self._on_editor_modified)

        # 10. Настраиваем политики размеров для правильного растягивания
        self.text_editor.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        html_viewer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def _clear_editor(self):
        """Очищает текущий редактор и сбрасывает состояние"""
        # TODO 🚧 В разработке: 22.10.2025
        if hasattr(self, 'current_editor') and self.current_editor:
            try:
                # Очищаем содержимое редактора
                self.current_editor.set_content("")
                # Сбрасываем путь к файлу
                self.current_editor.file_path = None
                # Сбрасываем флаг модификации
                self.current_editor.is_modified = False

                # Обновляем UI
                self._update_window_title(False)
                if hasattr(self, 'save_action'):
                    self.save_action.setEnabled(False)

                print("DEBUG: Редактор очищен")

            except Exception as e:
                print(f"Ошибка при очистке редактора: {e}")

        # Также можно показать сообщение о том, что выбрана папка
        self.statusBar().showMessage("Выбрана папка - редактор очищен")
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
        self.tab_name = self.tab_widget.tabText(index)
        print(f"DEBUG: Переключена вкладка: {self.tab_name}")

        # 1. Синхронизация с TreeModelManager
        #active_info = self.tree_model_manager.get_active_tab_info()


        # 2. Обновление UI
        self.setWindowTitle(f"Редактор файлов - {self.tab_name}")

        # 3. Получаем модель для текущей вкладки
        current_model = self.all_models.get(self.tab_name)

        # Получаем модель для текущей вкладки
        #self.current_model = self.all_models.get(tab_name)

        # 4. Обновление статусбара
        # TODO 05.09.2025 технически правильно, но логически неверно
        file_count = current_model.rowCount() if current_model else 0
        self.statusBar().showMessage(
            f"Вкладка: {self.tab_name} | Файлов: {file_count} | Готово"
        )

        # 5. Логирование для отладки
        print(f"DEBUG: Активна вкладка '{self.tab_name}', модель: {current_model is not None}")

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
                self.statusBar().showMessage("Файл сохранен", 3000)
            else:
                print("DEBUG: Ошибка при сохранении файла")
                self.statusBar().showMessage("Ошибка сохранения файла", 5000)

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

    def on_display_content(self, content_type, content, path_file, metadata=None):
        """Отображает переданный контент в соответствующем редакторе.

            Проверяет видимость окна, создает редактор нужного типа с помощью
            фабрики, устанавливает в него переданный контент и путь к файлу,
            заменяет текущий редактор в интерфейсе и обновляет сообщение
            в строке состояния. В случае ошибки выводит сообщение об ошибке.

            Args:
                content_type: Тип контента (например, 'markdown', 'st').
                content: Строка с содержимым, которое нужно отобразить.
                path_file: Путь к файлу, ассоциированному с контентом.
            """
        # TODO 🚧 В разработке: 30.08.2025

        # Проверяем, активно ли это окно
        if not self.isVisible():
            return

        # ✅ ЗАПРЕТ на отображение папок в редакторе
        if content_type == 'folder':
            print(f"DEBUG: Папки не отображаются в редакторе - {path_file}")
            self.statusBar().showMessage("Папки не отображаются в редакторе")
            self._clear_editor()
            return  # Прерываем выполнение

        try:
            print("👍 Работает метод on_display_content()")
            # 1. Создаем подходящий редактор через фабрику
            editor = EditorFactory.create_editor_for_type(content_type, self)

            if editor is None:
                raise ValueError(f"Не удалось создать редактор для типа: {content_type}")

            # 2. Устанавливаем контент в редактор и путь к файлу
            print(f'content_type = {content_type}')
            #print(f'Устанавливаем контент в редактор и путь к файлу \n 🔥🔥🔥🔥\n {content} \n 🔥🔥🔥🔥')

            print(f'🔧🔧🔧metadata: {metadata} 🔧🔧🔧')

            #print(f'content: {content}')

            editor.set_content(content)
            editor.file_path = Path(path_file)

            # Сохраняем полный контекст - ОБНОВЛЯЕМ, а не перезаписываем
            if not hasattr(editor, 'template_context') or editor.template_context is None:
                editor.template_context = {}

            # Обновляем только нужные поля, сохраняя остальные
            editor.template_context.update({
                'file_path': metadata.get('file_path') if metadata else None,
                'template_id': metadata.get('template_id') if metadata else None,
                'original_structure': metadata.get('original_structure') if metadata else None,
                'element_path': metadata.get('element_path') if metadata else [],
                'original_content': content  # ⬅️ тоже важно добавить!
            })


            #if content_type == 'markdown':
                #self._setup_markdown_layout(editor, content)

            #else:
                # 3. Заменяем текущий редактор в UI
                #self.text_editor.setPlainText(content)
            self._set_current_editor(editor)


            # 4. Обновляем статус
            self.statusBar().showMessage(f"Загружен контент типа: {content_type}")
        except Exception as e:
            print(f"Ошибка при отображении контента: {e}")
            self.statusBar().showMessage(f"Ошибка загрузки: {str(e)}")
            # Можно показать ошибку в редакторе
            #self.text_editor.setPlainText(f"Ошибка загрузки контента:\n{str(e)}")

    '''    # Обработка разных типов элементов
        if content_type == 'template':
            pass
        elif content_type == 'markdown':
            pass
    '''


    def on_selection_changed(self, metadata):
        """Обрабатывает изменение выделения в модели дерева.

            Проверяет, есть ли выделение, определяет тип и путь к файлу,
            получает содержимое файла и передает его в метод отображения
            содержимого в редакторе.

            Args:
                metadata: Словарь с метаданными выбранного элемента.
                          Должен содержать ключи 'has_selection' (bool),
                          'type' (str), и 'path' (str).
        """
        if not metadata.get('has_selection', False):
            return

        item_type = metadata.get('type')
        file_path = metadata.get('path')
        # Получаем контент из кэша или другим способом
        content = self._get_content_for_file(file_path, item_type)

        if content:
            print('🙋🏻‍♂️ метод on_display_content() запустили через метод on_selection_changed()')
            template_context = self.controller.get_template_context(self.tab_widget)
            print(f'👻👻 Я печатаю на стороне метода on_selection_changed содержание переменной template_context : {template_context} 👻👻')
            self.on_display_content(content_type=item_type, content=content, path_file=file_path, metadata=template_context)

    def _get_content_for_file(self, file_path, content_type):
        """Получает контент файла для отображения"""
        try:
            print('😈😈😈😈😈😈😈 зашли в метод _get_content_for_file()😈😈😈😈😈😈😈😈')
            # Попробуйте получить из кэша
            if hasattr(self, 'content_cache'):
                cached_data = self.content_cache.get(file_path)
                if cached_data:
                    print(f'💡 Получает контент файла для отображения cached_data: {cached_data}')
                    print('🎃🎃🎃🎃🎃Вышли из метода _get_content_for_file🎃🎃🎃🎃🎃')
                    return cached_data.get('content', '')

            # Или прочитайте файл напрямую
            if file_path and os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    print('🐗🐗🐗🐗Вышли из метода _get_content_for_file🐗🐗🐗🐗')
                    return f.read()

        except Exception as e:
            print(f"Ошибка чтения файла {file_path}: {e}")
        print('😄😄😄😄Вышли из метода _get_content_for_file😄😄😄😄')
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

    def _set_current_editor_old(self, editor: BaseFileEditor):
        """Правильная замена редактора"""
        # 1. Удаляем старый редактор
        if hasattr(self, 'current_editor') and self.current_editor:
            try:
                self.current_editor.modification_changed.disconnect()
            except:
                pass

            old_editor_widget = self.current_editor.get_editor_widget()
            self.editor_layout.removeWidget(old_editor_widget)
            old_editor_widget.deleteLater()

        # 2. Удаляем старый text_editor если он существует
        if hasattr(self, 'text_editor'):
            self.editor_layout.removeWidget(self.text_editor)
            self.text_editor.deleteLater()
            del self.text_editor

        # 3. Сохраняем новый редактор
        self.current_editor = editor

        # 4. Добавляем ТОЛЬКО новый редактор
        editor_widget = editor.get_editor_widget()
        editor_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.editor_layout.addWidget(editor_widget)

        # 5. Подключаем сигналы
        editor.modification_changed.connect(self._on_editor_modified)

        # 6. Обновляем UI
        self._update_window_title(editor.is_modified)

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
                self.current_editor.undo_available.disconnect()
                self.current_editor.redo_available.disconnect()
            except:
                pass

            # Удаляем виджет старого редактора из layout
            old_editor_widget = self.current_editor.get_editor_widget()
            self.editor_layout.removeWidget(old_editor_widget)
            old_editor_widget.deleteLater()



        # 2. Сохраняем ссылку на новый редактор
        self.current_editor = editor

        # 3. Обновляем активный редактор в менеджере
        if self.tree_model_manager:
            self.tree_model_manager.set_active_editor(editor)

        # 4. Добавляем виджет нового редактора в layout
        editor_widget = editor.get_editor_widget()
        self.editor_layout.addWidget(editor_widget)

        # 5. Подключаем сигналы нового редактора
        editor.modification_changed.connect(self._on_editor_modified)
        editor.undo_available.connect(self._on_undo_available)
        editor.redo_available.connect(self._on_redo_available)
        # Можно подключить другие сигналы: error_occurred, validation_finished

        # 6. Обновляем состояние кнопок
        self._on_editor_modified(editor.is_modified)
        self._on_undo_available(editor.can_undo())
        self._on_redo_available(editor.can_redo())

        # 7. Обновляем UI в соответствии с состоянием нового редактора
        self._update_window_title(editor.is_modified)
        if hasattr(editor, 'get_available_actions'):
            self._update_toolbar_actions(editor.get_available_actions()) # TODO - ошибка тут: Ошибка возникает в методе _update_toolbar_actions при попытке очистить панель инструментов, которая уже была удалена. Проблема в том, что при смене редакторов вы пытаетесь обновить панель инструментов, но к этому моменту виджеты могут быть уже уничтожены.
        else:
            self._update_toolbar_actions([])  # Пустой список по умолчанию

    def _set_current_editor_old3(self, editor: BaseFileEditor):
        """Заменяет текущий редактор в пользовательском интерфейсе"""

        # 1. Удаляем старый редактор
        if hasattr(self, 'current_editor') and self.current_editor:
            try:
                # Отключаем сигналы
                self.current_editor.modification_changed.disconnect()
                self.current_editor.undo_available.disconnect()
                self.current_editor.redo_available.disconnect()
            except:
                pass

            # Удаляем виджет
            old_editor_widget = self.current_editor.get_editor_widget()
            if old_editor_widget:
                self.editor_layout.removeWidget(old_editor_widget)
                old_editor_widget.setParent(None)
                old_editor_widget.deleteLater()

        # 2. Сохраняем новый редактор
        self.current_editor = editor

        # 3. Добавляем новый редактор в layout
        editor_widget = editor.get_editor_widget()
        if editor_widget:
            editor_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.editor_layout.addWidget(editor_widget)

            # 4. Показываем виджет
            editor_widget.show()

        # 5. Подключаем сигналы
        editor.modification_changed.connect(self._on_editor_modified)
        if hasattr(editor, 'undo_available'):
            editor.undo_available.connect(self._on_undo_available)
        if hasattr(editor, 'redo_available'):
            editor.redo_available.connect(self._on_redo_available)

        # 6. Обновляем UI
        self._update_window_title(editor.is_modified)
        self._on_editor_modified(editor.is_modified)

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

    def _on_undo_available(self, available: bool):
        """Обновляет состояние кнопки Отменить"""
        if hasattr(self, 'undo_action'):
            self.undo_action.setEnabled(available)
        print(f"DEBUG: Отменить доступно: {available}")

    def _on_redo_available(self, available: bool):
        """Обновляет состояние кнопки Повторить"""
        if hasattr(self, 'redo_action'):
            self.redo_action.setEnabled(available)
        print(f"DEBUG: Повторить доступно: {available}")

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

    def _update_toolbar_actions_old(self, actions: list):
        """Обновляет панель инструментов actions редактора"""
        # TODO 🚧 В разработке: 05.09.2025 - проверить атктуальность _update_toolbar_actions

        # Проверяем существование панели инструментов
        if not hasattr(self, 'editor_toolbar') or  self.editor_toolbar is None:
            print("DEBUG: Панель инструментов редактора не инициализирована")
            return

            # ✅ Дополнительная проверка "на живца"
            try:
                # Пробуем вызвать простой метод - если вылетает ошибка, объект мертв
                _ = self.editor_toolbar.isVisible()
            except RuntimeError:
                self.editor_toolbar = None  # Помечаем как мертвый
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

    def _update_toolbar_actions(self, actions: list):
        """Обновляет панель инструментов actions редактора"""

        # Проверяем существование панели инструментов
        if not hasattr(self, 'editor_toolbar') or self.editor_toolbar is None:
            print("DEBUG: Панель инструментов редактора не инициализирована")
            return

        # Проверяем, не удален ли объект Qt
        try:
            # Простая проверка доступности объекта
            if not self.editor_toolbar.objectName():
                pass
        except RuntimeError as e:
            if "already deleted" in str(e):
                print("DEBUG: Панель инструментов уже удалена")
                self.editor_toolbar = None
                return
            else:
                print(f"DEBUG: Ошибка доступа к панели инструментов: {e}")
                return

        # Проверяем существование действий
        if not hasattr(self, 'save_action'):
            print("DEBUG: Действия редактора не созданы")
            return

        # Очищаем текущую панель
        try:
            self.editor_toolbar.clear()
        except RuntimeError as e:
            print(f"DEBUG: Ошибка при очистке панели инструментов: {e}")
            self.editor_toolbar = None
            return

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

    #----Создание файлов----

    def _setup_connections(self)->None:
        # Обработчики создания файлов в КОНТЕКСТЕ РЕДАКТОРА
        self.toolbar_manager.new_st_file.connect(self._handle_new_st_file)
        self.toolbar_manager.new_md_file.connect(self._handle_new_md_file)
        self.toolbar_manager.new_folder.connect(self._handle_new_folder)
        self.toolbar_manager.new_template.connect(self._handle_new_template)
        self.toolbar_manager.delete_element.connect(self._on_delete_element)


        # Подключаем сигналы сохранения из toolbar
        self.toolbar_manager.save_file.connect(self._on_save_action)


    def handle_tab_change(self, tab_name, index):
        print(f"Вкладка изменилась: {tab_name}, индекс: {index}")
        self.tab_name = tab_name

    def _set_active_tab(self):
        """Получает имя активной вкладки.

                Метод сначала проверяет, есть ли у текущего экземпляра локально сохранённое
                имя вкладки (в атрибуте self.tab_name), и если оно есть, строковое и не пустое,
                возвращает его. В противном случае, он запрашивает актуальное имя активной
                вкладки у родительского объекта через его tab_manager и возвращает его.

         Returns:
                 str: Имя активной вкладки.
        """
        # Получение словаря с информацией об активной вкладке от родительского менеджера вкладок
        active_info = self.parent.tab_manager.get_active_tab_info()
        # Проверка: существует ли атрибут tab_name у текущего объекта, является ли он строкой и не пустой ли он
        if hasattr(self, 'tab_name') and isinstance(self.tab_name, str) and self.tab_name:
            # Возврат локально сохранённого имени вкладки, если все условия выше выполнены
            return self.tab_name
        # Возврат имени активной вкладки из словаря информации, полученного от менеджера вкладок
        return active_info['tab_name']

    def _handle_new_st_file(self)->str:
        """Создает новый ST-файл, добавляет его в модель дерева и открывает в редакторе.

          Открывает диалог для ввода имени нового файла. При подтверждении создает
          файл в активной вкладке, добавляет его в дерево файлов и автоматически
          открывает в редакторе.

          Returns:
              str: Путь к созданному файлу, если операция успешна, иначе None.
          """
        # TODO 🚧 В разработке: 08.10.2025
        name, ok = QInputDialog.getText(self, "Имя файла", "Введите имя файла:")
        if not ok:
            return None
        active_tab_name = self._set_active_tab()
        file_path = self.file_operations.create_new_st_file(name, active_tab_name)
        self.tree_model_manager.add_files_to_tab(active_tab_name, [file_path])
        self.file_operations.add_new_st_file_cache(file_path)
        # Автоматически открываем новый файл в редакторе
        self.open_file_in_editor(file_path)

    def _handle_new_md_file(self)->None:
        # TODO 🚧 В разработке: 08.10.2025
        name, ok = QInputDialog.getText(self, "Имя файла", "Введите имя файла:")
        if not ok:
            return None
        active_tab_name = self._set_active_tab()
        file_path = self.file_operations.create_new_md_file(name, active_tab_name)
        self.tree_model_manager.add_files_to_tab(active_tab_name, [file_path])
        # Автоматически открываем новый файл в редакторе
        self.open_file_in_editor(file_path)

    def _handle_new_folder(self):
        # TODO 🚧 В разработке: 13.10.2025

        #  Запросить имя папки
        name_folder, ok = QInputDialog.getText(self, "Имя папки", "Введите имя папки:")
        if not ok or not name_folder.strip():
            return
        self.tree_model_manager.new_folder(name_folder)

    def _handle_new_template(self):
        # TODO 🚧 В разработке: 14.10.2025
        print('Зашли в метод _handle_new_template() класс FileEditorWindow')
        name_template, ok = QInputDialog.getText(self, "Имя шаблона", "Введите имя шаблона:")
        if not ok or not name_template.strip():
            return
        self.tree_model_manager.new_template(name_template)
        print('вышли из метода _handle_new_template() класс FileEditorWindow')

    def _on_delete_element(self):
        # Получаем информацию о выделении перед удалением
        selection_info = self.tree_model_manager.get_selection_info()
        if not selection_info:
            return

        file_path = selection_info['path']
        current_tab_name = self.tab_widget.tabText(self.tab_widget.currentIndex())

        # Выполняем удаление
        success = self.tree_model_manager.delete_element()

        # Обновляем модель после удаления
        if success:
            # 🔽 ПРОСТОЙ СПОСОБ: Используем встроенные методы обновления
            self._refresh_current_tab_model(current_tab_name)

    def _refresh_current_tab_model(self, tab_name: str):
        """Обновляет модель текущей вкладки"""
        try:
            # Просим TreeModelManager обновить модель для этой вкладки
            if hasattr(self.tree_model_manager, 'refresh_tab_model'):
                self.tree_model_manager.refresh_tab_model(tab_name)
            else:
                # Альтернативный способ: переключаем вкладку, чтобы вызвать обновление
                current_index = self.tab_widget.currentIndex()
                self.tab_widget.setCurrentIndex(-1)  # Сбрасываем
                self.tab_widget.setCurrentIndex(current_index)  # Возвращаем

            print(f"DEBUG: Модель обновлена для вкладки {tab_name}")

        except Exception as e:
            print(f"Ошибка при обновлении модели: {e}")
    def open_file_in_editor(self, file_path:str)-> None:
        """Открывает указанный файл в соответствующем редакторе.

            Определяет тип редактора на основе расширения файла, создает
            экземпляр редактора с помощью фабрики, загружает в него файл,
            заменяет текущий редактор в интерфейсе и обновляет сообщение
            в строке состояния.

            Args:
                file_path: Путь к файлу, который нужно открыть.
        """
        # TODO 🚧 В разработке: 08.10.2025

        try:

            # 1. Определяем тип редактора по расширению
            extension = Path(file_path).suffix  # '.st' или '.md'

            # 2. Создаем редактор через фабрику
            editor = EditorFactory.create_editor(extension, parent=self)

            # 3. Загружаем файл в редактор
            success = editor.load(Path(file_path))
            if not success:
                print(f"Ошибка загрузки файла: {file_path}")

            # 4. Заменяем текущий редактор в UI
            self._set_current_editor(editor)

            # 5. Обновляем статус
            self.statusBar().showMessage(f"Загружен: {Path(file_path).name}")
        except Exception as e:
            print(f"Ошибка открытия файла {file_path}: {e}")
            self.statusBar().showMessage(f"Ошибка: {str(e)}")