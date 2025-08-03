import json

from PySide6.QtWidgets import QFileDialog
from pathlib import Path
from typing import Dict, List, Union

class FileManager:
    @staticmethod
    def get_create_folder_path(title: str) -> str | None:
        """
           Открывает диалоговое окно выбора папки с возможностью создания новой директории.

           Параметры:
               title (str): Заголовок диалогового окна

           Возвращает:
               str | None: Абсолютный путь к выбранной папке или None, если выбор отменен

           Особенности:
               - Показывает только директории (файлы скрыты)
               - Не разрешает символьные ссылки (DontResolveSymlinks)
               - Позволяет пользователю создать новую папку через стандартный интерфейс ОС
               - Поддерживает нативные диалоги для Windows/macOS/Linux

           Пример использования:
                path = get_create_folder_path("Выберите папку для проекта")
                if path:
               ...     print(f"Выбрана папка: {path}")
           """
        # ✅ Реализовано: 02.08.2025
                #Задачи: Создание корневой папки
        folder_path = QFileDialog.getExistingDirectory(
            None,
            title,
            "",
            options=QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks
        )
        return folder_path if folder_path else None

    def create_root_folder_structure(self, config_path: Union[str, Path],folder_path: Union[str, Path, None] = None) -> None:
        """
            Создает иерархическую структуру папок на основе конфигурации из JSON-файла
            в указанной или текущей директории.

            Параметры:
                config_path (Union[str, Path]): Путь к JSON-файлу конфигурации структуры папок.
                    Должен содержать:
                    - root_folder: название корневой папки (строка)
                    - subfolders: словарь с вложенными папками (опционально)

                folder_path (Union[str, Path, None]): Базовый путь для создания структуры.
                    Если None (по умолчанию), используется текущая рабочая директория.

            Возвращает:
                None

            Особенности:
                - Автоматически создает все необходимые родительские директории
                - Безопасно обрабатывает уже существующие папки (без ошибок)
                - Поддерживает относительные и абсолютные пути
                - Кроссплатформенная работа с путями (Path)
                - Выводит информационное сообщение о результате

            Исключения:
                FileNotFoundError: если конфигурационный файл не найден
                json.JSONDecodeError: при ошибке формата JSON
                PermissionError: если нет прав на создание папок
                KeyError: если в конфиге отсутствует обязательное поле 'root_folder'

            Пример конфигурационного файла:
                {
                    "root_folder": "my_project",
                    "subfolders": {
                        "docs": ["v1", "v2"],
                        "src": ["main", "test"]
                    }
                }

            Примеры использования:
                 # Создать в текущей директории
                 create_root_folder_structure("config.json")

                 # Создать в указанной папке
                 create_root_folder_structure("config.json", "/path/to/target")
            """

        # ✅ Реализовано: 03.08.2025
                # Задачи: Создание корневой папки

        # Обработка базового пути
        base_path = Path(folder_path) if folder_path is not None else Path.cwd()

        # Чтение конфигурации
        config_file = Path(config_path) if isinstance(config_path, str) else config_path
        with config_file.open('r', encoding='utf-8') as f:
            config: Dict[str, Union[str, Dict[str, List[str]]]] = json.load(f)

        # Создание корневой папки (относительно base_path)
        root_path = base_path / config['root_folder']
        root_path.mkdir(parents=True, exist_ok=True)

        # Создание подпапок
        subfolders: Dict[str, List[str]] = config.get('subfolders', {})
        for folder, subfolders_list in subfolders.items():
            folder_full_path = root_path / folder
            folder_full_path.mkdir(exist_ok=True)

            for subfolder in subfolders_list:
                subfolder_full_path = folder_full_path / subfolder
                subfolder_full_path.mkdir(exist_ok=True)

        print(f"Структура папок '{root_path}' успешно создана в '{base_path}'!")
