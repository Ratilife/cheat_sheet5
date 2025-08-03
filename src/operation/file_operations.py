from pathlib import Path
from src.managers.file_manager import FileManager

class FileOperations:
    def __init__(self,  tree_model_manager=None, file_watcher=None):
        self.file_manager = FileManager()
    def create_root_folder(self):
        """Создает корневую папку проекта на основе JSON-конфигурации.

        Метод выполняет следующие действия:
        1. Запрашивает у пользователя выбор корневой папки через диалоговое окно
        2. Создает иерархию папок согласно конфигурации из файла 'root_folder_structure_basic.json'
        3. Обрабатывает возможные ошибки в процессе выполнения

        Возвращает:
            None

        Исключения:
            FileNotFoundError: если JSON-файл конфигурации не найден
            (другие исключения обрабатываются внутри file_manager)

        Логика работы:
            - При отмене выбора папки выводит сообщение и завершает работу
            - При успешном выполнении структура создается через file_manager
            - При ошибках выводит соответствующее сообщение в консоль

        Пример использования:
             project_manager = ProjectManager()
             project_manager.create_root_folder()
            [Откроется диалог выбора папки]
            Структура папок 'my_project' успешно создана!
        """
        # ✅ Реализовано: 03.08.2025
            # task: Создание корневой папки
        path_folder = self.file_manager.get_create_folder_path("Создайте корнивую папку")
        if not path_folder:
            print("Отменено: папка не выбрана.")
            return
        try:
            # Получаем путь к JSON-файлу относительно текущего модуля
            json_path = Path(__file__).parent.parent / "managers" / "root_folder_structure_basic.json"
            root_folder_path =  self.file_manager.create_root_folder_structure(json_path,path_folder)
            return root_folder_path
        except FileNotFoundError:
            print("Ошибка: JSON-файл конфигурации не найден!")


    def save_path_root_folder(self,root_path: str, target_name: str):
         # TODO 🚧 В разработке: 03.08.2025
            # task: Работа с окном Настройка для стартовой панели
         '''
         Если should_overwrite_existing_file = True - Создаем файл json
         :param root_path: - путь к корневой папке
         :param target_name: - назване папки куда будет осуществлятся запись
         :return:  Сообщение для пользователя
         '''
         pass

