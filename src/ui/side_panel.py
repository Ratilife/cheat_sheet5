from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QTreeWidget, QTreeWidgetItem, QApplication
from src.managers.dynamic_tabs import DynamicTabManager
from src.observers.file_watcher import FileWatcher
from src.observers.my_base_observer import MyBaseObserver
from src.widgets.markdown_viewer_widget import MarkdownViewer
from PySide6.QtCore import Qt
from src.managers.ui_manager import UIManager
from src.managers.toolbar_manager import ToolbarManager


class SidePanelObserver(MyBaseObserver):
    # ✅ Реализовано: 29.06.2025
    def __init__(self):
        super().__init__()
class SidePanel(QWidget):
    # TODO 🚧 В разработке: 08.08.2025
        # 🏆task: Создание боковой панели;
        # 🏆task: Открыть боковую панель из стартовой панели;
    def __init__(self, tab_names: list[str], parent=None):
        """
            Инициализация боковой панели с динамическими вкладками

            Args:
                tab_names: Список имен для вкладок (например, ["Documents", "Projects"])
                parent: Родительский виджет
        """
        # TODO 🚧 В разработке: 08.08.2025
        super().__init__(parent, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        # 1. Создаем экземпляр класса для сигналов
        self.observer = SidePanelObserver()

        self.tab_manager = DynamicTabManager()
        # 3. # Инициализация наблюдателя
        self.file_watcher = FileWatcher()
        self.file_watcher.file_updated.connect(self._on_file_updated)
        self.file_watcher.file_deleted.connect(self._on_file_deleted)

        # нижняя панель (отображение данных)
        self.content_viewer = MarkdownViewer()

        self.tab_names = tab_names
        self._init_ui()


        #self.connect_signals()

    def _init_ui(self):
        """Инициализация пользовательского интерфейса"""
        # TODO 🚧 В разработке: 08.08.2025
        # Устанавливаем минимальную ширину панели
        self.setMinimumWidth(300)

        self.ui = UIManager()
        self.tree_manager = None # TreeManager(self.tree_view)
        self.toolbar_manager = ToolbarManager(self.tree_manager, self.close, self.showMinimized)

        # Создаем разделитель с вертикальной ориентацией
        self.splitter = self.ui.create_splitter(Qt.Vertical,
                                                sizes=[300, 100],
                                                handle_width=5,
                                                handle_style="QSplitter::handle { background: #ccc; }")

        # Создаем основной вертикальный layout
        main_layout = QVBoxLayout(self)
        # Убираем отступы у layout
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Создаем панель заголовка с кнопками управления
        title_layout = self.toolbar_manager.get_title_layout()
        main_layout.addWidget(title_layout)  # Добавляем панель инструментов в основной layout(макет)

        # Создаем виджет вкладок
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.West)  # Вкладки слева

        # Создаем деревья для каждой вкладки
        self._create_tabs_with_trees()

        # Добавляем вкладки в основной layout
        main_layout.addWidget(self.tab_widget)
        # Текстовое поле (нижняя часть)
        self.splitter.addWidget(self.content_viewer)
        # Добавляем разделитель в основной layout
        main_layout.addWidget(self.splitter)

    def _create_tabs_with_trees(self):
        """Создает вкладки с деревьями файлов"""
        # TODO 🚧 В разработке: 08.08.2025 перенести в класс DynamicTabManager
        if not self.tab_names:
            raise ValueError("Список имен вкладок не может быть пустым!")

        for tab_name in self.tab_names:
            # Создаем дерево для вкладки
            tree = self._create_file_tree(tab_name)

            # Добавляем вкладку с деревом
            self.tab_widget.addTab(tree, tab_name)

    def _create_file_tree(self, tab_name: str) -> QTreeWidget:
        """Создает дерево файлов для конкретной вкладки"""
        # TODO 🚧 В разработке: 08.08.2025 перенести в класс DynamicTabManager
        tree = QTreeWidget()
        tree.setHeaderHidden(True)
        tree.setColumnCount(1)

        # Заголовок дерева
        root = QTreeWidgetItem(tree, [f"Файлы: {tab_name}"])

        # Примерная структура файлов (в реальном приложении заменить на сканирование директории)
        files = {
            "Документы": ["doc1.txt", "doc2.pdf"],
            "Изображения": ["image1.png"],
            "Код": ["main.py", "utils.py"]
        }

        for folder, file_list in files.items():
            folder_item = QTreeWidgetItem(root, [folder])
            for file in file_list:
                file_item = QTreeWidgetItem(folder_item, [file])
                folder_item.addChild(file_item)
            root.addChild(folder_item)

        tree.expandAll()
        return tree

    def update_dock_position(self):
        """Обновляет позицию панели"""
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(
            screen.right() - self.width(),
            screen.top() + 100
        )

    def _on_file_deleted(self, path):
        # TODO 🚧 В разработке: 08.08.2025
        pass

    def _on_file_updated(self,path):
        # TODO 🚧 В разработке: 08.08.2025
        pass
