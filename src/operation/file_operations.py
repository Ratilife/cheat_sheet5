from datetime import datetime
from pathlib import Path
from src.managers.file_manager import FileManager
from src.dialogs.dialog_manager import DialogManager
from src.global_var.config import update_root_folder

class FileOperations:
    def __init__(self,  tree_model_manager=None, file_watcher=None):
        self.file_manager = FileManager()
        self.messenger = DialogManager(console_output=False, gui_output= True)
    def create_root_folder(self):
        """Создает корневую папку проекта на основе JSON-конфигурации.

        """
        # TODO 🚧 В разработке: 03.08.2025 - нужна проверка на уже созданную папку
            # task: Создание корневой папки

        path_folder = self.file_manager.get_create_folder_path("Создайте корнивую папку")
        if not path_folder:
            self.messenger.show_warning("Отменено: папка не выбрана.")
            return
        try:
            # Получаем путь к JSON-файлу относительно текущего модуля
            json_path = Path(__file__).parent.parent / "managers" / "root_folder_structure_basic.json"

            root_folder_path = self.file_manager.create_root_folder_structure(json_path, path_folder)

            if not root_folder_path.success:
                if root_folder_path.already_exists:
                    self.messenger.show_warning("Ошибка", f"Папка уже существует: {root_folder_path.error}")
                else:
                    self.messenger.show_error("Ошибка", root_folder_path.error)
                return root_folder_path.root_path

            self.messenger.show_success(
                f"Структура папок успешно создана",
                f"Путь: {root_folder_path.root_path}"
            )
            return root_folder_path.root_path
        except FileNotFoundError as e:
            self.messenger.show_error(
                "JSON-файл конфигурации не найден",
                exception=e
            )
        except Exception as e:
            self.messenger.show_error(
                "Ошибка при создании структуры папок",
                exception=e
            )


    def save_path_root_folder(self,root_path: str, target_name: str):
         # TODO 🚧 В разработке: 03.08.2025 - нужно проверить работу и протестировать
            # task: Работа с окном Настройка для стартовой панели
         '''
         Если is_path_already_exists = True - Создаем файл json
         :param root_path: - путь к корневой папке
         :param target_name: - назване папки куда будет осуществлятся запись
         :return:  Сообщение для пользователя
         '''
         name_lile = "root_folder_path.json"
         target_folder = self.file_manager.check_path_exists(root_path,target_name)
         json_file = target_folder / name_lile
         data = {
             "path": root_path,
             "date": datetime.now().strftime("%d-%m-%Y")
         }

         if self.file_manager.is_path_already_exists(json_file):
             # Файл существует - читаем его и спрашиваем подтверждение
             existing_data = self.file_manager.load_json_file(json_file)
             message = (
                 f"Файл уже существует:\n"
                 f"Путь: {existing_data['path']}\n"
                 f"Дата: {existing_data['date']}\n\n"
                 f"Хотите перезаписать его новыми данными?"
             )
             if self.messenger.show_question("Подтверждение перезаписи", message):
                 update_root_folder(root_path)  # Обновляем глобальную переменную
                 self.file_manager.save_data_to_json(json_file, data)
                 self.messenger.show_info("Файл успешно перезаписан",timeout_ms=5000)
             else:
                 self.messenger.show_info("Операция отменена пользователем", timeout_ms=5000)
         else:
             # Файла нет - просто создаем новый
             update_root_folder(root_path)  # Обновляем глобальную переменную
             self.file_manager.save_data_to_json(json_file, data)
             self.messenger.show_info("Файл успешно создан", timeout_ms=5000)


    def get_path_root_folder(self,json_file):
        # TODO 🚧 В разработке: 04.08.2025
            # task: Работа с окном Настройка для стартовой панели
        if self.file_manager.is_path_already_exists(json_file):
            pass
