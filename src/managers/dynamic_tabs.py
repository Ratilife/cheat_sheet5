from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QTabWidget, QTreeWidget, QWidget, QVBoxLayout


class DynamicTabManager(QObject):
    # TODO 🚧 В разработке: 08.08.2025
        # 🏆task: Создание боковой панели;
        # 🏆task: Открыть боковую панель из стартовой панели;
    # Объявление сигнала
    tab_created = Signal(str, QTreeWidget)  # Сигнал передает имя вкладки и дерево
    def __init__(self, parent: QWidget = None):
        # TODO 🚧 В разработке: 08.08.2025
        super().__init__(parent)
        self.tab_widget = QTabWidget()
        self.trees = {}  # Словарь для хранения деревьев по именам вкладок


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
        self.tab_created.emit(name, tree)  # Уведомляем о создании

        return tree


    def _update_tree(self, tree: QTreeWidget, path: str):
        """Обновляет дерево при изменении файлов."""
        # TODO 🚧 В разработке: 08.08.2025
        # Логика обновления дерева...
        pass