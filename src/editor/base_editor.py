from abc import ABC, abstractmethod
from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget


class BaseFileEditor(QWidget, ABC):
    """
        Абстрактный базовый класс для всех редакторов файлов.
        Наследуется от QWidget, так как каждый редактор будет виджетом для размещения в UI.
    """

    #Сигналы
    # Сигнал об изменении модифицированного состояния (is_modified)
    modification_changed = Signal(bool)
    # Сигнал о том, что файл успешно сохранен по новому пути
    file_saved_as = Signal(Path)
    # Сигнал о возникновении ошибки (сообщение, уровень)
    error_occurred = Signal(str, str)

    def __init__(self, parent=None):
        # Важно: инициализируем оба родительских класса
        super().__init__(parent)
        self._file_path = None
        self._is_modified = False

    @property
    def file_path(self) -> Path | None:
        """Возвращает текущий путь к файлу. Может быть None для нового файла."""
        return self._file_path

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

