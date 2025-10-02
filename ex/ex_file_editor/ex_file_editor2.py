from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QMainWindow, QTreeView, QTabWidget, QTextEdit, QVBoxLayout, 
                               QWidget, QSplitter, QHBoxLayout, QLabel, QLineEdit, 
                               QToolBar, QApplication, QFileSystemModel)


class FileEditorWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Редактор файлов") # Заголовок окна
        self.setMinimumSize(800, 500)          # Размер окна

        self.template_name = "Тут будет текст"
        
        # Инициализируем UI
        self._init_ui()
        
    def _init_ui(self):
        """Инициализация пользовательского интерфейса"""
        main_widget = QWidget()                     # центральный виджет окна
        self.setCentralWidget(main_widget)          # устанавливаем как центральный виджет окна
        main_layout = QVBoxLayout(main_widget)      # вертикальное расположение
        main_layout.setContentsMargins(5, 5, 5, 5)  # установка минимального отступа
        main_layout.setSpacing(5)                   # Устанавливаем промежуток между виджетами

        # Создаем горизонтальный разделитель
        self.main_splitter = QSplitter(Qt.Horizontal)

        # ЛЕВАЯ ЧАСТЬ: Дерево файлов
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Создаем и настраиваем дерево файлов
        self.tree_view = QTreeView()
        self._setup_file_tree()
        left_layout.addWidget(QLabel("Файловая система:"))
        left_layout.addWidget(self.tree_view)
        
        # ПРАВАЯ ЧАСТЬ: Редактор
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Панель инструментов редактора
        toolbar_container = QWidget()
        toolbar_layout = QHBoxLayout(toolbar_container)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        
        self.template_edit = QLineEdit("Новый файл")
        toolbar_layout.addWidget(QLabel("Имя файла:"))
        toolbar_layout.addWidget(self.template_edit)
        toolbar_layout.addStretch()  # Растягивающее пространство
        
        # Текстовый редактор
        self.text_editor = QTextEdit()
        self.text_editor.setPlaceholderText("Введите текст здесь...")
        
        right_layout.addWidget(toolbar_container)
        right_layout.addWidget(self.text_editor)

        # Добавляем обе части в разделитель
        self.main_splitter.addWidget(left_container)
        self.main_splitter.addWidget(right_container)
        
        # Устанавливаем пропорции (30% дерево, 70% редактор)
        self.main_splitter.setSizes([240, 560])
        
        # Добавляем разделитель в основной layout
        main_layout.addWidget(self.main_splitter)
        
    def _setup_file_tree(self):
        """Настройка дерева файловой системы"""
        model = QFileSystemModel()
        model.setRootPath("")
        self.tree_view.setModel(model)
        self.tree_view.setRootIndex(model.index(""))
        self.tree_view.setColumnWidth(0, 250)  # Ширина первой колонки
        
        # Скрываем ненужные колонки
        self.tree_view.hideColumn(1)  # Размер
        self.tree_view.hideColumn(2)  # Тип
        self.tree_view.hideColumn(3)  # Дата изменения


# Запуск приложения
if __name__ == "__main__":
    app = QApplication([])
    window = FileEditorWindow()
    window.show()
    app.exec()