
import json
from PySide6.QtWidgets import QFileIconProvider
from PySide6.QtCore import QAbstractItemModel, Qt, QModelIndex, QSize
from PySide6.QtGui import QIcon, QFont

from PySide6.QtGui import QColor

from models.st_md_file_tree_item import STMDFileTreeItem
from src.parsers.content_cache import ContentCache

class STMDFileTreeModel(QAbstractItemModel):
    """Модель данных для отображения структуры ST-файлов и MD-файлов в дереве"""
    # TODO 🚧 В разработке: 13.07.2025
    def __init__(self, content_cache: ContentCache, root_item=None, parent=None):
        super().__init__(parent)

        self.content_cache = content_cache   # TODO 28.08.2025 мертвый код self.content_cache
        self.style_settings = {
            "file": {"color": "#2a82da", "icon": "text-x-generic", "bold": False},
            "folder": {"color": "#006400", "icon": "folder", "bold": True},
            "template": {"color": "#00008B", "icon": "text-x-script", "bold": False},
            "markdown": {"color": "#8B008B", "icon": "text-markdown", "bold": False}
        }
        self.root_item = root_item or STMDFileTreeItem(["Root", "root", ""])
    # Основные методы модели
    def index(self, row, column, parent=QModelIndex()):
        """
          Создает и возвращает индекс модели для элемента с указанными строкой, столбцом и родителем.

          Этот метод является обязательной частью реализации QAbstractItemModel. Он используется фреймворком Qt
          для получения доступа к элементам данных в модели. Индекс создается для конкретного дочернего элемента
          указанного родительского элемента.

          Args:
              row (int): Номер строки (позиция дочернего элемента относительно родителя)
              column (int): Номер столбца (в нашем случае всегда 0)
              parent (QModelIndex): Индекс родительского элемента

          Returns:
              QModelIndex: Созданный индекс или недопустимый индекс, если запрошенная позиция не существует

          Сферы применения:
              Навигация по дереву, обработка пользовательских взаимодействий,
              реализация drag-and-drop, поиск элементов, валидация данных, обновление представлений,
              кастомная отрисовка элементов, работа с буфером обмена, сериализация состояния,
              интеграция с делегатами, отладка структуры модели.
          """
        # ✅ Реализовано: 15.08.2025

        # Проверяем существует ли запрошенный индекс в модели
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        # Получаем родительский элемент:
        # - Если parent валиден, берем связанный с ним элемент
        # - Если нет, используем корневой элемент модели
        parent_item = parent.internalPointer() if parent.isValid() else self.root_item
        # Получаем дочерний элемент по указанной позиции (row)
        child_item = parent_item.child_items[row]
        # Создаем и возвращаем индекс для дочернего элемента
        return self.createIndex(row, column, child_item)

    def parent(self, index):
        """
        Возвращает индекс родительского элемента для указанного дочернего элемента.

        Этот метод является обязательной частью реализации QAbstractItemModel. Он используется фреймворком Qt
        для навигации по иерархии данных. Если индекс соответствует корневому элементу или недопустим,
        возвращается пустой индекс.

        Args:
            index (QModelIndex): Индекс дочернего элемента, для которого нужно найти родителя

        Returns:
            QModelIndex: Индекс родительского элемента или пустой индекс, если:
                - Переданный индекс невалиден
                - Элемент является корневым
                - Родитель не найден

        Сферы применения:
                Навигация по иерархии, реализация collapse/expand в дереве,
                обработка drag-and-drop операций, сериализация выделения, восстановление состояния view,
                вычисление относительных путей, валидация операций перемещения, отображение breadcrumbs,
                поиск по дереву, копирование иерархических структур, отладка модели данных,
                импорт/экспорт древовидных структур, применение рекурсивных операций.

        """
        # ✅ Реализовано: 15.08.2025
        # Проверяем валидность переданного индекса
        if not index.isValid():
            return QModelIndex()

        # Получаем элемент, связанный с индексом (это дочерний элемент)
        child_item = index.internalPointer()

        # Получаем родительский элемент из свойств дочернего элемента
        parent_item = child_item.parent_item

        # Если родительский элемент является корневым, возвращаем пустой индекс
        # (так как корневой элемент не отображается в представлении)
        if parent_item == self.root_item:
            return QModelIndex()

        # Создаем и возвращаем индекс для родительского элемента
        return self.createIndex(parent_item.child_items.index(child_item), 0, parent_item)

    def rowCount(self, parent=QModelIndex()):
        """Возвращает количество дочерних элементов для указанного родительского индекса.

         Этот метод является обязательной частью реализации QAbstractItemModel. Он используется
         фреймворком Qt для определения:
         - Количества строк (дочерних элементов) для каждого родительского элемента
         - Необходимости отображения кнопки раскрытия (если rowCount > 0)
         - Области выделения при навигации

         Args:
             parent (QModelIndex): Индекс родительского элемента. Если невалиден или QModelIndex(),
                                  означает запрос количества элементов верхнего уровня.

         Returns:
             int: Количество дочерних элементов (0 если элемент не имеет детей или невалиден)

         Note:
             Для древовидных моделей возвращаемое значение соответствует количеству:
             - Дочерних папок для папки
             - Вложенных элементов для файла
             - Корневых элементов, если parent невалиден

         Сферы применения:
            Отрисовка древовидных структур, управление элементами интерфейса,
            динамическая подгрузка данных, валидация операций вставки/удаления, реализация
            drag-and-drop, вычисление размеров элементов, оптимизация производительности,
            построение контекстных меню, навигация с клавиатуры, сериализация состояния,
            экспорт иерархических данных, отладка структуры модели, ленивая инициализация,
            применение CSS-стилей, обработка жестов, управление фокусом.
         """
        # ✅ Реализовано: 15.08.2025

        # Получаем родительский элемент:
        # - Если parent валиден, используем связанный с ним элемент
        # - Если нет (корневой уровень), используем self.root_item
        parent_item = parent.internalPointer() if parent.isValid() else self.root_item
        # Возвращаем количество дочерних элементов:
        # - Для папки: количество вложенных файлов/папок
        # - Для файла: количество секций/шаблонов
        # - Для корня: количество элементов верхнего уровня
        return len(parent_item.child_items)

    def columnCount(self, parent=QModelIndex()):
        """Возвращает количество столбцов для элементов модели.

        Данный метод определяет горизонтальную структуру данных в представлении.
        В текущей реализации модель использует единственный столбец для отображения
        имени элемента, что является стандартным подходом для древовидных структур.

        Args:
            parent (QModelIndex): Индекс родительского элемента. В текущей реализации
                                не влияет на результат, так как структура колонок
                                едина для всех уровней иерархии.

        Returns:
            int: Всегда возвращает 1, что означает:
                 - Одиночную колонку для отображения имени элемента
                 - Отсутствие дополнительных колонок с метаданными

        Note:
            Несмотря на доступность информации о типе элемента (item_data[1]),
            она отображается через иконки (DecorationRole) и стили, а не в отдельной колонке.
            Изменение возвращаемого значения на 2+ потребует:
            1. Модификации метода data() для обработки column > 0
            2. Настройки заголовков в представлении
            3. Адаптации логики отображения

        Сферы применения:
            Отображение древовидных структур, настройка табличных представлений,
            интеграция с QDataWidgetMapper, экспорт данных в табличные форматы, сортировка элементов,
            фильтрация данных, кастомизация внешнего вида, работа с делегатами, печать документов,
            обработка буфера обмена, реализация drag-and-drop, валидация операций редактирования,
            построение отчетов, отладка структуры данных, адаптация для мобильных устройств
        """
        # ✅ Реализовано: 15.08.2025

        # Фиксированное значение 1 означает:
        # - Все элементы отображаются в одной колонке
        # - Для отображения типа используются иконки/стили
        return 1

    def data(self, index, role=Qt.DisplayRole):
        """Возвращает данные для элемента по указанному индексу и роли.

        Этот метод обеспечивает визуальное представление элементов дерева,
        включая текст, иконки, стили и пользовательские данные.

        Args:
            index (QModelIndex): Индекс запрашиваемого элемента
            role (int): Роль данных (DisplayRole, DecorationRole и др.)

        Returns:
            QVariant: Запрошенные данные или None если недоступно

        Сферы применения:
            Отображение текста элементов, показ иконок, настройка шрифтов,
            цветовое оформление, управление размерами строк, кастомизация отступов,
            передача метаданных, фильтрация данных, сортировка элементов, drag-and-drop,
            работа с буфером обмена, контекстные меню, доступность (a11y), печать документов,
            экспорт данных, интеграция с делегатами, валидация ввода, анимации интерфейса,
            тематическое оформление, ленивая загрузка, отладка структуры данных.
        """
        # ✅ Реализовано: 15.08.2025
        # Проверка валидности переданного индекса
        if not index.isValid():
            return None   # Возвращаем None для невалидных индексов

        # Получаем объект элемента, связанный с индексом
        item = index.internalPointer()
        # Извлекаем тип элемента из его данных (второй элемент в списке)
        item_type = item.item_data[1]
        # Получаем номер колонки для запрошенного индекса
        column = index.column()

        # Обработка роли для отображения основного текста
        if role == Qt.DisplayRole:
            # Безопасно возвращаем данные для колонки, если индекс в пределах
            return item.item_data[column] if column < len(item.item_data) else None

        # Обработка роли для отображения иконки (только для первой колонки)
        elif role == Qt.DecorationRole and column == 0:
            # Получаем иконку из кэша по имени из настроек стиля
            return self._get_icon(self.style_settings[item_type]["icon"])

        # Обработка роли для настройки шрифта
        elif role == Qt.FontRole:
            # Создаем объект шрифта
            font = QFont()
            # Устанавливаем жирность в зависимости от типа элемента
            font.setBold(self.style_settings[item_type]["bold"])
            return font

        # Обработка роли для цвета текста
        elif role == Qt.ForegroundRole:
            # Возвращаем цвет из настроек стиля для данного типа элемента
            return QColor(self.style_settings[item_type]["color"])

        # Обработка роли для размера элемента
        elif role == Qt.SizeHintRole:
            # Фиксированная высота строки 24 пикселя (ширина автоматическая)
            return QSize(0, 24)

        # Пользовательская роль 1: Уровень вложенности элемента
        elif role == Qt.UserRole + 1:
            # Вычисляем и возвращаем глубину вложенности элемента
            return self._calculate_item_level(item)
        # Пользовательская роль 2: Тип элемента
        elif role == Qt.UserRole + 2:
            # Возвращаем тип элемента (file, folder и т.д.)
            return item_type
        # Возвращаем None для необработанных ролей
        return None

    def flags(self, index):
        """Возвращает флаги состояния для элемента по указанному индексу.

        Определяет поведение и возможности взаимодействия с элементами:
        - Базовые флаги для всех элементов
        - Специальные флаги для папок
        - Возможности редактирования
        - Drag-and-drop поддержка

        Args:
            index (QModelIndex): Индекс элемента

        Returns:
            Qt.ItemFlags: Комбинация флагов для элемента

        Сферы применения:
            Управление выделением элементов, редактирование содержимого,
            drag-and-drop операции, работа с чекбоксами, контекстные меню, валидация действий,
            настройка доступности элементов, управление фокусом, интеграция с буфером обмена,
            кастомизация поведения элементов, контроль состояния тристатных чекбоксов,
            ограничение операций для разных типов пользователей, синхронизация с внешними системами,
            отладка взаимодействий, реализация специальных возможностей (a11y).
        """
        # ✅ Реализовано: 15.08.2025
        # Проверка валидности переданного индекса
        if not index.isValid():
            # Возвращаем пустые флаги для невалидных индексов
            return Qt.ItemFlag.NoItemFlags

        # Базовые флаги, применяемые ко всем элементам:
        # - ItemIsEnabled: элемент доступен для взаимодействия
        # - ItemIsSelectable: элемент можно выделять
        # - ItemIsDragEnabled: элемент можно перетаскивать
        flags = (Qt.ItemFlag.ItemIsEnabled |
                 Qt.ItemFlag.ItemIsSelectable |
                 Qt.ItemFlag.ItemIsDragEnabled)

        # Получаем объект элемента, связанный с индексом
        item = index.internalPointer()
        if not item:
            return flags

        # Флаги для редактируемых элементов
        if item.type in ["file", "markdown", "template"]:
            # ItemIsEditable позволяет редактировать текст элемента
            flags |= Qt.ItemFlag.ItemIsEditable

        # Специальные флаги для элементов типа "folder":
        if item.type == "folder":
            # ItemIsDropEnabled разрешает "бросать" другие элементы в эту папку
            flags |= Qt.ItemFlag.ItemIsDropEnabled
            # Дополнительные флаги для непустых папок:
            if len(item.child_items) > 0:
                # ItemIsAutoTristate: автоматическое тристатное состояние для чекбоксов
                # ItemIsUserCheckable: элемент может быть отмечен чекбоксом
                # ItemIsTristate: поддерживает три состояния (выбран/не выбран/частично выбран)
                flags |= (Qt.ItemFlag.ItemIsAutoTristate |
                          Qt.ItemFlag.ItemIsUserCheckable
                          )
        # Возвращаем итоговую комбинацию флагов
        return flags

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

        Сферы применения:
            Удаление файлов и папок, очистка структуры данных, отмена операций добавления,
            синхронизация с файловой системой, реализация команд удаления в undo/redo стеке, обработка
            drag-and-drop перемещений, обновление данных из внешних источников, валидация бизнес-правил,
            автоматическая очистка временных элементов, работа с корзиной/архивом, пакетное удаление,
            интеграция с системами контроля версий, обработка конфликтов синхронизации.
        """
        # ✅ Реализовано: 15.08.2025

        # Определяем родительский элемент:
        # - Если parent невалиден, берем корневой элемент
        # - Иначе получаем элемент через internalPointer()
        if not parent.isValid():
            parent_item = self.root_item
        else:
            parent_item = parent.internalPointer()

        # Проверка корректности индекса строки:
        # - Должен быть >= 0
        # - Должен быть меньше количества дочерних элементов
        if row < 0 or row >= len(parent_item.child_items):
            return False
        # Уведомляем view о начале удаления:
        # - parent: индекс родителя
        # - row, row: диапазон удаляемых строк (одна строка)
        self.beginRemoveRows(parent, row, row)
        # Непосредственное удаление элемента:
        # - Удаляем из списка дочерних элементов родителя
        parent_item.child_items.pop(row)
        # Уведомляем view о завершении удаления
        self.endRemoveRows()
        # Возвращаем флаг успешного выполнения
        return True

    def has_children(self, parent=QModelIndex()):
        """Определяет, содержит ли указанный узел дочерние элементы.

        Используется Qt для визуального отображения иерархии и оптимизации работы с деревом.
        Применение: отображение стрелок раскрытия, ленивая загрузка, валидация операций.

        Args:
            parent (QModelIndex, optional): Индекс проверяемого узла.
                Если невалиден (по умолчанию), проверяет корневой уровень.

        Returns:
            bool: True если узел содержит хотя бы один дочерний элемент, иначе False.

        Операции где используется: отрисовка дерева, динамическая загрузка данных,
        проверка перед удалением, контекстные меню, drag-and-drop операции.
        """
        # ✅ Реализовано: 16.08.2025

        # Проверка корневого уровня (когда parent невалиден)
        if not parent.isValid():
            # Возвращаем True, если корневой элемент имеет детей
            return len(self.root_item.child_items) > 0
        # Получаем объект элемента, связанный с индексом
        item = parent.internalPointer()
        # Проверяем наличие дочерних элементов у узла
        return len(item.child_items) > 0

    def canFetchMore(self, parent):
        """Определяет возможность динамической подгрузки дочерних элементов для узла.

        Используется для реализации ленивой загрузки данных в дереве. Метод проверяет,
        существуют ли дочерние элементы, которые еще не были загружены в модель.

        Args:
            parent (QModelIndex): Индекс родительского узла, для которого проверяется
                                возможность подгрузки. Невалидный индекс означает корень.

        Returns:
            bool: True если узел может иметь дополнительные дочерние элементы для подгрузки,
                  False если все дети уже загружены или узел не поддерживает подгрузку.

        Note:
            Для работы с ленивой загрузкой требуется реализация fetchMore().
            По умолчанию возвращает False, так как базовый QAbstractItemModel
            не поддерживает ленивую загрузку.

        Сферы применения:
            ленивая загрузка данных, работа с большими иерархиями,
            оптимизация памяти, загрузка из удалённых источников, динамическое обновление дерева,
            отложенная инициализация веток, обработка частично загруженных структур,
            интеграция с базами данных, REST API, файловыми системами.
        """
        # ✅ Реализовано: 16.08.2025

        # Проверка невалидного родителя (корневого уровня)
        if not parent.isValid():
            return False  # Корневой уровень всегда полностью загружен  ???

        # Получаем объект элемента, связанный с индексом
        item = parent.internalPointer()

        # Проверяем наличие неподгруженных дочерних элементов
        return bool(item.child_items)  # True если есть хотя бы один ребенок

    def _get_icon(self, icon_name):
        """Возвращает QIcon для указанного имени иконки.

        Args:
            icon_name (str): Имя иконки из настроек стиля

        Returns:
            QIcon: Объект иконки или пустая иконка, если не найдена
        """
        # Создаем провайдер иконок файловой системы
        icon_provider = QFileIconProvider()

        # Сопоставление имен иконок с системными иконками
        icon_mapping = {
            "text-x-generic": icon_provider.icon(QFileIconProvider.IconType.File),
            "folder": icon_provider.icon(QFileIconProvider.IconType.Folder),
            "text-x-script": icon_provider.icon(QFileIconProvider.IconType.File),
            "text-markdown": icon_provider.icon(QFileIconProvider.IconType.File)
        }

        # Возвращаем соответствующую иконку или пустую, если не найдена
        return icon_mapping.get(icon_name, QIcon())

    def _calculate_item_level(self, item):
        """
            Вычисляет уровень вложенности элемента в дереве.

            Args:
                item: Элемент дерева (STMDFileTreeItem)

            Returns:
                int: Глубина вложенности (0 для корневых элементов)
        """
        # ✅ Реализовано: 15.08.2025
        # Инициализация счетчика уровня
        level = 0
        # Получаем родительский элемент
        parent = item.parent_item

        # Поднимаемся по иерархии родителей:
        # - Пока есть родитель и это не корневой элемент
        while parent and parent != self.root_item:
            # Увеличиваем уровень вложенности
            level += 1
            # Переходим к родителю текущего родителя
            parent = parent.parent_item
        # Возвращаем итоговый уровень вложенности
        return level

    def _build_tree(self, nodes, parent):
        """Рекурсивно строит иерархическую структуру дерева из переданных данных.

        Преобразует древовидную структуру в формате словарей/списков в связанные
        объекты STMDFileTreeItem, сохраняя исходную иерархию.

        Args:
            nodes (list[dict]): Список узлов для обработки, где каждый узел содержит:
                - name (str): Имя элемента
                - type (str): Тип элемента ('file', 'folder' и т.д.)
                - content (str, optional): Содержимое элемента
                - children (list[dict], optional): Вложенные элементы
            parent (STMDFileTreeItem): Родительский элемент для создаваемых узлов

        Returns:
            None: Метод модифицирует переданный parent_item, добавляя детей

        Note:
            Для корректной работы требует предварительно вызванных beginInsertRows()
            при добавлении элементов верхнего уровня.

        Сферы применения: инициализация модели, динамическая подгрузка данных,
        импорт из JSON/XML, восстановление состояния, копирование поддеревьев,
        обработка результатов парсинга, тестирование, отладка структуры данных.
        """
        # TODO 16.08.2025 - метод _build_tree посмотреть оставить приватным или сделать публичным
        for node in nodes:
            item = STMDFileTreeItem(data=[node['name'], node['type'], node.get('content', '')], parent=parent)
            parent.child_items.append(item)
            if 'children' in node:
                self._build_tree(node['children'], item)

    def add_st_file(self, file_path, result_parser: dict):
        # TODO 16.08.2025 Возможно прийдется удалить add_st_file - метод устарел

        # Получаем результат парсинга, который теперь содержит и структуру, и имя корневой папки
        result = result_parser

        print("Parsed structure:")
        print(json.dumps(result['structure'], indent=2, ensure_ascii=False))
        print(f"Root name: {result['root_name']}")  # Отладочный вывод

        # Извлекаем имя корневой папки (например, "Новый1")
        root_name = result['root_name']

        # Извлекаем структуру файла для построения дерева
        structure = result['structure']

        # Начинаем вставку данных в модель
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())

        # Создаем элемент для корневой папки с именем из файла
        file_item = STMDFileTreeItem([root_name, "file", file_path], self.root_item)

        # Строим поддерево на основе структуры файла
        self._build_tree(structure, file_item)

        # Добавляем элемент в корневую папку модели
        self.root_item.child_items.append(file_item)

        # Завершаем вставку
        self.endInsertRows()
        # self.print_tree()
        print(f"Структура из парсера: {json.dumps(structure, indent=2)}")

    def add_file(self, file_path: str, parsed_data: dict):
        """
         Добавляет в модель структуру файла на основе данных от парсера.
         Универсальный метод, который работает с любым типом файла (.st, .md и т.д.),
         если parsed_data имеет ожидаемую структуру.

         Args:
             file_path: Полный путь к файлу.
             parsed_data: Словарь с результатами парсинга. Содержит ключи:
                 - 'root_name': Имя корневого элемента для этого файла.
                 - 'structure': Иерархическая структура содержимого файла.
         """
        # ✅ Реализовано: 26.08.2025
        if not parsed_data or not isinstance(parsed_data, dict):
            print(f"Warning: недопустимые обработанные данные для файла {file_path}")
            return

        # 1. Извлекаем данные из словаря. Это ЕДИНЫЙ формат для всех парсеров.
        root_name = parsed_data.get('root_name', 'Unknown')
        structure = parsed_data.get('structure', [])

        # 2. Определяем тип корневого элемента на основе расширения файла
        # или других критериев. Это лучше, чем надеяться на парсер.
        if file_path.endswith('.st'):
            root_type = "file"
        elif file_path.endswith('.md'):
            root_type = "markdown"
        else:
            root_type = "file"  # fallback

        # 3. Создаем корневой элемент для ЭТОГО ФАЙЛА.
        # Он будет дочерним элементом общего корня модели (self.root_item).
        # В его данные мы кладем путь к файлу, чтобы потом его можно было открыть.
        file_item = STMDFileTreeItem([root_name, root_type, file_path], self.root_item)

        # 4.Вычисляем позицию, куда будет вставлен новый элемент (в конец списка детей корня)
        new_row_position = self.rowCount()  # Текущее количество детей у корня
        self.beginInsertRows(QModelIndex(), new_row_position, new_row_position)  # <- ВЫЗОВ ЗДЕСЬ

        # 5. Старый добрый _build_tree строит поддерево из structure.
        # Обратите внимание: мы передаем file_item в качестве родителя.
        # Вся структура (папки, шаблоны) будет построена внутри этого file_item.
        self._build_tree(structure, file_item)

        # 6. Добавляем корневой элемент файла в корень всей модели.
        self.root_item.child_items.append(file_item)

        # 4. ОПОВЕЩАЕМ VIEW о завершении добавления!
        self.endInsertRows()  # <- ВЫЗОВ ЗДЕСЬ

    def get_item_level(self, index):
        """Возвращает уровень вложенности элемента в иерархии модели.

        Вычисляет глубину вложенности элемента, подсчитывая количество родителей
        между текущим элементом и корнем дерева. Корневые элементы имеют уровень 0.

        Args:
            index (QModelIndex): Индекс элемента, для которого определяется уровень.
            Должен быть валидным индексом модели.

        Returns:
            int: Уровень вложенности (0 для корня, 1 для его непосредственных детей и т.д.).

        Raises:
            ValueError: Если передан невалидный индекс (необязательно, зависит от требований).

        Сферы применения: визуальное оформление дерева, валидация операций,
        применение CSS-стилей, логирование структуры, ограничение глубины вложенности,
        экспорт данных, анимации элементов, анализ сложности структуры,
        подсветка родительских веток, настройка отступов.
        """
        # ✅ Реализовано: 16.08.2025

        # Инициализация счетчика уровня
        level = 0

        # Получаем индекс родительского элемента
        current_parent = index.parent()

        # Рекурсивно поднимаемся по иерархии родителей
        while current_parent.isValid():
            # Увеличиваем уровень для каждого родителя
            level += 1
            # Переходим к родителю текущего родителя
            current_parent = current_parent.parent()

        # Возвращаем итоговый уровень вложенности
        return level
    def get_item_path(self, index):
        """
        Возвращает путь к файлу для указанного элемента дерева.

        Аргументы:
            index (QModelIndex): Индекс элемента, для которого требуется получить путь к файлу.

        Возвращаемое значение:
            str или None: Строка с абсолютным или относительным путем к файлу, если элемент является файлом или markdown-файлом.
            Если элемент не является файлом или индекс невалиден, возвращается None.
            ---
            str | None: Абсолютный путь к файлу для файловых элементов,
                  None для папок/невалидных элементов.

        Описание:
            Метод проверяет валидность переданного индекса. Если индекс невалиден, возвращает None.
            Затем получает внутренний объект элемента через index.internalPointer().
            Если тип элемента (item.item_data[1]) равен 'file' или 'markdown', метод возвращает путь к файлу,
            который хранится в item.item_data[2]. Если элемент не является файлом или markdown-файлом, возвращает None.

        Сферы применения:
            Открытие файлов в редакторе, мониторинг изменений файлов,
            обновление содержимого при изменении файла, экспорт данных, привязка внешних
            инструментов, логирование операций, отображение полного пути в UI,
            проверка прав доступа, синхронизация с файловой системой.
        """
        # ✅ Реализовано: 16.08.2025

        # Проверка валидности переданного индекса
        if not index.isValid():
            return None # Невалидный индекс → нет пути

        # Получение объекта элемента, связанного с индексом
        item = index.internalPointer()
        # Проверка типа элемента (файл или markdown-документ)
        if item.item_data[1] in ['file', 'markdown']:
            # Возвращаем путь из данных элемента (предполагается item_data[2])
            return item.item_data[2]
        # Возвращаем None для неподходящих типов элементов
        return None

    def get_item_type(self, index):
        """
        Возвращает тип элемента файлового дерева.

        Извлекает тип элемента из внутренней структуры данных для принятия решений
        о дальнейшей обработке элемента. Тип определяется при создании элемента.

        Аргументы:
            index (QModelIndex): Индекс элемента, для которого требуется определить тип. Должен быть валидным.

        Возвращаемое значение:
            str: Строковый идентификатор типа элемента. Возможные значения:
             - 'file' - обычный файл
             - 'folder' - папка/директория
             - 'markdown' - markdown-документ
             - 'template' - шаблон

       Raises:
            RuntimeError: Если индекс невалиден или элемент не существует

        Описание:
            Метод получает внутренний объект элемента с помощью index.internalPointer(),
            после чего извлекает из его структуры данных значение, определяющее тип элемента.
            Обычно это строка, обозначающая, является ли элемент файлом, папкой и т.д.
            Тип хранится во втором элементе item_data (item.item_data[1]).

       Сферы применения:
            Фильтрация элементов, определение доступных операций,
            применение стилей отображения, построение контекстных меню, валидация действий,
            сортировка элементов, группировка данных, логирование, экспорт в другие форматы,
            интеграция с плагинами, управление видимостью элементов.
        """
        # ✅ Реализовано: 16.08.2025

        # Получаем объект элемента, связанный с индексом
        item = index.internalPointer()
        # Извлекаем тип элемента из данных (второй элемент в item_data)
        return item.item_data[1]  # 'folder', 'file' и т.д.

    def update_file_item_old(self, file_path: str, new_data: dict) -> bool:
        """Находит и обновляет элемент по пути файла с уведомлением view"""
        # TODO 🚧 В разработке: 29.08.2025 метод устарел update_file_item_old можно удалить
        # Добавляем проверку на валидность new_data
        print(f"DEBUG🔍: Поиск файла '{file_path}' в модели")
        if not new_data or not isinstance(new_data, dict):
            print(f"Warning: недопустимые новые данные для файла {file_path}")
            return False
        for row in range(self.rowCount()):
            index = self.index(row, 0)
            if not index.isValid():
                continue

            item = index.internalPointer()
            if not item:
                continue

            # Проверяем, что это файл и путь совпадает
            if (len(item.item_data) > 2 and
                    item.item_data[1] in ['file', 'markdown', 'template'] and
                    item.item_data[2] == file_path):

                # Сохраняем старые данные для сравнения
                old_children_count = len(item.child_items)

                # Очищаем старых детей с уведомлением
                if old_children_count > 0:
                    self.beginRemoveRows(index, 0, old_children_count - 1)
                    item.child_items.clear()
                    self.endRemoveRows()

                # Строим новую структуру
                # Безопасное получение данных с проверками
                root_name = new_data.get('root_name', 'Unknown') if new_data else 'Unknown'
                structure = new_data.get('structure', []) if new_data else []

                # Обновляем имя корневого элемента
                if len(item.item_data) > 0:
                    item.item_data[0] = root_name

                # Добавляем новых детей с уведомлением
                if structure:
                    new_children_count = len(structure)
                    self.beginInsertRows(index, 0, new_children_count - 1)
                    self._build_tree(structure, item)
                    self.endInsertRows()

                # Уведомляем об изменении самого элемента
                self.dataChanged.emit(index, index, [Qt.DisplayRole])
                print(f"DEBUG✅: Файл найден в строке {row}, обновляем...")
                return True
            #временно для проверки
            else:
                if len(item.item_data) > 2:
                    print(f"DEBUG: Строка {row}: {item.item_data[2]} (тип: {item.item_data[1]})")
        print(f"DEBUG❌: Файл '{file_path}' не найден в модели")
        return False

    def update_file_item(self, file_path: str, new_data: tuple) -> bool:
        """Находит и обновляет элемент по пути файла с уведомлением view"""
        print(f"DEBUG🔍: Поиск файла '{file_path}' в модели")

        # Проверяем, что new_data - кортеж и содержит 2 элемента
        if not new_data or not isinstance(new_data, tuple) or len(new_data) != 2:
            print(f"Warning: недопустимые новые данные для файла {file_path}: {type(new_data)}")
            return False

        # Извлекаем тип файла и данные
        file_type, parsed_data = new_data

        # Проверяем, что данные парсинга - словарь
        if not isinstance(parsed_data, dict):
            print(f"Warning: недопустимые данные парсинга для файла {file_path}: {type(parsed_data)}")
            return False

        # Проверяем, что это поддерживаемый тип файла
        if file_type not in ['file', 'markdown']:
            print(f"Warning: неподдерживаемый тип файла {file_type} для {file_path}")
            return False

        # Работаем с данными парсинга
        for row in range(self.rowCount()):
            index = self.index(row, 0)
            if not index.isValid():
                continue

            item = index.internalPointer()
            if not item:
                continue

            # Проверяем, что это файл и путь совпадает
            if (len(item.item_data) > 2 and
                    item.item_data[1] in ['file', 'markdown'] and
                    item.item_data[2] == file_path):

                # Сохраняем старые данные для сравнения
                old_children_count = len(item.child_items)

                # Очищаем старых детей с уведомлением
                if old_children_count > 0:
                    self.beginRemoveRows(index, 0, old_children_count - 1)
                    item.child_items.clear()
                    self.endRemoveRows()

                # Строим новую структуру
                # Безопасное получение данных с проверками
                root_name = parsed_data.get('root_name', 'Unknown')
                structure = parsed_data.get('structure', [])

                # Обновляем имя корневого элемента
                if len(item.item_data) > 0:
                    item.item_data[0] = root_name

                # Добавляем новых детей с уведомлением
                if structure:
                    new_children_count = len(structure)
                    self.beginInsertRows(index, 0, new_children_count - 1)
                    self._build_tree(structure, item)
                    self.endInsertRows()

                # Уведомляем об изменении самого элемента
                self.dataChanged.emit(index, index, [Qt.DisplayRole])
                print(f"DEBUG✅: Файл найден в строке {row}, обновляем...")
                return True

            # Временно для проверки
            else:
                if len(item.item_data) > 2:
                    print(f"DEBUG: Строка {row}: {item.item_data[2]} (тип: {item.item_data[1]})")

        print(f"DEBUG❌: Файл '{file_path}' не найден в модели")
        return False
    def refresh_view(self, parent_index=QModelIndex()):
        """
        Принудительно обновляет представление для указанного родительского элемента
        и всех его потомков.

        Args:
            parent_index: Индекс родительского элемента для обновления
                         (по умолчанию - корневой уровень)
        """
        if not parent_index.isValid():
            # Обновление всей модели
            self.beginResetModel()
            self.endResetModel()
        else:
            # Обновление конкретной ветки
            row_count = self.rowCount(parent_index)
            if row_count > 0:
                top_left = self.index(0, 0, parent_index)
                bottom_right = self.index(row_count - 1, 0, parent_index)
                self.dataChanged.emit(top_left, bottom_right)

    # Если нужно обновлять конкретные элементы(Нужно определится)
    def refresh_item(self, file_path: str):
        """Обновляет конкретный элемент по пути файла"""
        # TODO 🚧 В разработке: 28.08.2025 мертвый код refresh_item
        for row in range(self.rowCount()):
            index = self.index(row, 0)
            item = index.internalPointer()

            if (item and len(item.item_data) > 2 and
                    item.item_data[2] == file_path):
                self.dataChanged.emit(index, index)
                return True
        return False
    #------------(Нужно определится)

