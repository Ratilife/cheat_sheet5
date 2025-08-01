from typing import List
from abc import ABC, abstractmethod,ABCMeta
from src.start_panel.models.model import IButtonModel
from PySide6.QtCore import QObject, Signal


class IButtonViewModel(ABC):
    @abstractmethod
    def get_buttons(self) -> List['ButtonModel']: ...

    @abstractmethod
    def add_button(self, name: str, path: str): ...

    @abstractmethod
    def execute_program(self, index: int): ...

# Создаем комбинированный метакласс, который объединяет QObject и ABC
class MetaQObjectABC(type(QObject), ABCMeta):
    pass

class ButtonViewModel(IButtonViewModel, QObject,  metaclass=MetaQObjectABC):
    def __init__(self, model: IButtonModel):
        QObject.__init__(self)
        self._model = model  # Ссылка на Model

    # Сигнал для уведомления View об изменении данных
    buttonsChanged = Signal()

    def add_button(self, name: str, path: str):
        # Добавление новой кнопки через Model
        self._model.add_button(name, path)
        self.buttonsChanged.emit()  # Уведомление View об изменении

    def get_buttons(self):
        # Получение списка кнопок через Model
        return self._model.get_buttons()

    def execute_program(self, index: int):
        # Запуск программы через Model
        button = self._model.get_button(index)
        if button:
            import os
            os.startfile(button.path)  # Запуск программы

    def remove_button(self, index: int):
        self._model.remove_button(index)
        self.buttonsChanged.emit()        

    def edit_button(self, index: int, name: str, path: str):
        if self._model.is_valid_button(name, path):
            self._model.edit_button(index, name, path)
            self.buttonsChanged.emit()    

    def sort_buttons(self):
        self._model.sort_buttons()
        self.buttonsChanged.emit()        

    def is_valid_button(self, name: str, path: str) -> bool:
        return self._model.is_valid_button(name, path)    
    
    def save_buttons(self):
        """
        Сохраняет кнопки через Model.
        """
        self._model.save_buttons()

