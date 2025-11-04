from abc import ABC, abstractmethod
from pathlib import Path

from PySide6.QtCore import Signal, QObject
from PySide6.QtWidgets import QWidget

from operation.delta_operations import Delta


class Meta(type(QObject), type(ABC)):
    """Метакласс для разрешения конфликта между QObject и ABC"""
    pass


class BaseFileEditor(QWidget, ABC, metaclass=Meta):
    """
        Абстрактный базовый класс для всех редакторов файлов.
        Наследуется от QWidget, так как каждый редактор будет виджетом для размещения в UI.
    """
    # Сигналы

    # Сигнал для отмены/повтора
    undo_available = Signal(bool)
    redo_available = Signal(bool)

    # Сигнал об изменении модифицированного состояния (is_modified)
    modification_changed = Signal(bool)
    # Сигнал о том, что файл успешно сохранен по новому пути
    file_saved_as = Signal(Path)
    # Сигнал о возникновении ошибки (сообщение, уровень)
    error_occurred = Signal(str, str)

    def __init__(self, parent=None):
        # Важно: инициализируем оба родительских класса
        super().__init__(parent=parent)
        self._file_path = None
        self._is_modified = False
        self._undo_stack = []  # Стек для отмены
        self._redo_stack = []  # Стек для повтора
        self._current_state = ""  # Текущее состояние

        self.template_context = {
            'file_path': None,          # Путь к элементу модели дерева (файл), он же ключ к структуре элемента в кэш
            'template_id': None,        # определение шаблона, куда вносим данные.
            'original_structure': None, # данные из кэш, полная структуда,
            'element_path': [],         # что нужно вставить в структуру
            'pending_deltas': [],  # ⬅️ ОЧЕРЕДЬ НЕСОХРАНЕННЫХ ИЗМЕНЕНИЙ
            'last_saved_structure': None  # ⬅️ СТРУКТУРА НА МОМЕНТ ПОСЛЕДНЕГО СОХРАНЕНИЯ
        }

    @abstractmethod
    def can_undo(self) -> bool:
        """Можно ли отменить действие"""
        return len(self._undo_stack) > 0
    @abstractmethod
    def can_redo(self) -> bool:
        """Можно ли повторить действие"""
        return len(self._redo_stack) > 0

    @abstractmethod
    def undo(self) -> bool:
        """Отменить последнее действие"""
        pass

    @abstractmethod
    def redo(self) -> bool:
        """Повторить отмененное действие"""
        pass

    def save_state(self):
        """Сохраняет текущее состояние для отмены"""
        current_content = self.get_content()
        if current_content != self._current_state:              # 1. Проверка изменений
            self._undo_stack.append(self._current_state)        # 2. Сохранение в историю
            self._redo_stack.clear()  # Очищаем стек повтора при новом действии
            self._current_state = current_content               # 4. Обновление текущего состояния

            # Обновляем доступность кнопок
            self.undo_available.emit(self.can_undo())
            self.redo_available.emit(self.can_redo())

    @property
    def file_path(self) -> Path | None:
        """Возвращает текущий путь к файлу. Может быть None для нового файла."""
        return self._file_path

    @file_path.setter
    def file_path(self, value: Path | None):
        self._file_path = value

    @property
    def is_modified(self) -> bool:
        """Возвращает флаг, был ли документ изменен с момента последнего сохранения."""
        return self._is_modified

    @is_modified.setter
    def is_modified(self, value: bool):
        """Устанавливает флаг модификации и испускает соответствующий сигнал."""
        if self._is_modified != value:
            self._is_modified = value
            self.modification_changed.emit(value)

    @abstractmethod
    def load(self, file_path: Path) -> bool:
        """
        Загружает содержимое файла в редактор.

        Args:
            file_path (Path): Путь к файлу для загрузки.

        Returns:
            bool: True если загрузка прошла успешно, False в противном случае.
        """
        pass

    @abstractmethod
    def save(self) -> bool:
        """
        Сохраняет содержимое редактора в текущий файл (file_path).
        Если file_path is None, должен вести себя как save_as().

        Returns:
            bool: True если сохранение прошло успешно, False в противном случае.
        """
        pass

    @abstractmethod
    def save_as(self, new_file_path: Path) -> bool:
        """
        Сохраняет содержимое редактора в новый файл и делает его текущим.

        Args:
            new_file_path (Path): Новый путь для сохранения файла.

        Returns:
            bool: True если сохранение прошло успешно, False в противном случае.
        """
        pass

    @abstractmethod
    def get_content(self) -> str:
        """
        Возвращает текущее содержимое редактора в виде строки.
        Это основной способ получить данные из редактора для сохранения.

        Returns:
            str: Текстовое содержимое редактора.
        """
        pass

    @abstractmethod
    def set_content(self, content: str):
        """
        Устанавливает содержимое редактора из строки.
        Это основной способ загрузить данные в редактор (например, из БД).

        Args:
            content (str): Содержимое для отображения.
        """
        pass

    def set_clean(self):
        """Сбрасывает флаг модификации, указывая, что текущее состояние сохранено."""
        self.is_modified = False

    def get_editor_widget(self) -> QWidget:
        """
        Возвращает виджет редактора для встраивания в UI.
        По умолчанию возвращает self, но может быть переопределен,
        если редактор является контейнером для других виджетов.

        Returns:
            QWidget: Виджет, который можно разместить в layout.
        """
        return self

    def get_available_actions(self) -> list:
        """
        Возвращает список доступных действий для редактора.
        Может быть переопределен в подклассах для предоставления специфичных действий.

        Returns:
            list: Список QAction или пустой список
        """
        return []

    def after_save_cleanup(self):
        """Очищает состояние отмены после успешного сохранения"""
        self._undo_stack.clear()
        self._redo_stack.clear()
        self._current_state = self.get_content()
        self.undo_available.emit(False)
        self.redo_available.emit(False)

    def register_change(self, operation, element_path, **data):
        """Регистрирует любое изменение в очереди дельт"""
        delta = Delta(operation, element_path, **data)
        self.template_context['pending_deltas'].append(delta)

        # Автоматически помечаем как измененный
        self.is_modified = True