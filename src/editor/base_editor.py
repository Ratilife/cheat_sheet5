from abc import ABC, abstractmethod


class BaseFileEditor(ABC):
    """Абстрактный базовый класс для всех редакторов"""

    @abstractmethod
    def set_content(self, content: str):
        """Установка содержимого редактора"""
        pass

    @abstractmethod
    def get_content(self) -> str:
        """Получение содержимого редактора"""
        pass

    @abstractmethod
    def is_modified(self) -> bool:
        """Проверка наличия несохраненных изменений"""
        pass

    @abstractmethod
    def save_state(self):
        """Сохранение файла"""
        pass

    @abstractmethod
    def get_supported_extensions(self) -> list:
        """Получение поддерживаемых расширений"""
        pass

    @abstractmethod
    def restore_state(self):
        # восстановление_состояния
        pass