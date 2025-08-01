import os
import json
from dataclasses import dataclass
from typing import List, Dict
from abc import ABC, abstractmethod

# Интерфейс для Model
class IButtonModel(ABC):
    @abstractmethod
    def get_buttons(self) -> List['ButtonModel']: ...

    @abstractmethod
    def add_button(self, name: str, path: str): ...

    @abstractmethod
    def remove_button(self, index: int): ...

    @abstractmethod
    def save_buttons(self): ...

    @abstractmethod
    def load_buttons(self): ...

@dataclass
class ButtonModel:
    '''
    Это dataclass, который представляет собой модель данных для кнопки. Он содержит два поля: 
    name (название кнопки) и path (путь к программе, которую нужно запустить).
    '''
    name: str  # Название кнопки
    path: str  # Путь к программе

class ButtonListModel(IButtonModel):
    '''
    Этот класс управляет списком кнопок. Он предоставляет методы для добавления новой кнопки (add_button), 
    получения списка всех кнопок (get_buttons) и получения конкретной кнопки по индексу (get_button).
    '''
    def __init__(self, file_path: str = "buttons.json"):
        """
        Инициализация класса ButtonListModel.

        :param file_path: Путь к файлу, в котором хранятся данные о кнопках. По умолчанию "buttons.json".
        """
        self._buttons: List[ButtonModel] = []  # Список кнопок
        self._file_path = file_path
        self.load_buttons()  # Загружаем кнопки при инициализации
    def is_button_name_unique(self, name: str) -> bool:
        """
        Проверяет, уникально ли имя кнопки в списке.

        :param name: Имя кнопки для проверки.
        :return: True, если имя уникально, иначе False.
        """
        return not any(button.name == name for button in self._buttons)
    
    def add_button(self, name: str, path: str):
        """
        Добавляет новую кнопку в список, если имя уникально.

        :param name: Имя кнопки.
        :param path: Путь к программе, которую нужно запустить.
        :raises ValueError: Если имя кнопки уже существует или данные невалидны.
        """
        # Добавление новой кнопки
        if self.is_button_name_unique(name):
            self._buttons.append(ButtonModel(name, path))

        else:
            raise ValueError("Кнопка с таким именем уже существует или данные невалидны.")

    def get_buttons(self) -> List[ButtonModel]:
        """
        Возвращает список всех кнопок.
        :return: Список объектов ButtonModel.
        """
        # Получение списка кнопок
        return self._buttons

    def get_button(self, index: int) -> ButtonModel:
        """
        Возвращает кнопку по указанному индексу.
        :param index: Индекс кнопки в списке.
        :return: Объект ButtonModel, если индекс корректен, иначе None.
        """
        # Получение кнопки по индексу
        if 0 <= index < len(self._buttons):
            return self._buttons[index]
        return None



    def remove_button(self, index: int):
        """
        Удаляет кнопку по указанному индексу.
        :param index: Индекс кнопки для удаления.
        """
        if 0 <= index < len(self._buttons):
            self._buttons.pop(index)

    def edit_button(self, index: int, name: str, path: str):
        """
        Редактирует кнопку по указанному индексу.
        :param index: Индекс кнопки для редактирования.
        :param name: Новое имя кнопки.
        :param path: Новый путь к программе.
        """
        if 0 <= index < len(self._buttons):
            self._buttons[index].name = name
            self._buttons[index].path = path        

    def is_valid_button(self, name: str, path: str) -> bool:
        """
        Проверяет, является ли кнопка валидной (имя не пустое и путь существует).

        :param name: Имя кнопки.
        :param path: Путь к программе.
        :return: True, если кнопка валидна, иначе False.
        """
        return bool(name.strip()) and os.path.exists(path)        
    
    def sort_buttons(self, key=lambda button: button.name):
        """
        Сортирует кнопки по указанному ключу.
        :param key: Функция, возвращающая ключ для сортировки. По умолчанию сортирует по имени кнопки.
        """
        self._buttons.sort(key=key)

    def save_buttons(self):
        """
        Сохраняет кнопки в файл в формате JSON.
        """
        data = [{"name": button.name, "path": button.path} for button in self._buttons]
        with open(self._file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def load_buttons(self):
        """
        Загружает кнопки из файла JSON.
        """
        if not os.path.exists(self._file_path):
            return  # Файл не существует, пропускаем загрузку

        with open(self._file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            for item in data:
                self.add_button(item["name"], item["path"])