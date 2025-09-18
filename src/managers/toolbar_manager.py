from src.managers.ui_manager import UIManager
from src.managers.dynamic_tabs import DynamicTabManager
from PySide6.QtCore import Signal, QObject
from PySide6.QtGui import QIcon
class ToolbarManager(QObject):
    """Управление панелями инструментов с использованием UIManager.
           Класс ToolbarManager отвечает за создание и управление панелями инструментов редактора.
           Он инкапсулирует логику генерации кнопок, панелей, а также связывания пользовательских действий с обработчиками.
           Использует UIManager для шаблонного создания компонентов интерфейса, поддерживает динамическое подключение к TreeManager и модели дерева.
           Реализует набор сигналов для интеграции с внешней логикой (например, сохранение, создание, удаление файлов, форматирование и др.).
           Позволяет централизованно настраивать и изменять поведение панели инструментов редактора.

    """
    # Сигналы для внешних обработчиков
    load_requested = Signal()  # Загрузка файлов
    editor_toggled = Signal(bool)  # Открытие/закрытие редактора
    format_action = Signal(str)  # Форматирование текста (например, "bold")

    collapse_all = Signal()
    expand_all = Signal()
    new_st_file = Signal()
    new_md_file = Signal()
    new_folder = Signal()
    new_template = Signal()
    save_file = Signal()
    save_file_as = Signal()
    delete_action = Signal()
    cut_action = Signal()
    copy_action = Signal()
    paste_action = Signal()

    def __init__(self,tree_manager=None, close=None, showMinimized=None  ):
        super().__init__()
        self.ui = UIManager()  # Создаем экземпляр UIManager
        self.tree_manager = tree_manager
        self.close = close
        self.showMinimized = showMinimized
        self._setup_buttons()
        self._setup_toolbars()
        #self._connect_tree_manager()

    def _connect_tree_manager(self):
        """Подключает методы TreeManager к кнопкам."""
        # ✅ Реализовано: 10.08.2025
        if self.tree_manager:
            # Подключаем кнопки к методам TreeManager
            self.ui.buttons["collapse_btn"].clicked.connect(self.tree_manager.collapse_all)
            self.ui.buttons["expand_btn"].clicked.connect(self.tree_manager.expand_all)
            self.ui.buttons["collapse_panel_btn"].clicked.connect(self.showMinimized)

    def _setup_buttons(self):
        """Создает кнопки и привязывает сигналы."""
        # TODO 🚧 В разработке: 10.08.2025
        # Кнопка свернуть все
        self.ui.create_button(
            name="collapse_btn",
            text="+",
            tooltip="Свернуть все"
        )
        # self.ui.buttons["collapse_btn"].clicked.connect(self.collapse_all.emit)

        # Кнопка развернуть все
        self.ui.create_button(
            name="expand_btn",
            text="-",
            tooltip="Развернуть все",
            fixed_width=20,
            fixed_height=20

        )
        # self.ui.buttons["expand_btn"].clicked.connect(self.expand_all.emit())

        # Кнопка свернуть панель
        self.ui.create_button(
            name="collapse_panel_btn",
            text="—",
            tooltip="Свернуть панель",
            fixed_width=20,
            fixed_height=20
        )
        self.ui.buttons["collapse_panel_btn"].clicked.connect(self.showMinimized)

        # Кнопка закрыть панель
        self.ui.create_button(
            name="close_panel_btn",
            text="Х",
            tooltip="Закрыть панель",
            fixed_width=20,
            fixed_height=20
        )
        self.ui.buttons["close_panel_btn"].clicked.connect(self.close)

        # Кнопка открыть окно редактора
        self.ui.create_button(
            name="edit_btn",
            text="✏️",
            tooltip="Открыть редактор",
            fixed_width=20,
            fixed_height=20
        )
        self.ui.buttons["edit_btn"].clicked.connect(
            lambda: self.editor_toggled.emit(True)  # TODO - нет подключения к этому сигналу
        )
        # Кнопка загрузить файл
        self.ui.create_button(
            name="load_btn",
            text="📥",
            tooltip="Загрузить файл",
            fixed_width=20,
            fixed_height=20
        )
        self.tab_manager = DynamicTabManager()
        self.ui.buttons["load_btn"].clicked.connect(self.tab_manager.launch_download_for_active_tab)   #TODO 17/09/2025 изменить переписуем TreeModelManager

        # Кнопка Создать st-файл
        self.ui.create_button(
            name="new_st_btn",
            text="📄",
            tooltip="Создать ST-файл"
        )
        self.ui.buttons["new_st_btn"].clicked.connect(lambda: self.new_st_file.emit())

        # Кнопка Создать md-файл
        self.ui.create_button(
            name="new_md_btn",
            text="📝",
            tooltip="Создать MD-файл"
        )
        self.ui.buttons["new_md_btn"].clicked.connect(lambda: self.new_md_file.emit())

        # Кнопка Создать папку
        self.ui.create_button(
            name="new_folder_btn",
            text="📂",
            tooltip="Создать папку"
        )
        self.ui.buttons["new_folder_btn"].clicked.connect(lambda: self.new_folder.emit())

        # Кнопка Создать шаблон
        self.ui.create_button(
            name="new_template_btn",
            text="🖼️",
            tooltip="Создать шаблон"
        )
        self.ui.buttons["new_template_btn"].clicked.connect(lambda: self.new_template.emit())

        # Кнопка Сохранить
        self.ui.create_button(
            name="save_btn",
            text="💾",
            tooltip="Сохранить"
        )
        self.ui.buttons["save_btn"].clicked.connect(lambda: self.save_file.emit())

        # Кнопка Сохранить как
        self.ui.create_button(
            name="new_save_as_btn",
            text="💽",
            tooltip="Сохранить как"
        )
        self.ui.buttons["new_save_as_btn"].clicked.connect(lambda: self.save_file_as.emit())

        # Кнопка Удалть редактор
        self.ui.create_button(
            name="delete_btn",
            icon=QIcon.fromTheme("edit-delete"),
            text="",
            tooltip="Удалть"
        )
        self.ui.buttons["delete_btn"].clicked.connect(lambda: self.delete_action)

        # Кнопка Вырезать редактор
        self.ui.create_button(
            name="cut_btn",
            icon=QIcon.fromTheme("edit-cut"),
            text="",
            tooltip="вырезать"
        )
        self.ui.buttons["cut_btn"].clicked.connect(lambda: self.cut_action.emit())

        # Кнопка Копировать редактор
        self.ui.create_button(
            name="copy_btn",
            icon=QIcon.fromTheme("edit-copy"),
            text="",
            tooltip="Копировать"
        )
        self.ui.buttons["copy_btn"].clicked.connect(lambda: self.copy_action.emit())

        # Кнопка Вставить редактор
        self.ui.create_button(
            name="paste_btn",
            icon=QIcon.fromTheme("edit-paste"),
            text="",
            tooltip="Вставить"
        )
        self.ui.buttons["paste_btn"].clicked.connect(lambda: self.paste_action.emit())

    def _setup_toolbars(self):
        """Создает панели инструментов."""
        # ✅ Реализовано: 10.08.2025
        # панель над деревом файлов в модуле side_panel.py
        self._title_layout = self.ui.create_toolbar(
            name="title_layout",
            buttons=["collapse_btn", "expand_btn", "load_btn", "edit_btn",
                     "spacer",
                     "collapse_panel_btn", "close_panel_btn"]
        )
        # панель над деревом файлов в модуле file_editor.py
        self._above_tree_toolbar_editor = self.ui.create_toolbar(
            name="above_tree_toolbar_editor",
            buttons=["new_st_btn", "new_md_btn", "new_folder_btn", "new_template_btn", "new_save_as_btn"],
        )

        # панель над текстовым редактором в модуле file_editor.py
        self._editor_toolbar = self.ui.create_toolbar(
            name="editor_toolbar",
            buttons=["cut_btn", "copy_btn", "delete_btn", "paste_btn", "save_btn"]
        )



    def get_title_layout(self):
        # ✅ Реализовано: 10.08.2025
        return self._title_layout

    def get_above_tree_toolbar_editor(self):
        # ✅ Реализовано: 10.08.2025
        return self._above_tree_toolbar_editor

    def get_editor_toolbar(self):
        # ✅ Реализовано: 10.08.2025
        return self._editor_toolbar