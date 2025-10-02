from pathlib import Path
import os

from PySide6.QtGui import QAction


from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QMainWindow, QTreeView, QTabWidget, QTextEdit, QVBoxLayout, QWidget, QSplitter,
                               QHBoxLayout, QLabel, QLineEdit, QToolBar, QApplication, QFileSystemModel)
class FileEditorWindow(QMainWindow):

    def __init__(self, parent = None):
        super().__init__(parent)
        self.template_name = "Тут будет текст"
        self.setWindowTitle("Редактор файлов")
        self.setMinimumSize(800, 500)
        self._init_ui()
    def _init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(10)

        #Создаем горизонтальный разделитель
        self.main_splitter = QSplitter(Qt.Horizontal)



        # ЛЕВАЯ ЧАСТЬ: Дерево файлов
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(3, 3, 3, 3)

        # Создаем и настраиваем дерево файлов
        self.tree_view = QTreeView() # Древовидная структура
        self._setup_file_tree()
        left_layout.addWidget(QLabel("Файловая система:")) # Добавляем виджет с заголовком
        left_layout.addWidget(self.tree_view)

        # ПРАВАЯ ЧАСТЬ: Редактор
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(3, 3, 3, 3)

        # Панель инструментов редактора
        toolbar_container = QWidget()
        toolbar_layout = QHBoxLayout(toolbar_container)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)

        self.template_edit = QLineEdit("Новый файл")
        toolbar_layout.addWidget(QLabel("Имя файла:"))
        toolbar_layout.addWidget(self.template_edit)
        toolbar_layout.addStretch()  # Растягивающее пространство



        #Текстовый редактор 1
        self.text_editor = QTextEdit()
        self.text_editor.setPlaceholderText("Введите текст здесь...")

        # Текстовый редактор 2
        self.text_editor2 = QTextEdit()
        self.text_editor2.setPlaceholderText("Введите текст здесь...")

        right_layout.addWidget(toolbar_container)
        # Создаем вертикальный разделитель для текстовых редакторов
        editor_splitter = QSplitter(Qt.Vertical)
        editor_splitter.addWidget(self.text_editor)
        editor_splitter.addWidget(self.text_editor2)

        # Настраиваем пропорции разделителя редакторов (50/50)
        editor_splitter.setSizes([300, 300])

        # Добавляем разделитель в правый layout
        right_layout.addWidget(editor_splitter)



        # Добавляем левую часть в разделитель
        self.main_splitter.addWidget(left_container)
        # Добавляем правую часть в разделитель
        self.main_splitter.addWidget(right_container)

        # Устанавливаем пропорции (30% дерево, 70% редактор)
        self.main_splitter.setSizes([220, 580])

        # Добавляем разделитель в основной layout
        main_layout.addWidget(self.main_splitter)

    def _setup_file_tree(self):
        """Настройка дерева файловой системы"""
        model = QFileSystemModel() # Строим файловую систему
        model.setRootPath("") # определяем корневой путь
        self.tree_view.setModel(model) # Устанавливаем модель в древовидную структуру
        self.tree_view.setRootIndex(model.index(""))
        self.tree_view.setColumnWidth(0, 250) # Ширина первой колонки

        # Скрываем ненужные колонки
        self.tree_view.hideColumn(1)
        self.tree_view.hideColumn(2)
        self.tree_view.hideColumn(3)


if __name__ == "__main__":
    app = QApplication([])
    window = FileEditorWindow()
    window.show()
    app.exec()