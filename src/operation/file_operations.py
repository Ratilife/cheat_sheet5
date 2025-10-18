import os
from datetime import datetime
from pathlib import Path

from PySide6.QtWidgets import QInputDialog

from src.managers.file_manager import FileManager
from src.dialogs.dialog_manager import DialogManager
from src.global_var.config import update_root_folder, get_bookmarks,get_for_program_path
from pathlib import Path


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
            json_path = Path(__file__).parent.parent / "managers" / "root_folder_structure_basic.json" # TODO 07.10.2025 заминить на диалог, пусть пользователь указует файл
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

    #---Создание новых файлов------

    def create_new_st_file(self,name_file, tab_name: str) -> str:
        """Создает новый ST-файл и возвращает путь к нему"""
        # TODO 🚧 В разработке: 08.10.2025
        # 1. Генерация имени
        file_path = self._create_file_path("st", name_file, tab_name)
        #file_path = self.file_manager.dialog_save_st_md_files() #TODO 08.10.2025 изменить функционал
        if not file_path:  # Если пользователь отменил диалог
            return ""

        # 2. Создание шаблона
        #name_file = Path(file_path).stem
        base_template = self._get_st_base(name_file)
        # 3. Запись на диск
        file_created = self.file_manager.write_file(file_path,base_template)
        # 4. Возврат пути
        if file_created:
            return file_path
        else:
            raise Exception("Не удалось создать файл")

    def create_new_md_file_old(self, name_file, tab_name: str)-> str:
        """Создает новый MD-файл и возвращает путь к нему"""
        file_path = self._create_file_path("md", name_file, tab_name)
        if not file_path:  # Если пользователь отменил диалог
            return ""
        file_created = self.file_manager.write_file(file_path)

        if file_created:
            return file_path
        else:
            raise Exception("Не удалось создать файл")

    def create_new_md_file(self, name_file, tab_name: str) -> str:
        """Создает новый MD-файл и возвращает путь к нему"""
        # TODO 🚧 В разработке: 08.10.2025
        print(f"🔍 DEBUG create_new_md_file: старт - name_file='{name_file}', tab_name='{tab_name}'")

        try:
            # 1. Получаем путь
            file_path = self._create_file_path("md", name_file, tab_name)
            print(f"🔍 DEBUG: получен file_path='{file_path}'")

            if not file_path:
                print("❌ DEBUG: file_path пустой!")
                return ""

            # 2. Проверяем папку закладок
            bookmarks = get_bookmarks()
            print(f"🔍 DEBUG: bookmarks='{bookmarks}'")
            print(f"🔍 DEBUG: bookmarks exists={Path(bookmarks).exists() if bookmarks else 'None'}")

            # 3. Создаем папку вкладки если нужно
            file_dir = Path(file_path).parent
            print(f"🔍 DEBUG: file_dir='{file_dir}'")
            print(f"🔍 DEBUG: file_dir exists={file_dir.exists()}")

            if not file_dir.exists():
                print("🔍 DEBUG: создаем папку...")
                try:
                    file_dir.mkdir(parents=True, exist_ok=True)
                    print(f"✅ DEBUG: папка создана '{file_dir}'")
                except Exception as e:
                    print(f"❌ DEBUG: ошибка создания папки: {e}")
                    raise

            # 4. Создаем содержимое
            base_template = self._get_md_base(name_file)
            print(f"🔍 DEBUG: base_template='{base_template}'")

            # 5. Пробуем записать файл РАЗНЫМИ способами
            print("🔍 DEBUG: пробуем записать файл...")

            # Способ 1: через file_manager
            file_created = self.file_manager.write_file(file_path, base_template)
            print(f"🔍 DEBUG: file_manager.write_file вернул={file_created}")

            # Способ 2: напрямую (на случай если file_manager не работает)
            if not file_created:
                print("🔍 DEBUG: пробуем записать напрямую...")
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(base_template)
                    file_created = True
                    print("✅ DEBUG: прямой запись успешна")
                except Exception as e:
                    print(f"❌ DEBUG: ошибка прямой записи: {e}")

            # 6. Проверяем результат
            file_exists = Path(file_path).exists()
            print(f"🔍 DEBUG: файл существует после создания={file_exists}")

            if file_exists:
                print(f"✅ DEBUG: УСПЕХ! Файл создан: {file_path}")
                return file_path
            else:
                print(f"❌ DEBUG: Файл не создан! Путь: {file_path}")
                raise Exception("Не удалось создать файл")

        except Exception as e:
            print(f"❌ DEBUG: Исключение в create_new_md_file: {e}")
            import traceback
            traceback.print_exc()
            raise


    def _get_st_base(self,name_file: str) -> str:
        # Возвращает содержимое для нового ST-файла
        """Возвращает шаблон для нового ST-файла"""
        # TODO 🚧 В разработке: 08.10.2025
        return '{1,{0,{"%s"},1,0,"",""}}'% name_file

    def _get_md_base(self, name_file: str) -> str:
        return f"{name_file}\n"



    def _create_file_path(self, expansion: str, name: str, tab_name: str):
        # TODO 🚧 В разработке: 08.10.2025
        bookmarks = get_bookmarks()
        print(f"🔍 DEBUG _create_file_path: bookmarks='{bookmarks}'")

        if not bookmarks:
            print("❌ DEBUG: bookmarks is None или пустой!")
            return ""

        bookmarks_path = Path(bookmarks)
        if not bookmarks_path.exists():
            print(f"❌ DEBUG: папка bookmarks не существует: {bookmarks_path}")
            return ""

        filename = f"{name}.{expansion}"
        file_path = os.path.join(bookmarks, tab_name, filename)
        print(f"🔍 DEBUG: итоговый file_path='{file_path}'")

        return file_path

    def create_st_template(self, template_name, flag=0, avto_text="", text=""):
        """
        Создает шаблон для ST-файла

        Args:
            template_name (str): Имя шаблона
            flag (int): Флаг (0 или 1), по умолчанию 0
            avto_text (str): имя автовставки шаблона
            text (str): содержание шаблона

        Returns:
            str: Строка с шаблоном в формате ST-файла
        """
        #TODO 17.10.2025 - мертвый код create_st_template

        # Проверяем корректность флага
        if flag not in (0, 1):
            raise ValueError("Flag must be 0 or 1")

        # Экранируем кавычки в строках
        def escape_string(s):
            return f'"{s.replace('"', '""')}"'

        # Формируем шаблон согласно грамматике
        template = (
            f"{{0, {{{escape_string(template_name)}, 0, {flag}, "
            f"{escape_string(avto_text)}, {escape_string(text)}}}}}"
        )

        return template

    def create_st_folder(self, folder_name, flag=1, items=None):
        """
        Создает папку для ST-файла согласно грамматике

        Args:
            folder_name (str): Имя папки
            flag (int): Флаг (0 или 1), по умолчанию 1
            items (list): Список вложенных элементов (шаблонов или других папок)

        Returns:
            str: Строка с папкой в формате ST-файла
        """
        #TODO - 17.10.2025 - мертвый код create_st_folder

        if flag not in (0, 1):
            raise ValueError("Flag must be 0 or 1")

        # Экранируем кавычки в строках (удваиваем их)
        def escape_string(s):
            return f'"{s.replace('"', '""')}"'

        # Формируем header папки
        folder_header = f"{escape_string(folder_name)}, 1, {flag}, \"\", \"\""

        # Определяем количество элементов
        item_count = len(items) if items else 0

        # Формируем папку
        if items and item_count > 0:
            # Папка с вложенными элементами
            items_str = ", " + ", ".join(items)
            folder = f"{{{item_count}, {{{folder_header}}}{items_str}}}"
        else:
            # Пустая папка
            folder = f"{{{item_count}, {{{folder_header}}}}}"

        return folder


    def add_st_folder(self, new_folder_name: str)->dict:

        # Создаем новую папку
        new_folder = {
            'name': new_folder_name,
            'type': 'folder',
            'children': []
        }
        return new_folder

    def add_st_template(self,new_template_name: str, template_content: str = "")->dict:
        # Создаем новый шаблон
        new_template = {
            'name': new_template_name,
            'type': 'template',
            'content': template_content
        }
        return new_template


    def add_data_st_structure(self,data:tuple, new_element):
        # Количество элементов в кортеже
        name=''
        structure = None
        insert = None
        type = ''
        new_name = new_element['name']
        new_type = new_element['type']

        tuple_length = len(data)
        if tuple_length == 4:
            print(f'💊 tuple: {data}')
            print(f'⭐ {data[0]}')
            print(f'⭐ {data[1]}')
            print(f'⭐ {data[2]}')
            print(f'⭐ {data[3]}')

            name = data[0]
            structure = data[1]
            insert = data[2]
            type = data[3]

        if tuple_length == 3:
            name = data[0]
            insert = data[1]
            type = data[2]
            print(f'💊 tuple: {data}')
            print(f'⭐ {data[0]}')
            print(f'⭐ {data[1]}')
            print(f'⭐ {data[2]}')
            

        if type in ['folder', 'template']:
            if new_type == 'folder':
                new_folder = self.add_st_folder(new_name)
                insert['children'].append(new_folder)
                print(f'🟢 folder insert: {insert}')
                print(f'🍀 structure: {structure}')
            if new_type == 'template':
                new_template = self.add_st_template(new_name)
                insert['children'].append(new_template)
                print(f'🟢 template insert: {insert}')
                print(f'🍀 structure: {structure}')
            return structure

        elif type == 'file':
            print("зашел в type == 'file'")
            if new_type == 'folder':
                new_folder = self.add_st_folder(new_name)
                insert.append(new_folder)
                print(f'🟢 folder insert: {insert}')
            if new_type == 'template':
                new_template = self.add_st_template(new_name)
                insert.append(new_template)
                print(f'🟢 template insert: {insert}')

            return insert






