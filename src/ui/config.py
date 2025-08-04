# config.py
from datetime import datetime
from typing import Dict, Optional

# Глобальная переменная для хранения данных о корневой папке
ROOT_FOLDER_DATA: Dict[str, Optional[str]] = {
    "path": None,    # Путь к корневой папке
    "date": None     # Дата последнего обновления
}

def update_root_folder(path: str) -> None:
    """Обновляет глобальные данные о корневой папке"""
    global ROOT_FOLDER_DATA
    ROOT_FOLDER_DATA["path"] = path
    ROOT_FOLDER_DATA["date"] = datetime.now().strftime("%d-%m-%Y")

def get_root_folder() -> Dict[str, Optional[str]]:
    """Возвращает текущие данные о корневой папке"""
    return ROOT_FOLDER_DATA.copy()  # Возвращаем копию, чтобы избежать изменений извне