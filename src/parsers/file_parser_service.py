from PySide6.QtCore import Qt

from src.parsers.st_file_parser import STFileParserWrapper
from src.parsers.md_file_parser import MarkdownListener
from src.parsers.metadata_cache import MetadataCache
import os

class FileParserService:
    def __init__(self):
        self.st_parser = STFileParserWrapper()
        self.md_parser = MarkdownListener()
        self.metadata_cahce = MetadataCache()

    def parse_and_get_type(self, file_path: str) -> tuple[str, dict]:
        # ✅ Реализовано: 06.07.2025
        print('зашли в метод parse_and_get_typeкласс FileParserService')
        if file_path.endswith('.st'):
            print('Выход из метода parse_and_get_type() класс FileParserService')
            return "file", self.st_parser.parse_st_file(file_path)
        elif file_path.endswith('.md'):
            print('Выход из метода parse_and_get_type() класс FileParserService')
            return "markdown", self.md_parser.parse_markdown_file(file_path)
        raise ValueError("Unsupported file type")

    def parse_metadata(self, file_path: str) -> dict:
        """Извлекает базовые метаданные файла без полного парсинга.

        Args:
            file_path: Путь к файлу или папке
        """
        # ✅ Реализовано: 24.08.2025

        # Определяем тип по расширению и содержимому
        print('Зашел в метод parse_metadata() класс FileParserService')
        if file_path.endswith('.st'):
            res = self.st_parser.parse_st_metadata_level2(file_path)
            self.metadata_cahce.set(file_path,res,'file')
            print('Вышел из метода parse_metadata() класс FileParserService')
            return res
        elif file_path.endswith('.md'):
            res = self.md_parser.parse_md_metadata(file_path)
            self.metadata_cahce.set(file_path,res,'markdown')
            print('Вышел из метода parse_metadata() класс FileParserService')
            return res

    #---Новые методы проверить их работу

    def serialize_st_structure(self, cache_structure):
        print('🥺зашли в метод serialize_st_structure() класс FileParserService🥺')
        print(f'✅️ Параметр cache_structure содержит: {cache_structure}')

        # 🔧 ИЗВЛЕКАЕМ root_name И structure
        if isinstance(cache_structure, dict):
            root_name = cache_structure.get('root_name', 'Root')
            structure_list = cache_structure.get('structure', [])
        else:
            root_name = "Root"
            structure_list = []

        print(f'🔍 root_name: {root_name}')
        print(f'🔍 structure_list: {structure_list}')

        # 🔽 СОЗДАЕМ КОРНЕВОЙ ШАБЛОН из root_name
        root_template = {
            'name': root_name,
            'type': 'template',
            'flags': 0,
            'desc1': '',
            'desc2': ''
        }

        # 🔽 fileStructure: {1, rootContent}
        # rootContent: {count, folderContent} где count - количество элементов из structure
        structure_count = len(structure_list)

        # 🔽 Сериализуем: корневой шаблон + элементы из structure
        folder_content_parts = []
        folder_content_parts.append(self._serialize_root_template(root_template))  # корневой шаблон

        for item in structure_list:
            if item['type'] == 'folder':
                folder_content_parts.append(self._serialize_folder(item))
            elif item['type'] == 'template':
                folder_content_parts.append(self._serialize_template(item))

        folder_content = ',\n'.join(folder_content_parts)

        result = f"{{1,\n{{{structure_count},\n{folder_content}\n}}\n}}"
        print(f'🟡 результат метода serialize_st_structure: {result}')
        print('выход из метода serialize_st_structure класс FileParserService')
        return result

    def _serialize_root_template(self, template_data):
        # 🔽 корневой шаблон: только templateHeader без {0,}
        print('зашли в метод _serialize_root_template() класс FileParserService')
        template_header = self._serialize_folder_header(template_data)
        print('вышел из метода _serialize_root_template() класс FileParserService')
        return template_header  # ⚠️ возвращаем без обертки {0,}

    def _serialize_template_header(self, template_data):
        # 🔽 templateHeader: {name, 0, flags, desc1, desc2}
        print('Зашли в метод _serialize_template_header() класс FileParserService')
        name = template_data['name']
        flags = template_data.get('flags', 0)
        desc1 = template_data.get('desc1', '')
        desc2 = template_data.get('desc2', '')
        print('Вышли из метода _serialize_template_header() класс FileParserService')
        return f"{{\"{name}\",0,{flags},\"{desc1}\",\"{desc2}\"}}"
    def _serialize_folder_content(self, structure_list):
        # 🔽 folderContent: элементы через запятую
        print('Зашли в метод _serialize_folder_content()  класс FileParserService')
        if not structure_list:
            return "{}"

        parts = []
        for item in structure_list:
            if item['type'] == 'folder':
                parts.append(self._serialize_folder(item))
            elif item['type'] == 'template':
                parts.append(self._serialize_template(item))

        # 🔽 ЭЛЕМЕНТЫ В СТРОКУ, РАЗДЕЛЕННЫЕ ЗАПЯТЫМИ С ПЕРЕНОСОМ
        print('Выйти из метода _serialize_folder_content()  класс FileParserService')
        return ',\n'.join(parts)

    def _serialize_folder(self, folder_data):
        # 🔽 entry для папки: {children_count, folderHeader, entryList}
        print('Зашли в метод _serialize_folder()  класс FileParserService')
        folder_header = self._serialize_folder_header(folder_data)
        children_count = len(folder_data.get('children', []))

        if children_count > 0:
            entry_list = self._serialize_entry_list(folder_data['children'])
            # 🔽 ПАПКА С ЭЛЕМЕНТАМИ: {children_count, folderHeader, entryList}
            print('Выйти из метода _serialize_folder()  класс FileParserService')
            return f"{{{children_count},\n{folder_header},\n{entry_list}\n}}"
        else:
            # 🔽 ПУСТАЯ ПАПКА: {0, folderHeader}
            print('Выйти из метода _serialize_folder()  класс FileParserService')
            return f"{{0,\n{folder_header}\n}}"

    def _serialize_template(self, template_data):
        # 🔽 entry для шаблона: {0, templateHeader}
        print('Зашли в метод _serialize_template() класс FileParserService')
        template_header = self._serialize_template_header(template_data)
        print('Выйти из метода _serialize_template()  класс FileParserService')
        return f"{{0,\n{template_header}\n}}"

    def _serialize_folder_header(self, folder_data):
        # 🔽 folderHeader: {name, 1, flags, desc1, desc2}
        print('зашли в метод _serialize_folder_header() класс FileParserService')
        name = folder_data['name']
        flags = folder_data.get('flags', 0)
        desc1 = folder_data.get('desc1', '')
        desc2 = folder_data.get('desc2', '')
        print('Выход из метода _serialize_folder_header() класс FileParserService')
        return f"{{\"{name}\",1,{flags},\"{desc1}\",\"{desc2}\"}}"

    def _serialize_template_header(self, template_data):
        # 🔽 templateHeader: {name, 0, flags, desc1, desc2}
        name = template_data['name']
        content = template_data['content']
        flags = template_data.get('flags', 0)
        desc1 = template_data.get('desc1', '')
        desc2 = template_data.get('desc2', content)
        return f"{{\"{name}\",0,{flags},\"{desc1}\",\"{desc2}\"}}"

    def _serialize_entry_list(self, children_list):
        # 🔽 entryList: entry (',' entry)*
        print('Вход в метод _serialize_entry_list класс FileParserService')
        if not children_list:
            print('Выход из метода _serialize_entry_list класс FileParserService')
            return "{}"

        entries = []
        for child in children_list:
            if child['type'] == 'folder':
                entries.append(self._serialize_folder(child))
            elif child['type'] == 'template':
                entries.append(self._serialize_template(child))

        entries_str = ',\n'.join(entries)
        print('Выход из метода _serialize_entry_list класс FileParserService')
        return f"{entries_str}"
