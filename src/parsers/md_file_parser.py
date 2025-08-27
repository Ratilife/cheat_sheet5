"""
    Модуль md_file_parser.py

    Предназначен для парсинга Markdown-файлов и извлечения их структуры.
    Основные возможности:
        1. Чтение содержимого Markdown-файлов
        2. Формирование структуры документа
        3. Обработка ошибок чтения файлов
"""
import os
from pathlib import Path

class MarkdownListener:
    """
        Класс для обработки и анализа Markdown-файлов.

        Содержит методы для:
        - чтения файлов
        - извлечения структуры
        - обработки ошибок
    """
    def __init__(self):
        """
            Инициализация объекта MarkdownListener.
            Создает пустой список для хранения структуры документа.
        """
        self.structure = [] # Список для хранения структуры документа

    def get_structure(self):
        """
            Возвращает текущую структуру документа.
            Возвращает:
            list: Список элементов структуры документа
        """
        return self.structure

    def parse_markdown_file(self, file_path):

        """
        Парсит указанный Markdown-файл и возвращает его структуру.

        Этот метод читает содержимое Markdown-файла по заданному пути, сохраняет его в структуре в виде словаря с ключами 'name', 'type' и 'content',
        где:
            - 'name' — имя файла без расширения,
            - 'type' — тип документа ('markdown'),
            - 'content' — содержимое файла в виде строки.

        В случае успешного чтения файла возвращается словарь с двумя ключами:
            - 'structure': список из одного элемента, содержащий структуру документа;
            - 'root_name': имя корневого элемента (имя файла без расширения).

        В случае возникновения ошибки чтения файла метод выводит сообщение об ошибке и возвращает пустую структуру и значение "Error" в качестве имени корневого элемента.

        Parameters
        ----------
        file_path : str
            Путь к Markdown-файлу, который необходимо распарсить.

        Returns
        -------
        dict
            Словарь с двумя ключами:
                - 'structure' (list): список, содержащий структуру документа (или пустой список при ошибке);
                - 'root_name' (str): имя файла без расширения (или "Error" при ошибке).

        Примеры
        -------
        >>> parser = MdFileParser()
        >>> parser.parse_markdown_file('example.md')
        {
            'structure': [{'name': 'example', 'type': 'markdown', 'content': '<содержимое файла>'}],
            'root_name': 'example'
        }

        Notes
        -----
        Метод автоматически обрабатывает ошибки открытия и чтения файла, возвращая безопасный результат.
        """
        try:
            # Чтение содержимого файла с указанием кодировки UTF-8
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            # Получение имени файла без расширения
            file_name = os.path.splitext(os.path.basename(file_path))[0]
            # Формирование структуры документа
            self.structure = [{
                'name': file_name,       # Имя документа
                'type': 'markdown',      # Тип документа
                'content': content       # Содержимое файла
            }]
            # Возвращаем структуру и имя корневого элемента
            return {
                'structure': self.structure,
                'root_name': file_name
            }
        except Exception as e:
            # Обработка ошибок при чтении файла
            print(f"Error parsing markdown file: {str(e)}")
            # Возвращаем пустую структуру в случае ошибки
            return {
                'structure': [],
                'root_name': "Error"
            }

    def parse_md_metadata(self, file_path: str, first_lines: list = None) -> dict:
        """Парсит метаданные Markdown-файла"""
        if first_lines is None:
            first_lines = []
        title = next((line.strip('# ') for line in first_lines if line.startswith('#')), None)

        # Получаем имя файла без расширения через pathlib
        file_name_without_extension = Path(file_path).stem

        return {
            "root_name": title or file_name_without_extension,
            "type": "markdown",
            "size": os.path.getsize(file_path),
            "last_modified": os.path.getmtime(file_path),
            #"headers": [line.strip('#') for line in first_lines if line.startswith('#')]
        }
