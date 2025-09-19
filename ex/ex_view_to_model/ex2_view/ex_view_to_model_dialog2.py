import sys
from PySide6.QtWidgets import QApplication, QSplitter, QTreeView, QListView, QFileDialog, QMessageBox
from PySide6.QtCore import QDir
from PySide6.QtWidgets import QFileSystemModel


def main():
    # Создаем приложение
    app = QApplication(sys.argv)

    # Диалог выбора папки
    folder_path = QFileDialog.getExistingDirectory(
        None,
        "Выберите папку для отображения",
        QDir.currentPath(),
        QFileDialog.ShowDirsOnly
    )

    # Если пользователь отменил выбор
    if not folder_path:
        QMessageBox.information(None, "Информация", "Выбор папки отменен")
        sys.exit(0)

    # Проверяем, существует ли выбранная папка
    if not QDir(folder_path).exists():
        QMessageBox.critical(None, "Ошибка", f"Папка не существует: {folder_path}")
        sys.exit(1)

    # Создаем разделитель
    splitter = QSplitter()

    # Создаем модель файловой системы
    model = QFileSystemModel()
    model.setRootPath(folder_path)  # Устанавливаем выбранную папку как корневую

    # Создаем древовидное представление
    tree = QTreeView(splitter)
    tree.setModel(model)
    tree.setRootIndex(model.index(folder_path))  # Показываем выбранную папку

    # Создаем списковое представление
    list_view = QListView(splitter)
    list_view.setModel(model)
    list_view.setRootIndex(model.index(folder_path))  # Показываем выбранную папку

    # Настраиваем окно
    splitter.setWindowTitle(f"Два представления одной файловой системы: {folder_path}")
    splitter.resize(800, 600)  # Устанавливаем размер окна

    # Настраиваем разделитель
    splitter.setSizes([400, 400])  # Равное разделение области

    splitter.show()

    # Запускаем цикл событий
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())