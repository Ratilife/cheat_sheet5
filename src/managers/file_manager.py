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
                #task: Создание корневой папки
        folder_path = QFileDialog.getExistingDirectory(
            None,
            title,
            "",
            options=QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks
        )
        return folder_path if folder_path else None

    def create_root_folder_structure(self, config_path: Union[str, Path],folder_path: Union[str, Path, None] = None) -> str:
        """Создает иерархическую структуру папок на основе JSON-конфигурации и возвращает абсолютный путь к корневой папке.

            Параметры:
                config_path (Union[str, Path]): Путь к JSON-файлу конфигурации. Должен содержать:
                    - root_folder: название корневой папки (строка)
                    - subfolders: словарь с вложенными папками (опционально)

                folder_path (Union[str, Path, None]): Базовый путь для создания структуры.
                    Если None (по умолчанию), используется текущая рабочая директория.

            Возвращает:
                str: Абсолютный путь к созданной корневой папке в формате строки

            Исключения:
                FileNotFoundError: если конфигурационный файл не найден
                json.JSONDecodeError: при ошибке формата JSON
                PermissionError: если нет прав на создание папок
                KeyError: если в конфиге отсутствует обязательное поле 'root_folder'

            Особенности:
                - Автоматически создает все необходимые родительские директории
                - Безопасно обрабатывает уже существующие папки (без ошибок)
                - Поддерживает относительные и абсолютные пути
                - Возвращает нормализованный абсолютный путь (разрешает симлинки и '..')
                - Выводит информационное сообщение о результате

            Пример конфигурационного файла:
                {
                    "root_folder": "my_project",
                    "subfolders": {
                        "docs": ["v1", "v2"],
                        "src": ["main", "test"]
                    }
                }

            Пример использования:
                 path = create_root_folder_structure("config.json")
                 print(f"Создана структура в: {path}")
                Создана структура в: /absolute/path/to/my_project
            """

        # ✅ Реализовано: 03.08.2025
                # task: Создание корневой папки

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
        return str(root_path.resolve())  # Возвращаем абсолютный путь к корневой папке

    def check_path_exists(self, root_path: str, target_name: str) -> Path:
        """
        Проверяет существование папки или файла по указанному пути.

        Параметры:
            root_path (str): Базовый путь для проверки
            target_name (str): Имя папки/файла для проверки (например, "for_program")

        Возвращает:
            Path: Полный путь к проверяемому объекту

        Исключения:
            FileNotFoundError: Если указанный root_path не существует
            RuntimeError: Если target_name существует, но это файл (а не папка)
        """
        # ✅ Реализовано: 03.08.2025
            # task: Работа с окном Настройка для стартовой панели
        base_path = Path(root_path)
        if not base_path.exists():
            raise FileNotFoundError(f"Указанный путь не существует: {root_path}")

        target_path = base_path / target_name

        if target_path.exists():
            if target_path.is_file():
                raise RuntimeError(f"Объект '{target_name}' существует, но это файл (ожидалась папка)")
            return target_path

        return target_path

    def should_overwrite_existing_file(self, json_file: Path) -> bool:
        """Проверяет нужно ли перезаписывать существующий файл."""
        if not json_file.exists():
            return True
        else:
            return False

    def _load_json_file(self, file_path: Path) -> dict:
        """
        Загружает данные из JSON-файла с обработкой ошибок.
        Args:
            file_path: Путь к JSON-файлу
        Returns:
            Словарь с данными из файла
        Raises:
            RuntimeError: Если файл не существует, недоступен для чтения
                        или содержит невалидный JSON
        """
        # TODO 🚧 В разработке: 03.08.2025 - проверить нужен  метод _load_json_file в дальнейшем
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            raise RuntimeError(f"Файл не найден: {file_path}")
        except PermissionError:
            raise RuntimeError(f"Нет прав на чтение файла: {file_path}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Ошибка парсинга JSON в файле {file_path}: {str(e)}")

    def save_data_to_json(self, json_file: Path, data: dict) -> None:
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)