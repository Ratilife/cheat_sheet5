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
        if file_path.endswith('.st'):
            return "file", self.st_parser.parse_st_file(file_path)
        elif file_path.endswith('.md'):
            return "markdown", self.md_parser.parse_markdown_file(file_path)
        raise ValueError("Unsupported file type")

    def parse_metadata(self, file_path: str) -> dict:
        """Извлекает базовые метаданные файла без полного парсинга.

        Args:
            file_path: Путь к файлу или папке
        """
        # ✅ Реализовано: 24.08.2025

        # Определяем тип по расширению и содержимому
        if file_path.endswith('.st'):
            res = self.st_parser.parse_st_metadata_level2(file_path)
            self.metadata_cahce.set(file_path,res,'file')
            return res
        elif file_path.endswith('.md'):
            res = self.md_parser.parse_md_metadata(file_path)
            self.metadata_cahce.set(file_path,res,'markdown')
            return res

    #---Новые методы проверить их работу

    def serialize_st_structure(self, cache_structure):
        # TODO 🚧 В разработке: 13.10.2025
        # 1. fileStructure: {count, rootContent}
        # Получаем структуру
        print('🥺зашли в метод serialize_st_structure🥺')
        print(f'✅️ Параметр cache_structure содержит: {cache_structure}')

        # 🔧 ИЗВЛЕКАЕМ root_name И structure
        if isinstance(cache_structure, dict):
            if 'root_name' in cache_structure and 'structure' in cache_structure:
                # Это полная структура с root_name
                root_name = cache_structure['root_name']
                structure_list = cache_structure['structure']
            elif 'structure' in cache_structure:
                # Только структура, создаем root_name из первого элемента
                structure_list = cache_structure['structure']
                root_name = structure_list[0]['name'] if structure_list else "Root"
            else:
                # Неизвестный формат
                structure_list = cache_structure
                root_name = "Root"
        elif isinstance(cache_structure, list):
            structure_list = cache_structure
            root_name = structure_list[0]['name'] if structure_list else "Root"
        else:
            structure_list = []
            root_name = "Root"

        print(f'🔍 root_name: {root_name}')
        print(f'🔍 structure_list: {structure_list}')

        # 🔽 СОЗДАЕМ КОРНЕВОЙ ШАБЛОН С root_name
        root_template = {
            'name': root_name,
            'type': 'template',
            'flags': 0,
            'desc1': '',
            'desc2': ''
        }

        # 🔽 ДОБАВЛЯЕМ КОРНЕВОЙ ШАБЛОН В НАЧАЛО СТРУКТУРЫ
        full_structure = [root_template] + structure_list

        count = len(full_structure)
        root_content = self._serialize_root_content(full_structure)

        result = f"{count},\n{root_content}"
        print(f'🟡 результат метода serialize_st_structure: {result}')
        return result

    def _serialize_root_content(self,  structure_list):
        # TODO 🚧 В разработке: 13.10.2025
        # 2. rootContent: {count, folderContent}
        if not structure_list:
            return "{}"

        count = len(structure_list)
        folder_content = self._serialize_folder_content(structure_list)

        # 🔽 ФОРМАТИРОВАНИЕ: {count, элементы_в_строку_но_с_переносами}
        return f"{{\n{count},\n{folder_content}\n}}"


    def _serialize_folder_content(self, structure_list):
        # TODO 🚧 В разработке: 13.10.2025
        # 3. folderContent: folderHeader (',' entry)*

        if not structure_list:
            return ""

        parts = []
        for item in structure_list:
            if item['type'] == 'folder':
                parts.append(self._serialize_folder(item))
            elif item['type'] == 'template':
                parts.append(self._serialize_template(item))

        # 🔽 ЭЛЕМЕНТЫ В СТРОКУ, РАЗДЕЛЕННЫЕ ЗАПЯТЫМИ С ПЕРЕНОСОМ
        return ',\n'.join(parts)


    def _serialize_folder(self,  folder_data):
        # TODO 🚧 В разработке: 13.10.2025
        # 4. entry для папки: {count, folderHeader, entryList} или {count, folderHeader}

        folder_header = self._serialize_folder_header(folder_data)
        children_count = len(folder_data.get('children', []))

        if children_count > 0:
            entry_list = self._serialize_entry_list(folder_data['children'])
            # 🔽 ПАПКА: {count, заголовок_в_строку, содержимое_в_столбик}
            return f"{{\n{children_count},\n{folder_header},\n{entry_list}\n}}"
        else:
            # 🔽 ПУСТАЯ ПАПКА: {0, заголовок_в_строку}
            return f"{{\n0,\n{folder_header}\n}}"


    def _serialize_template(self, template_data):
        # TODO 🚧 В разработке: 13.10.2025
        # 5. entry для шаблона: {0, templateHeader}
        template_header = self._serialize_template_header(template_data)
        # 🔽 ШАБЛОН: {0, заголовок_в_строку}
        return f"{{\n0,\n{template_header}\n}}"

    def _get_item_flags(self, item):
        # TODO 🚧 В разработке: 13.10.2025
        """Получает флаги элемента - НУЖНО НАСТРОИТЬ ЭТОТ МЕТОД"""
        if hasattr(item, 'item_data') and len(item.item_data) > 3:
            return item.item_data[3]  # 🔍 Настрой под свою структуру
        return 0

    def _get_item_description1(self, item):
        # TODO 🚧 В разработке: 13.10.2025
        """Получает description1 - НУЖНО НАСТРОИТЬ"""
        if hasattr(item, 'item_data') and len(item.item_data) > 4:
            return item.item_data[4] or ""
        return ""

    def _get_item_description2(self, item):
        # TODO 🚧 В разработке: 13.10.2025
        """Получает description2 - НУЖНО НАСТРОИТЬ"""
        if hasattr(item, 'item_data') and len(item.item_data) > 5:
            return item.item_data[5] or ""
        return ""

    def _serialize_folder_header(self,  folder_data):
        # TODO 🚧 В разработке: 13.10.2025
        # 6. folderHeader: {name, 1, flags, desc1, desc2}
        name = folder_data['name']
        flags = folder_data.get('flags', 0)
        desc1 = folder_data.get('desc1', '')
        desc2 = folder_data.get('desc2', '')
        # 🔽 ЗАГОЛОВОК В СТРОКУ: {"name",1,flags,"desc1","desc2"}
        return f"{{\"{name}\",1,{flags},\"{desc1}\",\"{desc2}\"}}"

    def _serialize_template_header(self, template_data):   #TODO проверить метод _serialize_template_header перем content не используется
        # TODO 🚧 В разработке: 13.10.2025
        # 7. templateHeader: {name, 0, flags, desc1, desc2}
        name = template_data['name']
        flags = template_data.get('flags', 0)
        desc1 = template_data.get('desc1', '')
        desc2 = template_data.get('desc2', '')
        # 🔽 ЗАГОЛОВОК В СТРОКУ: {"name",0,flags,"desc1","desc2"}
        return f"{{\"{name}\",0,{flags},\"{desc1}\",\"{desc2}\"}}"


    def _serialize_entry_list(self, children_list):
        # TODO 🚧 В разработке: 13.10.2025
        # 8. entryList: entry (',' entry)*
        if not children_list:
            return "{}"

        entries = []
        for child in children_list:
            if child['type'] == 'folder':
                entries.append(self._serialize_folder(child))
            elif child['type'] == 'template':
                entries.append(self._serialize_template(child))

        # 🔽 ЭЛЕМЕНТЫ В СТРОКУ С ПЕРЕНОСАМИ
        entries_str = ',\n'.join(entries)
        return f"{{\n{entries_str}\n}}"






