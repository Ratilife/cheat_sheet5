from datetime import datetime
from pathlib import Path
from src.managers.file_manager import FileManager
from src.dialogs.dialog_manager import DialogManager
from src.global_var.config import update_root_folder, get_bookmarks,get_for_program_path
from src.managers.tree_model_manager import TreeModelManager


class FileOperations:
    def __init__(self,file_watcher=None):
        self.file_manager = FileManager()
        self.messenger = DialogManager(console_output=False, gui_output= True)

    def create_root_folder(self):
        """Создает корневую папку проекта на основе JSON-конфигурации.

        """
        # TODO 🚧 В разработке: 03.08.2025 - нужна проверка на уже созданную папку
            # 🏆task: Создание корневой папки;

        path_folder = self.file_manager.get_create_folder_path("Создайте корнивую папку")
        if not path_folder:
            self.messenger.show_warning("Отменено: папка не выбрана.")
            return
        try:
            # Получаем путь к JSON-файлу относительно текущего модуля
            json_path = Path(__file__).parent.parent / "managers" / "root_folder_structure_basic.json"
            #json_path = Path(os.path.join(get_for_program_path(),"root_folder_structure_basic.json"))
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
         # TODO 🚧 В разработке: 03.08.2025 - метод уже не актуален (мертвый код) Нужен пока как пример
            # 🏆task: Работа с окном Настройка для стартовой панели;
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
        # TODO 🚧 В разработке: 04.08.2025 - мертвый код get_path_root_folder
            # 🏆task: Работа с окном Настройка для стартовой панели;
        if self.file_manager.is_path_already_exists(json_file):
            pass

    def fetch_file_heararchy(self):
        """Получает иерархию файлов из папки закладок в виде словаря.

        Метод выполняет следующие действия:
        1. Получает путь к папке закладок через get_bookmarks()
        2. Проверяет существование указанного пути
        3. Создает словарь с иерархией файлов если путь существует

        Returns:
            dict: Словарь с иерархией файлов и директорий, где ключи - пути к файлам,
                  значения - соответствующая информация о файлах. Возвращает пустой
                  словарь если закладки не найдены или путь не существует.

        Notes:
            - Использует file_manager для проверки путей и создания структуры файлов
            - Возвращает None если bookmarks не определены

        Example:
            >>> result = fetch_file_heararchy()
            >>> print(result)
            {'/path/to/file1.md': FileInfo(...), '/path/to/file2.md': FileInfo(...)}
        """
        # ✅ Реализовано: 12.08.2025
        dict_dir_files = None
        bookmarks = get_bookmarks()
        if not bookmarks:
            return {}

        if self.file_manager.is_path_already_exists(Path(bookmarks)):
            dict_dir_files = self.file_manager.create_files_dict_with_paths(Path(bookmarks))

        return dict_dir_files

    def load_st_md_files(self, target_tab_name: str)->list:

        """Обработчик кнопки загрузки файлов"""
        # ✅ Реализовано: 01.09.2025
        files = self.file_manager.dialog_st_md_files()
        if files and target_tab_name:
            self.file_manager.save_path_for_program(target_tab_name,files)
            return files
        elif not target_tab_name:
            print("DEBUG: Не выбрана целевая вкладка")

    def extend_dict_with_file(self,file_name: str,tab_names:dict)->dict:
        # ✅ Реализовано: 02.09.2025

        path_folder_for_program = get_for_program_path()
        path_file = Path(path_folder_for_program) / file_name

        if self.file_manager.is_path_already_exists(path_file):
            data_file = self.file_manager.load_json_file(path_file)

            for item in data_file:
                tab_name = item['tab_name']
                path_item = item['path']
                if tab_name in tab_names:
                    tab_names[tab_name].append(path_item)
                else:
                    tab_names[tab_name] = [path_item]

        return tab_names