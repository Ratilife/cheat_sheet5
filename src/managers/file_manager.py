"""
FileManager - модуль для управления файлами и папками.

Класс FileManager предоставляет методы для работы с файловой системой:
- ✅ get_create_folder_path() - диалог выбора папки с созданием новой
- ✅ save_path_for_program() - сохранение путей файлов в JSON
- ✅ create_root_folder_structure() - создание иерархии папок из JSON-конфига
- ❌check_path_exists() - проверка существования пути  мертвый код
- ✅ is_path_already_exists() - проверка существования файла/папки
- ✅ load_json_file() - загрузка данных из JSON-файла
- ✅ save_data_to_json() - сохранение данных в JSON-файл
- ✅ create_files_dict_with_paths() - создание словаря файлов .md и .st
- ✅ dialog_st_md_files() - диалог выбора ST/MD файлов

Вспомогательный класс FolderCreationResult хранит результат создания папки.
"""
import json
import os
from dataclasses import dataclass
from PySide6.QtWidgets import QFileDialog
from pathlib import Path
from typing import Dict, List, Union
from src.global_var.config import get_for_program_path

@dataclass
class FolderCreationResult:
    success: bool
    root_path: str | None  # Путь к созданной папке (если успех)
    error: str | None      # Сообщение об ошибке (если failure)
    already_exists: bool   # Флаг "папка уже существует"

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
                #🏆task: Создание корневой папки;
        folder_path = QFileDialog.getExistingDirectory(
            None,
            title,
            "",
            options=QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks
        )
        return folder_path if folder_path else None

    def save_path_for_program(self, tab_name: str,path_files: list) -> None:
        """
        Сохраняет путь к файлу в папке for_program.
        Добавляет данные к существующему файлу, если он уже есть.
        """
        # ✅ Реализовано: 01.09.2025
        json_path = Path(os.path.join(get_for_program_path(), "saved_files.json"))

        # 1. Загружаем существующие данные
        try:
            existing_data = self.load_json_file(json_path)
        except RuntimeError:
            existing_data = []  # Инициализируем пустой список, если загрузка не удалась, чтобы избежать сбоя

        # 2. Формируем новые данные из path_files
        new_data = []
        for path_file in path_files:
            extension_file = Path(path_file).suffix
            file_type = 'unknown'  # Используем file_type, чтобы не путать с встроенным type()
            if extension_file.lower() == '.st':
                file_type = 'file'
            elif extension_file.lower() == '.md':
                file_type = 'markdown'

            new_data.append({
                "path": path_file,
                "type": file_type,
                "tab_name": tab_name
            })

        # 3. Объединяем существующие данные с новыми
        if existing_data:
            # Предполагаем, что данные — это список.
            # Если данные в JSON могут быть другого типа, нужна дополнительная проверка.
            merged_data = list(existing_data)
            merged_data.extend(new_data)
        else:
            merged_data = new_data

        # 4. Сохраняем объединённые данные обратно в файл
        self.save_data_to_json(json_file=json_path, data=merged_data)


    def create_root_folder_structure(self, config_path: Union[str, Path],
                                     folder_path: Union[str, Path, None] = None) -> FolderCreationResult:
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

        #TODO 🚧 В разработке: 03.08.2025 -
                # 🏆task: Создание корневой папки;

        # Обработка базового пути
        base_path = Path(folder_path) if folder_path is not None else Path.cwd()

        # Чтение конфигурации
        config_file = Path(config_path) if isinstance(config_path, str) else config_path
        with config_file.open('r', encoding='utf-8') as f:
            config: Dict[str, Union[str, Dict[str, List[str]]]] = json.load(f)

        # Создание корневой папки (относительно base_path)
        root_folder_name = config['root_folder']
        root_path = base_path / root_folder_name

        if self.is_path_already_exists(Path(root_path)):
            return FolderCreationResult(
                success=False,
                root_path= str(root_path),
                error=f"Папка '{root_folder_name}' уже существует",
                already_exists=True
            )

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
        return FolderCreationResult(
                success=True,
                root_path=str(root_path.resolve()),
                error=None,
                already_exists=False
            )

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
        # TODO 04.08.2025 - метод check_path_exists мертвый код, так как метод save_path_root_folder из модуля file_operation тоже  мертвый код, повторяет функционал метода is_path_already_exists

            # 🏆task: Работа с окном Настройка для стартовой панели;
        base_path = Path(root_path)
        if not base_path.exists():
            raise FileNotFoundError(f"Указанный путь не существует: {root_path}")

        target_path = base_path / target_name

        if target_path.exists():
            if target_path.is_file():
                raise RuntimeError(f"Объект '{target_name}' существует, но это файл (ожидалась папка)")
            return target_path

        return target_path


    def is_path_already_exists(self, path: Path) -> bool:
        """Проверяет, существует ли указанный путь (файл или папка) в файловой системе.
        Args:
            path: Путь к файлу или папке для проверки
        Returns:
            bool: True если путь существует (независимо файл это или папка), False если не существует
        Пример использования:
            if project_manager.is_path_already_exists(Path("my_folder")):
                print("Объект уже существует")
        """
        # TODO 🚧 В разработке: 04.08.2025 - нужно проверить работу и протестировать
            # 🏆task: Работа с окном Настройка для стартовой панели;
            # 🏆task: Создание корневой папки;
        return path.exists()

    def load_json_file(self, file_path: Path) -> dict:
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
        # TODO 🚧 В разработке: 03.08.2025 - нужно проверить работу и протестировать
            # 🏆task: Работа с окном Настройка для стартовой панели;
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            raise RuntimeError(f"Файл не найден: {file_path}")
        except PermissionError:
            raise RuntimeError(f"Нет прав на чтение файла: {file_path}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Ошибка парсинга JSON в файле {file_path}: {str(e)}")

    def save_data_to_json(self, json_file: Path, data: any) -> None:
        """Сохраняет любые данные, совместимые с JSON, в файл."""
        # ✅ Реализовано: 01.09.2025

        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def create_files_dict_with_paths(self, bookmarks_path: Path) -> dict:
        """
        Создает словарь со всеми папками (включая пустые) и путями к файлам .md и .st,
        исключая корневую папку и файлы в ней.

        Args:
            bookmarks_path (Path): Путь к корневой директории для поиска.

        Returns:
            dict: Словарь, где:
                  - ключи: имена поддиректорий (не включая корневую)
                  - значения: списки полных путей к файлам .md или .st в этих поддиректориях
        """
        # ✅ Реализовано: 13.08.2025
        dict_dir_files = {}

        # Проходим по всем поддиректориям, начиная с первого уровня вложенности
        for root, dirs, files in os.walk(bookmarks_path):
            # Пропускаем корневую директорию
            if Path(root) == bookmarks_path:
                continue

            dir_name = os.path.basename(root)
            if dir_name not in dict_dir_files:
                dict_dir_files[dir_name] = []  # Инициализируем пустым списком

            # Добавляем только файлы .md и .st
            for file in files:
                if file.endswith((".md", ".st")):
                    file_path = os.path.join(root, file)
                    dict_dir_files[dir_name].append(file_path)

        return dict_dir_files


    def dialog_st_md_files(self):
        """Загрузка ST-файлов, MD-файлов через диалог"""
        # ✅ Реализовано: 31.08.2025
        files, _ = QFileDialog.getOpenFileNames(None,
                "Открыть файлы", "", "ST Files (*.st);;Markdown Files (*.md)")
        return files

    def dialog_save_st_md_files(self):
        """Диалог создания ST-файлов и MD-файлов"""
        # ✅ Реализовано: 08.10.2025
        # TODO 08.10.2025 -  мертвый код dialog_save_st_md_files
        file_path, _ = QFileDialog.getSaveFileName(
            None,
            "Создать файл",
            "",  # Начальная директория (пустая = текущая)
            "ST Files (*.st);;Markdown Files (*.md)"
        )
        return file_path



    def write_file(self, path: str, content: str = "") -> bool:
        """Записывает содержимое в файл по указанному пути.

            Автоматически создает все необходимые родительские каталоги,
            если они не существуют. Использует кодировку 'utf-8-sig' для
            записи текста. В случае успеха возвращает True, иначе False.

            Args:
                 path (str): Полный путь к файлу, в который нужно записать содержимое.
                 content (str, optional): Строка с содержимым для записи. По умолчанию "".

            Returns:
                 bool: True, если файл был успешно записан, иначе False.
        """
        print(f"🔍 DEBUG write_file: path='{path}', content='{content}'")

        if not path:
            print("❌ DEBUG write_file: path пустой!")
            return False

        try:
            file_path = Path(path)
            print(f"🔍 DEBUG write_file: file_path='{file_path}'")
            print(f"🔍 DEBUG write_file: parent='{file_path.parent}'")
            print(f"🔍 DEBUG write_file: parent exists={file_path.parent.exists()}")

            # Создаем папки
            file_path.parent.mkdir(parents=True, exist_ok=True)
            print(f"✅ DEBUG write_file: папки созданы/проверены")

            # Записываем файл
            with open(file_path, 'w', encoding='utf-8-sig') as f:
                f.write(content if content else "")
            print(f"✅ DEBUG write_file: файл записан успешно")

            # Проверяем что файл действительно создан
            result = file_path.exists()
            print(f"🔍 DEBUG write_file: файл существует после записи={result}")

            return result

        except Exception as e:
            print(f"❌ DEBUG write_file: ошибка: {e}")
            import traceback
            traceback.print_exc()
            return False