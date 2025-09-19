import sys
from PySide6.QtWidgets import QApplication, QSplitter, QTreeView, QListView
from PySide6.QtCore import QDir
from PySide6.QtWidgets import QFileSystemModel


def main():
    # Создаем приложение
    app = QApplication(sys.argv)

    # Создаем разделитель
    splitter = QSplitter()

    # Создаем модель файловой системы
    model = QFileSystemModel()
    model.setRootPath(QDir.currentPath())

    # Создаем древовидное представление
    tree = QTreeView(splitter)
    tree.setModel(model)
    tree.setRootIndex(model.index(QDir.currentPath()))

    # Создаем списковое представление
    list_view = QListView(splitter)
    list_view.setModel(model)
    list_view.setRootIndex(model.index(QDir.currentPath()))

    # Настраиваем окно
    splitter.setWindowTitle("Two views onto the same file system model")
    splitter.show()

    # Запускаем цикл событий
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())