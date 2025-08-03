import datetime
from pathlib import Path
from src.managers.file_manager import FileManager
from src.dialogs.dialog_manager import DialogManager, MessageType

class FileOperations:
    def __init__(self,  tree_model_manager=None, file_watcher=None):
        self.file_manager = FileManager()
        self.messenger = DialogManager(console_output=True, gui_output=False)
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
            self.messenger.show_warning("Отменено: папка не выбрана.")
            return
        try:
            # Получаем путь к JSON-файлу относительно текущего модуля
            json_path = Path(__file__).parent.parent / "managers" / "root_folder_structure_basic.json"
            root_folder_path =  self.file_manager.create_root_folder_structure(json_path,path_folder)
            self.messenger.show_success(
                f"Структура папок успешно создана",
                f"Путь: {root_folder_path}"
            )
            return root_folder_path
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
         Если should_overwrite_existing_file = True - Создаем файл json
         :param root_path: - путь к корневой папке
         :param target_name: - назване папки куда будет осуществлятся запись
         :return:  Сообщение для пользователя
         '''
         name_lile = "root_folder_path.json"
         target_folder = self.file_manager.check_path_exists(root_path,target_name)
         json_file = target_folder / name_lile
         data = {
             "path": root_path,
             "date": datetime.now().strftime("%Y-%m-%d")
         }

         if self.file_manager.should_overwrite_existing_file(json_file):
             # Файл существует - читаем его и спрашиваем подтверждение
             existing_data = self.file_manager.load_json_file(json_file)
             message = (
                 f"Файл уже существует:\n"
                 f"Путь: {existing_data['path']}\n"
                 f"Дата: {existing_data['date']}\n\n"
                 f"Хотите перезаписать его новыми данными?"
             )
             if self.messenger.show_question("Подтверждение перезаписи", message):
                 self.file_manager.save_data_to_json(json_file, data)
                 self.messenger.show_info("Файл успешно перезаписан",timeout_ms=5000)
             else:
                 self.messenger.show_info("Операция отменена пользователем", timeout_ms=5000)
         else:
             # Файла нет - просто создаем новый
             self.file_manager.save_data_to_json(json_file, data)
             self.messenger.show_info("Файл успешно создан", timeout_ms=5000)



