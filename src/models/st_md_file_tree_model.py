from PySide6.QtCore import QAbstractItemModel
import json
from PySide6.QtWidgets import QFileIconProvider
from PySide6.QtCore import QAbstractItemModel, Qt, QModelIndex, QSize
from PySide6.QtGui import QIcon, QFont

from PySide6.QtGui import QColor

from models.st_md_file_tree_item import STMDFileTreeItem


class STMDFileTreeModel(QAbstractItemModel):
    """Модель данных для отображения структуры ST-файлов и MD-файлов в дереве"""
    # TODO 🚧 В разработке: 13.07.2025
    def __init__(self, root_item=None, parent=None):
        super().__init__(parent)
        self.root_item = root_item or STMDFileTreeItem(["Root", "folder"])
    # Основные методы модели
    def index(self, row, column, parent=QModelIndex()):
        """Создает индекс для элемента"""
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        parent_item = parent.internalPointer() if parent.isValid() else self.root_item
        child_item = parent_item.child_items[row]
        return self.createIndex(row, column, child_item)

    def parent(self, index):
        """Возвращает родителя элемента"""
        if not index.isValid():
            return QModelIndex()

        child_item = index.internalPointer()
        parent_item = child_item.parent_item

        if parent_item == self.root_item:
            return QModelIndex()

        return self.createIndex(parent_item.child_items.index(child_item), 0, parent_item)

    def rowCount(self, parent=QModelIndex()):
        """Количество строк (дочерних элементов)"""
        parent_item = parent.internalPointer() if parent.isValid() else self.root_item
        return len(parent_item.child_items)

    def columnCount(self, parent=QModelIndex()):
        """Количество колонок (фиксировано: Имя и Тип)"""
        return 1

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        item = index.internalPointer()

        if role == Qt.DisplayRole:
            return item.item_data[0]  # Имя элемента

        elif role == Qt.DecorationRole:
            type_ = item.item_data[1]
            return {
                "file": QIcon.fromTheme("text-x-generic"),
                "folder": QIcon.fromTheme("folder"),
                "markdown": QIcon.fromTheme("text-markdown")
            }.get(type_, QIcon())

        elif role == Qt.UserRole:  # Для доступа к полным данным
            return item.item_data

        return None

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable
    def removeRow(self, row, parent=QModelIndex()):
        """
        Удаляет строку (элемент) из модели.

        Аргументы:
            row (int): Номер строки (индекс элемента), который требуется удалить из родительского элемента.
            parent (QModelIndex, необязательный): Индекс родительского элемента, из которого будет удаляться строка.
            По умолчанию используется корневой элемент (QModelIndex()).

        Возвращаемое значение:
            bool: True, если удаление прошло успешно, иначе False.

        Описание:
            Метод реализует стандартное удаление строки в модели, основанной на QAbstractItemModel.
            Если parent невалиден, используется корневой элемент модели (self.root_item) как родитель.
            Если переданный индекс строки некорректен (отрицательный или превышает количество дочерних элементов),
            возвращается False.

            Для удаления вызываются beginRemoveRows и endRemoveRows для корректного обновления модели и интерфейса.
            После этого соответствующий дочерний элемент удаляется из списка child_items родительского элемента.
            При успешном удалении возвращается True.
        """
        if not parent.isValid():
            parent_item = self.root_item
        else:
            parent_item = parent.internalPointer()

        if row < 0 or row >= len(parent_item.child_items):
            return False

        self.beginRemoveRows(parent, row, row)
        parent_item.child_items.pop(row)
        self.endRemoveRows()
        return True

    def get_item_path(self, index):
        """
        Возвращает путь к файлу для указанного элемента дерева.

        Аргументы:
            index (QModelIndex): Индекс элемента, для которого требуется получить путь к файлу.

        Возвращаемое значение:
            str или None: Строка с абсолютным или относительным путем к файлу, если элемент является файлом или markdown-файлом.
            Если элемент не является файлом или индекс невалиден, возвращается None.

        Описание:
            Метод проверяет валидность переданного индекса. Если индекс невалиден, возвращает None.
            Затем получает внутренний объект элемента через index.internalPointer().
            Если тип элемента (item.item_data[1]) равен 'file' или 'markdown', метод возвращает путь к файлу,
            который хранится в item.item_data[2]. Если элемент не является файлом или markdown-файлом, возвращает None.
        """
        if not index.isValid():
            return None

        item = index.internalPointer()
        if item.item_data[1] in ['file', 'markdown']:
            return item.item_data[2]
        return None

    def get_item_type(self, index):
        """
        Возвращает тип элемента файлового дерева.

        Аргументы:
            index (QModelIndex): Индекс элемента, для которого требуется определить тип.

        Возвращаемое значение:
            str: Тип элемента, например, 'file', 'folder' и т.д.

        Описание:
            Метод получает внутренний объект элемента с помощью index.internalPointer(),
            после чего извлекает из его структуры данных значение, определяющее тип элемента.
            Обычно это строка, обозначающая, является ли элемент файлом, папкой и т.д.
            Тип хранится во втором элементе item_data (item.item_data[1]).
        """
        item = index.internalPointer()
        return item.item_data[1]  # 'folder', 'file' и т.д.

