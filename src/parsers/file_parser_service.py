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

    def serialize_st_structure(self, model, root_index):
        # TODO 🚧 В разработке: 13.10.2025
        # 1. fileStructure: {count, rootContent}
        root_content = self._serialize_root_content(model, root_index)
        file_structure = f"{{{model.rowCount(root_index)}, {root_content}}}"
        return file_structure

    def _serialize_root_content(self, model, root_index):
        # TODO 🚧 В разработке: 13.10.2025
        # 2. rootContent: {count, folderContent}
        folder_content = self._serialize_folder_content(model, root_index)
        return f"{{{model.rowCount(root_index)}, {folder_content}}}"

    def _serialize_folder_content(self, model, parent_index):
        # TODO 🚧 В разработке: 13.10.2025
        # 3. folderContent: folderHeader (',' entry)*
        if model.rowCount(parent_index) == 0:
            return "{}"

        parts = []
        for row in range(model.rowCount(parent_index)):
            child_index = model.index(row, 0, parent_index)
            item_type = model.get_item_type(child_index)
            type_element = item_type ['type']
            if type_element  == 'folder':
                parts.append(self._serialize_folder(model, child_index))
            elif type_element == 'template':
                parts.append(self._serialize_template(model, child_index))

        return ', '.join(parts)

    def _serialize_folder(self, model, folder_index):
        # TODO 🚧 В разработке: 13.10.2025
        # 4. entry для папки: {count, folderHeader, entryList} или {count, folderHeader}
        folder_header = self._serialize_folder_header(model, folder_index)

        if model.rowCount(folder_index) > 0:
            # Папка с детьми: {count, folderHeader, entryList}
            entry_list = self._serialize_entry_list(model, folder_index)
            return f"{{{model.rowCount(folder_index)}, {folder_header}, {entry_list}}}"
        else:
            # Пустая папка: {count, folderHeader}
            return f"{{0, {folder_header}}}"

    def _serialize_template(self, model, template_index):
        # TODO 🚧 В разработке: 13.10.2025
        # 5. entry для шаблона: {0, templateHeader}
        template_header = self._serialize_template_header(model, template_index)
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

    def _serialize_folder_header(self,  model, folder_index):
        # TODO 🚧 В разработке: 13.10.2025
        # 6. folderHeader: {name, 1, flags, desc1, desc2}
        folder_element = folder_index.internalPointer()
        name = model.data(folder_index, Qt.DisplayRole)
        flags = self._get_item_flags(folder_element)
        desc1 = self._get_item_description1(folder_element)
        desc2 = self._get_item_description2(folder_element)

        return f'{{"{name}", 1, {flags}, "{desc1}", "{desc2}"}}'

    def _serialize_template_header(self,  model, template_index):
        # TODO 🚧 В разработке: 13.10.2025
        # 7. templateHeader: {name, 0, flags, desc1, desc2}
        template_element = template_index.internalPointer()
        name = model.data(template_index, Qt.DisplayRole)
        flags = self._get_item_flags(template_element)
        desc1 = self._get_item_description1(template_element)
        desc2 = self._get_item_description2(template_element)

        return f'{{"{name}", 0, {flags}, "{desc1}", "{desc2}"}}'

    def _serialize_entry_list(self, model, parent_index):
        # TODO 🚧 В разработке: 13.10.2025
        # 8. entryList: entry (',' entry)*
        entries = []
        for row in range(model.rowCount(parent_index)):
            child_index = model.index(row, 0, parent_index)
            item_type = model.get_item_type(child_index)

            if item_type == 'folder':
                entries.append(self._serialize_folder(model, child_index))
            elif item_type == 'template':
                entries.append(self._serialize_template(model, child_index))

        return f"{{{', '.join(entries)}}}"






