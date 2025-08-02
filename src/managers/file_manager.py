import json

from PySide6.QtWidgets import QFileDialog
from pathlib import Path
from typing import Dict, List, Union
class FileManager:
    @staticmethod
    def get_create_folder_path(title: str) -> str | None:
        """Открывает диалог выбора папки (с возможностью создания новой)"""
        # ✅ Реализовано: 02.08.2025
                #Задачи: Создание корневой папки
        folder_path = QFileDialog.getExistingDirectory(
            None,
            title,
            "",
            options=QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks
        )
        return folder_path if folder_path else None

    def create_root_folder_structure(config_path: Union[str, Path]) -> None:
        """
        Создает дерево папок на основе структуры, описанной в JSON-конфигурационном файле.

        Args:
            config_path: Путь к JSON-файлу конфигурации (строка или Path-объект)

        Пример конфигурационного файла:
        {
            "root_folder": "my_project",
            "subfolders": {
                "docs": ["v1", "v2"],
                "src": ["main", "test"]
            }
        }
        """

        # ✅ Реализовано: 02.08.2025
                # Задачи: Создание корневой папки

        # Создаем локальную переменную вместо переприсваивания параметра
        config_file = Path(config_path) if isinstance(config_path, str) else config_path

        # Чтение конфигурационного файла с аннотацией типа
        with config_file.open('r', encoding='utf-8') as f:
            config: Dict[str, Union[str, Dict[str, List[str]]]] = json.load(f)

        # Создание корневой папки
        root_path = Path(config['root_folder'])
        root_path.mkdir(parents=True, exist_ok=True)

        # Создание подпапок
        subfolders: Dict[str, List[str]] = config.get('subfolders', {})
        for folder, subfolders_list in subfolders.items():
            # Создание основной подпапки
            folder_path = root_path / folder
            folder_path.mkdir(exist_ok=True)

            # Создание вложенных подпапок
            for subfolder in subfolders_list:
                subfolder_path = folder_path / subfolder
                subfolder_path.mkdir(exist_ok=True)

        print(f"Структура папок '{root_path}' успешно создана!")