from PySide6.QtCore import QObject
from PySide6.QtWidgets import QTabWidget, QTreeWidget, QWidget, QVBoxLayout
from PySide6.QtGui import QIcon

class DynamicTabManager(QObject):
    # TODO 🚧 В разработке: 08.08.2025
        # 🏆task: Создание боковой панели;
        # 🏆task: Открыть боковую панель из стартовой панели;

    def __init__(self, parent: QWidget = None):
        # TODO 🚧 В разработке: 08.08.2025
        super().__init__(parent)
        self.tab_widget = QTabWidget()
        self.trees = {}  # Словарь для хранения деревьев по именам вкладок
    def create_tabs(self, tab_names: list[str]) -> QTabWidget:
        """Создает вкладки и деревья на основе списка имен."""
        # TODO 🚧 В разработке: 08.08.2025

        if not tab_names:
            raise ValueError("Список имен вкладок не может быть пустым!")

        for name in tab_names:
            self._add_tab(name)
        return self.tab_widget

    def _add_tab(self, name: str) -> QTreeWidget:
        """Добавляет одну вкладку с деревом."""
        # TODO 🚧 В разработке: 08.08.2025
        tree = QTreeWidget()
        tree.setHeaderHidden(True)  # Пример настройки

        tab_content = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(tree)
        tab_content.setLayout(layout)

        self.tab_widget.addTab(tab_content, name)
        self.trees[name] = tree
        #TODO 08.08.2025 self.tab_created Что за переменная и для чего
        self.tab_created.emit(name, tree)  # Уведомляем о создании

        return tree


    def _update_tree(self, tree: QTreeWidget, path: str):
        """Обновляет дерево при изменении файлов."""
        # TODO 🚧 В разработке: 08.08.2025
        # Логика обновления дерева...
        pass