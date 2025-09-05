# Фабрика редакторов

from pathlib import Path
from typing import Type, Dict, Optional, List
from PySide6.QtWidgets import QWidget

from src.editors.base_editor import BaseFileEditor
# Предполагается, что конкретные редакторы будут реализованы в этих модулях
from src.editor.markdown_editor import MarkdownEditor
from src.editor.st_editor import STEditor
from src.editor.plain_text_editor import PlainTextEditor


class EditorFactory:
    """
    Фабрика для создания редакторов файлов на основе расширения.
    Класс предоставляет статические методы для создания экземпляров редакторов,
    соответствующих различным типам файлов. Реализует паттерн "Фабричный метод".
    Attributes:
        _registry (Dict[str, Type[BaseFileEditor]]): Реестр сопоставления
            расширений файлов классам редакторов.
    """

    # Реестр сопоставления расширений файлов классам редакторов
    _registry: Dict[str, Type[BaseFileEditor]] = {
        '.md': MarkdownEditor,          # Редактор для Markdown-файлов
        '.st': STEditor,                # Редактор для Structured Text файлов
        '.txt': PlainTextEditor,        # Редактор для простого текста
        # Можно добавлять другие расширения по мере реализации редакторов
    }

    @staticmethod
    def create_editor(extension: str, parent: Optional[QWidget] = None) -> BaseFileEditor:
        """
        Создает и возвращает редактор для указанного расширения файла.
        Args:
            extension (str): Расширение файла (с точкой, например: '.md', '.st').
            parent (Optional[QWidget]): Родительский виджет для редактора.
        Returns:
            BaseFileEditor: Экземпляр редактора, соответствующий расширению.
        Raises:
            ValueError: Если расширение не поддерживается и нет редактора по умолчанию.
        """
        # Приводим расширение к нижнему регистру для регистронезависимого сравнения
        ext = extension.lower()

        # Ищем соответствующий класс редактора в реестре
        editor_class = EditorFactory._registry.get(ext)

        if editor_class:
            # Если нашли подходящий редактор, создаем его экземпляр
            return editor_class(parent=parent)
        else:
            # Если расширение не найдено в реестре, используем редактор для простого текста
            # Можно также выбросить исключение: raise ValueError(f"Unsupported extension: {extension}")
            return PlainTextEditor(parent=parent)

    @staticmethod
    def get_supported_extensions() -> List[str]:
        """
        Возвращает список всех поддерживаемых расширений файлов.
        Returns:
            List[str]: Список расширений, для которых есть зарегистрированные редакторы.
        """
        # Возвращаем ключи из реестра в виде списка
        return list(EditorFactory._registry.keys())

    @staticmethod
    def get_editor_description(extension: str) -> str:
        """
        Возвращает описание редактора для указанного расширения.
        Args:
            extension (str): Расширение файла.
        Returns:
            str: Человекочитаемое описание типа редактора.
        """
        # Приводим расширение к нижнему регистру
        ext = extension.lower()

        # Словарь с описаниями для различных расширений
        descriptions = {
            '.md': 'Markdown-документ',
            '.st': 'Structured Text файл',
            '.txt': 'Текстовый файл',
        }

        # Возвращаем описание или сообщение по умолчанию
        return descriptions.get(ext, f'Файл {ext} (редактор по умолчанию)')

    @staticmethod
    def register_editor(extension: str, editor_class: Type[BaseFileEditor]) -> None:
        """
        Регистрирует новый редактор для указанного расширения.
        Args:
            extension (str): Расширение файла (с точкой).
            editor_class (Type[BaseFileEditor]): Класс редактора.
        Raises:
            ValueError: Если editor_class не является подклассом BaseFileEditor.
        """
        # Проверяем, что переданный класс является подклассом BaseFileEditor
        if not issubclass(editor_class, BaseFileEditor):
            raise ValueError("Editor class must be a subclass of BaseFileEditor")

        # Регистрируем редактор для указанного расширения
        EditorFactory._registry[extension.lower()] = editor_class

        # Логируем регистрацию (в реальном проекте здесь может быть logging.debug)
        print(f"DEBUG: Зарегистрирован редактор {editor_class.__name__} для расширения {extension}")

    @staticmethod
    def unregister_editor(extension: str) -> None:
        """
        Удаляет регистрацию редактора для указанного расширения.
        Args:
            extension (str): Расширение файла.
        Returns:
            bool: True если регистрация была удалена, False если расширение не было найдено.
        """
        ext = extension.lower()
        if ext in EditorFactory._registry:
            # Удаляем расширение из реестра
            del EditorFactory._registry[ext]
            return True
        return False