from src.parsers.file_parser_service import FileParserService
from src.operation.file_operations import FileOperations
def find_parent_in_structure():
    updated_structure = {'structure': [{'name': 'Текст', 'type': 'template', 'content': '\t\tСообщение = Новый СообщениеПользователю;\r\n\t\tСообщение.Текст = """";\r\n\t\tСообщение.Поле = """";\r\n\t\tСообщение.УстановитьДанные();\r\n\t\tСообщение.Сообщить();\t\t'}, {'name': 'Папка', 'type': 'folder', 'children': [{'name': 'Текст2', 'type': 'template', 'content': 'Привет'}, {'name': 'текст3', 'type': 'template', 'content': 'содержимое'}, {'name': 'Вложенная папка', 'type': 'folder', 'children': [{'name': 'Текст', 'type': 'template', 'content': ' содержимое'}, {'name': 'Еще папка', 'type': 'folder', 'children': [{'name': 'текст6', 'type': 'template', 'content': ''}, {'name': 'текст7', 'type': 'template', 'content': ''}]}]}]}, {'name': 'Папка2', 'type': 'folder', 'children': [{'name': 'Текст4', 'type': 'template', 'content': 'ПравоДоступа(""Чтение"", ""<ОбъектМетаданных>"", ""<Пользователь/Роль>"", ""<СтандартныйРеквизитСтандартнаяТабличнаяЧасть>"")'}]}, {'name': 'текст5 ', 'type': 'template', 'content': 'текст шаблона \r\nеще текст шаблона'}, {'name': 'Папка3', 'type': 'folder', 'children': [{'name': 'новая папка', 'type': 'folder', 'children': []}]}], 'root_name': 'Новый4'}
    print(f'updated_structure:  {updated_structure}')
    file_path = "F:\\Языки\\Python\\Partfolio\\cheat_sheet5\\Временно\\Новый4.st"

    # 3. Сериализуем и записываем в файл
    parser_service = FileParserService()
    file_operation = FileOperations()
    st_content = parser_service.serialize_st_structure(updated_structure)
    print(f'st_content : {st_content}')
    success = file_operation.file_manager.write_file(file_path, st_content)
    print(f'success = {success}')
    if success:
        print(f"✅ Файл {file_path} успешно обновлен")
    else:
        print(f"❌ Ошибка записи файла {file_path}")

def find_parent_in_structure2():
    updated_structure = {'structure': [{'name': 'папка', 'type': 'folder', 'children': []}], 'root_name': 'Шаблон3'}
    print(f'updated_structure:  {updated_structure}')
    file_path = "F:\\Языки\\Python\\Partfolio\\cheat_sheet5\\Временно\\Шаблон3.st"

    # 3. Сериализуем и записываем в файл
    parser_service = FileParserService()
    file_operation = FileOperations()
    st_content = parser_service.serialize_st_structure(updated_structure)
    print(f'st_content : {st_content}')
    success = file_operation.file_manager.write_file(file_path, st_content)
    print(f'success = {success}')
    if success:
        print(f"✅ Файл {file_path} успешно обновлен")
    else:
        print(f"❌ Ошибка записи файла {file_path}")

def find_parent_in_structure3():
    updated_structure2 = {'structure': [{'name': 'папка', 'type': 'folder', 'children': [{'name': 'Текст', 'type': 'template', 'content': 'тут текст'}, {'name': 'текст2', 'type': 'template', 'content': ''}]}, {'name': 'шаблон', 'type': 'template', 'content': 'здесь будет текст '}], 'root_name': 'Шаблон4'}
    updated_structure = {'structure': [{'name': 'папка', 'type': 'folder',
                                         'children': [{'name': 'Текст', 'type': 'template', 'content': 'тут текст'}]},
                                        {'name': 'шаблон', 'type': 'template', 'content': 'здесь будет текст '}],
                          'root_name': 'Шаблон4'}
    file_path = "F:\\Языки\\Python\\Partfolio\\cheat_sheet5\\Временно\\Шаблон4.st"

    # 3. Сериализуем и записываем в файл
    parser_service = FileParserService()
    file_operation = FileOperations()
    st_content = parser_service.serialize_st_structure(updated_structure)
    print(f'st_content : {st_content}')
    success = file_operation.file_manager.write_file(file_path, st_content)
    print(f'success = {success}')
    if success:
        print(f"✅ Файл {file_path} успешно обновлен")
    else:
        print(f"❌ Ошибка записи файла {file_path}")

def main() -> None:
    """Основная функция, запускаемая при выполнении модуля напрямую."""
    find_parent_in_structure()

if __name__ == "__main__":
    main()