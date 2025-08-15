from src.parsers.st_file_parser import STFileParserWrapper
from src.parsers.md_file_parser import MarkdownListener
import os

class FileParserService:
    def __init__(self):
        self.st_parser = STFileParserWrapper()
        self.md_parser = MarkdownListener()

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

        Returns:
            {
                "name": "имя_файла",
                "type": "file"|"folder",
                "size": int,
                "last_modified": float (timestamp)
            }
        """
        # TODO 🚧 В разработке: 15.07.2025
        if os.path.isdir(file_path):
            return {
                "name": os.path.basename(file_path),
                "type": "folder",
                "size": 0,
                "last_modified": os.path.getmtime(file_path)
            }

        # Для ST/MD файлов - читаем только начало файла
        with open(file_path, 'r', encoding='utf-8') as f:
            first_lines = [f.readline() for _ in range(3)]  # Первые 3 строки

        # Определяем тип по расширению и содержимому
        if file_path.endswith('.st'):
            return self.st_parser.parse_st_metadata(file_path, first_lines)
        elif file_path.endswith('.md'):
            return self.md_parser.parse_md_metadata(file_path, first_lines)
        else:
            return {
                "name": os.path.basename(file_path),
                "type": "file",
                "size": os.path.getsize(file_path),
                "last_modified": os.path.getmtime(file_path)
            }



