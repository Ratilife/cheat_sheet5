import os
import time
from typing import Optional, Dict, Any, List
from parsers.file_parser_service import FileParserService
class MetadataCache:
    # TODO 🚧 В разработке: 22.08.2025
    _instance = None # Это "хранилище" для синглтон-объекта. Классовая переменная (принадлежит классу, а не экземпляру)
    _cache: Dict[str, Dict[str, Any]] = {}
    _default_ttl = 300  # 5 минут в секундах

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._cache = {}
        return cls._instance

    def set_st(self, file_path: str, metadata: dict, ttl: int = None) -> None:
        """
        Сохраняет метаданные файла в кэш.

        Args:
            file_path: Путь к файлу (ключ кэша)
            metadata: Словарь с метаданными от парсера
            ttl: Время жизни записи в кэше (секунды)
        """
        try:
            # Получаем информацию о файле для проверки изменений
            file_stats = os.stat(file_path)

            # ТОЛЬКО необходимые данные для кэша
            self._cache[file_path] = {
                'metadata': metadata,  # Основные данные от парсера
                'timestamp': time.time(),  # Когда положили в кэш
                'file_size': file_stats.st_size,  # Размер файла (для проверки изменений)
                'file_mtime': file_stats.st_mtime,  # Время изменения (для проверки изменений)
                'ttl': ttl or self._default_ttl  # Время жизни записи
            }

        except Exception as e:
            # В случае ошибки создаем запись с базовой информацией
            self._cache[file_path] = {
                'metadata': metadata,
                'timestamp': time.time(),
                'file_size': 0,
                'file_mtime': 0,
                'ttl': ttl or self._default_ttl,
                'error': str(e)
            }

    def get_st(self, file_path: str) -> Optional[dict]:
        """
        Получает метаданные из кэша с проверкой актуальности.

        Returns:
            dict: Метаданные от парсера (то, что было в `metadata`) или None если устарело
        """
        if file_path not in self._cache:
            return None

        cached_data = self._cache[file_path]

        # 1. Проверяем TTL (время жизни)
        if time.time() - cached_data['timestamp'] > cached_data['ttl']:
            self.invalidate(file_path)
            return None

        # 2. Проверяем, не изменился ли файл на диске
        if self._is_file_modified(file_path, cached_data):
            self.invalidate(file_path)
            return None

        # Возвращаем ТОЛЬКО метаданные от парсера
        return cached_data['metadata']

    def _is_file_modified(self, file_path: str, cached_data: dict) -> bool:
        """Проверяет, изменился ли файл на диске"""
        if not os.path.exists(file_path):
            return True

        try:
            current_size = os.path.getsize(file_path)
            current_mtime = os.path.getmtime(file_path)

            # Файл изменился, если изменился размер или время модификации
            return (current_size != cached_data['file_size'] or
                    current_mtime != cached_data['file_mtime'])
        except OSError:
            return True

    def invalidate(self, file_path: str):
        """Удаляет данные из кэша"""
        self._cache.pop(file_path, None)

    def invalidate_all(self):
        """Очищает весь кэш"""
        self._cache.clear()

    def get_stats(self) -> dict:
        """Возвращает статистику кэша"""
        return {
            'total_items': len(self._cache),
            'memory_usage': sum(len(str(v)) for v in self._cache.values())
        }

    #--------для MD-файлов-------------

    def set_md(self, file_path: str, metadata: dict = None, ttl: int = None) -> None:
        """
        Сохраняет метаданные Markdown-файла в кэш.

        Args:
            file_path: Путь к MD-файлу
            metadata: Опциональные метаданные (если None - парсим автоматически)
            ttl: Время жизни записи в кэше (секунды)
        """
        try:
            # Если метаданные не предоставлены - парсим файл
            if metadata is None:
                metadata = self._parse_md_file_metadata(file_path)

            # Получаем информацию о файле
            file_stats = os.stat(file_path)

            # Создаем запись в кэше
            self._cache[file_path] = {
                'metadata': metadata,
                'timestamp': time.time(),
                'file_size': file_stats.st_size,
                'file_mtime': file_stats.st_mtime,
                'ttl': ttl or self._default_ttl,
                'file_type': 'markdown'
            }

        except Exception as e:
            # В случае ошибки создаем базовую запись
            self._cache[file_path] = {
                'metadata': metadata or {
                    "name": os.path.basename(file_path),
                    "type": "markdown",
                    "size": 0,
                    "last_modified": 0
                },
                'timestamp': time.time(),
                'file_size': 0,
                'file_mtime': 0,
                'ttl': ttl or self._default_ttl,
                'file_type': 'markdown',
                'error': str(e)
            }

    def _parse_md_file_metadata(self, file_path: str) -> dict:
        """
        Парсит Markdown-файл и извлекает метаданные.

        Args:
            file_path: Путь к MD-файлу

        Returns:
            Словарь с метаданными Markdown-файла
        """
        try:
            # Читаем первые несколько строк для извлечения заголовка
            with open(file_path, 'r', encoding='utf-8') as f:
                first_lines = [f.readline().strip() for _ in range(5)]

            # Извлекаем заголовок из первых строк
            title = next((line.strip('# ') for line in first_lines if line.startswith('#')), None)

            # Получаем статистику файла
            file_stats = os.stat(file_path)

            # Формируем метаданные (только базовые поля)
            return {
                "name": title or os.path.basename(file_path),
                "type": "markdown",
                "size": file_stats.st_size,
                "last_modified": file_stats.st_mtime,
                "has_title": title is not None,
                "file_path": file_path
            }

        except Exception as e:
            # Возвращаем базовые метаданные в случае ошибки
            return {
                "name": os.path.basename(file_path),
                "type": "markdown",
                "size": os.path.getsize(file_path) if os.path.exists(file_path) else 0,
                "last_modified": os.path.getmtime(file_path) if os.path.exists(file_path) else 0,
                "has_title": False,
                "file_path": file_path,
                "error": str(e)
            }

    def get_md_metadata(self, file_path: str) -> Optional[dict]:
        """
        Получает метаданные Markdown-файла из кэша.

        Returns:
            dict: Метаданные MD-файла или None если устарело
        """
        cached_data = self.get(file_path)
        if cached_data and cached_data.get('file_type') == 'markdown':
            return cached_data['metadata']
        return None

    def get_md_title(self, file_path: str) -> Optional[str]:
        """
        Получает заголовок Markdown-файла из кэша.
        Если заголовка нет, возвращает имя файла.
        """
        #TODO 🚧 В разработке: 22.08.2025 - мертвый код  get_md_title
        md_metadata = self.get_md_metadata(file_path)
        if md_metadata:
            return md_metadata['name']  # name уже содержит либо заголовок, либо имя файла
        return None
