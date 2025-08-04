# config.py
from datetime import datetime
from typing import Dict, Optional
import json
from pathlib import Path
from typing import Dict, Optional

# Путь к файлу конфигурации (в папке пользователя или рядом с программой)
CONFIG_FILE = Path.home() / "root_folder_path.json"

# Глобальная переменная для хранения данных о корневой папке
ROOT_FOLDER_DATA: Dict[str, Optional[str]] = {
    "path": None,    # Путь к корневой папке
    "date": None     # Дата последнего обновления
}

def load_config() -> None:
    """Загружает данные из файла при старте программы"""
    global ROOT_FOLDER_DATA
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                ROOT_FOLDER_DATA.update(json.load(f))
        except Exception as e:
            print(f"Ошибка загрузки конфига: {e}")

def _save_config() -> None:
    """Сохраняет данные в файл"""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(ROOT_FOLDER_DATA, f, indent=4)
    except Exception as e:
        print(f"Ошибка сохранения конфига: {e}")

def update_root_folder(path: str) -> None:
    """Обновляет глобальные данные о корневой папке"""
    global ROOT_FOLDER_DATA
    ROOT_FOLDER_DATA["path"] = path
    ROOT_FOLDER_DATA["date"] = datetime.now().strftime("%d-%m-%Y")
    _save_config()  # Автосохранение при изменении

def get_root_folder() -> Dict[str, Optional[str]]:
    """Возвращает текущие данные о корневой папке"""
    return ROOT_FOLDER_DATA.copy()  # Возвращаем копию, чтобы избежать изменений извне

# Загружаем конфиг при импорте модуля
load_config()