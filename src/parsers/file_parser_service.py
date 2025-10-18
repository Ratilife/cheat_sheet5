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

    def serialize_st_structure(self, model, cache_structure):
        # TODO 🚧 В разработке: 13.10.2025
        # 1. fileStructure: {count, rootContent}
        root_content = self._serialize_root_content(model, cache_structure)
        file_structure = f"{{{model.rowCount(cache_structure)}, {root_content}}}"
        return file_structure

    def _serialize_root_content(self, model, cache_structure):
        # TODO 🚧 В разработке: 13.10.2025
        # 2. rootContent: {count, folderContent}
        folder_content = self._serialize_folder_content(cache_structure['structure'])
        return f"{{{model.rowCount(cache_structure['structure'])}, {folder_content}}}"

    def _serialize_folder_content(self, model, structure_list):
        # TODO 🚧 В разработке: 13.10.2025
        # 3. folderContent: folderHeader (',' entry)*
        if model.rowCount(structure_list) == 0:
            return "{}"

        parts = []
        for item in structure_list:
            if item['type'] == 'folder':
                parts.append(self._serialize_folder(item))
            elif item['type'] == 'template':
                parts.append(self._serialize_template(item))

        return ', '.join(parts)

    def _serialize_folder(self,  folder_data):
        # TODO 🚧 В разработке: 13.10.2025
        # 4. entry для папки: {count, folderHeader, entryList} или {count, folderHeader}
        folder_header = self._serialize_folder_header(folder_data)
        children_count = len(folder_data.get('children', []))

        if children_count > 0:
            entry_list = self._serialize_entry_list(folder_data['children'])
            return f"{{{children_count}, {folder_header}, {entry_list}}}"
        else:
            return f"{{0, {folder_header}}}"

    def _serialize_template(self, template_data):
        # TODO 🚧 В разработке: 13.10.2025
        # 5. entry для шаблона: {0, templateHeader}
        template_header = self._serialize_template_header(template_data)
        return f"{{0, {template_header}}}"

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
        return f'{{"{name}", 1, {flags}, "{desc1}", "{desc2}"}}'

        return f'{{"{name}", 1, {flags}, "{desc1}", "{desc2}"}}'

    def _serialize_template_header(self, template_data):   #TODO проверить метод _serialize_template_header перем content не используется
        # TODO 🚧 В разработке: 13.10.2025
        # 7. templateHeader: {name, 0, flags, desc1, desc2}
        name = template_data['name']
        flags = template_data.get('flags', 0)
        desc1 = template_data.get('desc1', '')
        desc2 = template_data.get('desc2', '')
        content = template_data.get('content', '')
        return f'{{"{name}", 0, {flags}, "{desc1}", "{desc2}"}}'

    def _serialize_entry_list(self, children_list):
        # TODO 🚧 В разработке: 13.10.2025
        # 8. entryList: entry (',' entry)*
        entries = []
        for child in children_list:
            if child['type'] == 'folder':
                entries.append(self._serialize_folder(child))
            elif child['type'] == 'template':
                entries.append(self._serialize_template(child))

        return f"{{{', '.join(entries)}}}"






