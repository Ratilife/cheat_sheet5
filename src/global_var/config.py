"""
Модуль для управления конфигурацией программы и путями к ресурсам.

Attributes:
    CONFIG_FILE (Path): Путь к файлу конфигурации в домашней директории пользователя (root_folder_path.json)
    ROOT_FOLDER_DATA (Dict): Словарь для хранения пути к корневой папке и даты последнего обновления
    FOR_PROGRAM_PATH (Optional[str]): Динамически вычисляемый путь к папке for_program
    BOOKMARKS_PATH (Optional[str]): Динамически вычисляемый путь к папке bookmarks

Functions:
    load_config(): Инициализирует конфигурацию при старте программы
    update_root_folder(path): Обновляет данные о корневой папке
    get_root_folder(): Возвращает копию данных о корневой папке
    set_for_program_path(): Вычисляет путь к папке for_program
    get_for_program_path(): Возвращает сохраненный путь к папке for_program
    set_bookmarks(): Вычисляет путь к папке bookmarks
    get_bookmarks(): Возвращает сохраненный путь к папке bookmarks

Note:
    - Автоматически загружает конфигурацию при импорте модуля
    - Пути FOR_PROGRAM_PATH и BOOKMARKS_PATH вычисляются относительно корневой папки
    - Все изменения корневой папки автоматически сохраняются в JSON-файл
    - Использует глобальные переменные для хранения текущих настроек
    - Файл конфигурации хранится в домашней директории пользователя
"""
# config.py

# ✅ Реализовано: 01.09.2025
            # 🏆task: Работа с окном Настройка для стартовой панели;
            # 🏆task: Создать переменную которая знает где находится папка for_program из корневой папки;

from datetime import datetime
from typing import Dict, Optional
import json
from pathlib import Path
import os


# Путь к файлу конфигурации (в папке пользователя или рядом с программой)
CONFIG_FILE = Path.home() / "root_folder_path.json"

# Глобальная переменная для хранения данных о корневой папке
ROOT_FOLDER_DATA: Dict[str, Optional[str]] = {
    "path": None,    # Путь к корневой папке
    "date": None     # Дата последнего обновления
}
FOR_PROGRAM_PATH:  Optional[str] = None
BOOKMARKS_PATH:  Optional[str] = None
def set_for_program_path():
    """ Устанавливает глобальный путь для директории 'for_program'.

        Эта функция определяет корневую директорию приложения с помощью
        `get_root_folder()` и затем конструирует полный путь к поддиректории
        'for_program'. Полученный путь сохраняется в глобальной переменной
        `FOR_PROGRAM_PATH`. Это обеспечивает, что у приложения есть
        последовательная и легко доступная ссылка на эту конкретную папку для
        хранения файлов, связанных с программой.

        Raises:
            (Не явные исключения, зависит от поведения get_root_folder)
    """
    global FOR_PROGRAM_PATH
    root_folder_path = get_root_folder()
    for_program_path = os.path.join(root_folder_path['path'], "for_program")
    FOR_PROGRAM_PATH = for_program_path

def get_for_program_path():
    return  FOR_PROGRAM_PATH

def set_bookmarks():
    """ Устанавливает глобальный путь для директории 'bookmarks'.

        Эта функция определяет корневую директорию приложения с помощью
        `get_root_folder()` и затем конструирует полный путь к поддиректории
        'bookmarks'. Полученный путь сохраняется в глобальной переменной
        `BOOKMARKS_PATH`. Это обеспечивает, что у приложения есть
        последовательная и легко доступная ссылка на эту конкретную папку для
        хранения файлов закладок.

        Raises:
            (Не явные исключения, зависит от поведения get_root_folder)
    """
    global BOOKMARKS_PATH
    root_folder_path = get_root_folder()
    bookmarks_path = os.path.join(root_folder_path['path'], "bookmarks")
    BOOKMARKS_PATH = bookmarks_path

def get_bookmarks():
    return BOOKMARKS_PATH
def load_config() -> None:
    """Загружает данные конфигурации из файла при запуске приложения.

        Функция проверяет существование файла конфигурации (`CONFIG_FILE`).
        Если файл найден, она пытается загрузить его содержимое в формате JSON
        и обновить глобальную переменную `ROOT_FOLDER_DATA` полученными данными.
        При возникновении ошибок (например, некорректный JSON или проблемы
        с доступом к файлу) будет выведено сообщение об ошибке.

        После загрузки конфигурации функция вызывает `set_for_program_path()` и
        `set_bookmarks()` для инициализации путей к соответствующим директориям,
        используя данные, полученные из конфига.

        Raises:
            (Неявные исключения, обрабатываются внутри функции)
    """
    global ROOT_FOLDER_DATA
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                ROOT_FOLDER_DATA.update(json.load(f))
        except Exception as e:
            print(f"Ошибка загрузки конфига: {e}")
    set_for_program_path()
    set_bookmarks()

def _save_config() -> None:
    """Сохраняет текущие данные конфигурации в файл.

        Эта функция сериализует содержимое глобальной переменной
        `ROOT_FOLDER_DATA` в формат JSON и записывает его в файл,
        указанный `CONFIG_FILE`. Файл будет перезаписан, если он уже
        существует. Для удобства чтения человеком данные сохраняются с
        отступами (indent=4).

        При возникновении любых ошибок ввода-вывода или сериализации
        (например, нет прав на запись), будет выведено соответствующее
        сообщение об ошибке.

        Returns:
            None
        """
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