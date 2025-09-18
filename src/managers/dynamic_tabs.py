from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QTreeView

from operation.file_operations import FileOperations


class DynamicTabManager(QObject):
    # TODO 🚧 В разработке: 08.08.2025
        # 🏆task: Создание боковой панели;
        # 🏆task: Открыть боковую панель из стартовой панели;
    # Объявление сигнала
    tab_created = Signal(str, QTreeView)  # Сигнал передает имя вкладки и дерево
    def __init__(self, parent: QWidget = None):
        # TODO 🚧 В разработке: 08.08.2025
        super().__init__(parent)
        self.tab_widget = QTabWidget()
        self.trees = {}  # Словарь для хранения деревьев по именам вкладок

        # 🔽Добавляем методы 17.09.2025🔽
        self.tab_widgets = {}  # {"side_panel": tab_widget1, "editor": tab_widget2}
        self.widget_priorities = []
        # 🔽Конец добавления методов 17.09.2025🔽
        self.file_operations = FileOperations()
    def create_tabs(self, tab_data: dict) -> QTabWidget:
        """Создает вкладки и деревья на основе переданного словаря.
        Ключи словаря используются как имена вкладок.

        Args:
            tab_data: Словарь, где ключи - имена вкладок, а значения - связанные данные

        Returns:
            QTabWidget: Виджет с созданными вкладками

        Raises:
            ValueError: Если словарь пуст
        """
        if not tab_data:
            raise ValueError("Словарь с данными вкладок не может быть пустым!")

        for tab_name in tab_data.keys():
            self._add_tab(tab_name)
        return self.tab_widget

    def _add_tab(self, name: str) -> QTreeView:
        """Добавляет одну вкладку с деревом."""
        # TODO 🚧 В разработке: 08.08.2025
        tree = QTreeView()
        tree.setHeaderHidden(True)  # Пример настройки

        tab_content = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(tree)
        tab_content.setLayout(layout)

        self.tab_widget.addTab(tab_content, name)
        self.trees[name] = tree
        self.tab_created.emit(name, tree)  # Уведомляем о создании

        return tree


    def _update_tree(self, tree: QTreeView, path: str):
        """Обновляет дерево при изменении файлов."""
        # TODO 🚧 В разработке: 08.08.2025
        # Логика обновления дерева...
        pass

    # 🔽Добавляем методы 17.09.2025🔽
    def register_tab_widget(self, widget_name: str, tab_widget: QTabWidget, priority: int = 0):
        """Регистрирует tab_widget с приоритетом"""
        self.tab_widgets[widget_name] = tab_widget
        self.widget_priorities = sorted(
            self.tab_widgets.keys(),
            key=lambda x: priority,
            reverse=True
        )

    def get_active_tab_info(self) -> dict | None:
        """Возвращает информацию об активной вкладке из любого окна"""
        for widget_name in self.widget_priorities:
            tab_widget = self.tab_widgets[widget_name]
            if tab_widget and tab_widget.count() > 0:
                current_index = tab_widget.currentIndex()
                if current_index >= 0:
                    return {
                        'widget_name': widget_name,
                        'tab_name': tab_widget.tabText(current_index),
                        'tab_widget': tab_widget
                    }
        return None

    def launch_download_for_active_tab(self):
        """Загружает файлы для активной вкладки"""
        tab_info = self.get_active_tab_info()
        if not tab_info:
            print("Нет активных вкладок")
            return None

        files = self.file_operations.load_st_md_files(tab_info['tab_name'])
        return tab_info['tab_name'], files

    # 🔽Конец добавления методов 17.09.2025🔽