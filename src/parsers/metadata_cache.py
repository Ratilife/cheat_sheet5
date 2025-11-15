import os
import sys
import time
from typing import Optional, Dict, Any

class MetadataCache:
    """Кэш метаданных файлов для оптимизации доступа к структуре дерева файлов.

        Класс реализует паттерн Singleton для обеспечения единого экземпляра кэша
        во всем приложении. Предназначен для хранения легковесных метаданных файлов
        (структура дерева, имена элементов, типы) без полного содержимого файлов.

        Основные возможности:
            - Кэширование метаданных после парсинга файлов (ST и MD форматы)
            - Автоматическая проверка актуальности данных через TTL (Time To Live)
            - Автоматическая инвалидация при изменении файла на диске
            - Минимальное использование памяти (хранит только структуру, не содержимое)

        Класс используется совместно с ContentCache:
            - MetadataCache: быстрый доступ к структуре дерева для отображения UI
            - ContentCache: полное содержимое файлов для редактирования

        Attributes:
            _instance (Optional['MetadataCache']): Единственный экземпляр класса (Singleton).
            _cache (Dict[str, Dict[str, Any]]): Словарь кэша, где ключ - путь к файлу,
                значение - словарь с метаданными и служебной информацией:
                {
                    'metadata': dict,      # Структура дерева от парсера
                    'timestamp': float,    # Время добавления в кэш (time.time())
                    'file_size': int,      # Размер файла в байтах
                    'file_mtime': float,   # Время последней модификации файла
                    'ttl': int,            # Время жизни записи в секундах
                    'file_type': str       # Тип файла ('file' для .st, 'markdown' для .md)
                }
            _default_ttl (int): Время жизни записи в кэше по умолчанию (300 секунд = 5 минут).

        Example:
            >>> cache = MetadataCache()  # Создание/получение единственного экземпляра
            >>>
            >>> # Сохранение метаданных после парсинга
            >>> metadata = {
            ...     'structure': [{'name': 'Template1', 'type': 'template', ...}],
            ...     'root_name': 'MyFile'
            ... }
            >>> cache.set('/path/to/file.st', metadata, file_type='file', ttl=600)
            >>>
            >>> # Получение метаданных (с автоматической проверкой актуальности)
            >>> cached_metadata = cache.get('/path/to/file.st')
            >>> if cached_metadata:
            ...     print(cached_metadata['root_name'])  # 'MyFile'
            >>>
            >>> # Инвалидация при изменении файла
            >>> cache.invalidate('/path/to/file.st')

        Note:
            Класс использует паттерн Singleton через переопределение метода __new__.
            Все вызовы MetadataCache() возвращают один и тот же экземпляр.

            При получении данных из кэша автоматически проверяется:
            1. Не истек ли TTL (время жизни записи)
            2. Не изменился ли файл на диске (сравнение размера и времени модификации)

            Если любая из проверок не пройдена, запись удаляется из кэша и возвращается None.

        See Also:
            ContentCache: Кэш полного содержимого файлов для редактирования
            FileParserService: Сервис парсинга, который использует MetadataCache
            TreeModelManager: Менеджер моделей дерева, использующий кэш для быстрого доступа
    """
    # ✅ Реализовано: 24.08.2025
    _instance = None # Это "хранилище" для синглтон-объекта. Классовая переменная (принадлежит классу, а не экземпляру)
    _cache: Dict[str, Dict[str, Any]] = {}
    _default_ttl = 300  # 5 минут в секундах

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._cache = {}
        return cls._instance

    def set(self, file_path: str, metadata: dict,  file_type: str = None, ttl: int = None) -> None:
        """
        Универсальный метод для сохранения метаданных в кэш.
        """
        try:
            # Получаем информацию о файле для проверки изменений
            file_stats = os.stat(file_path)
            # ТОЛЬКО необходимые данные для кэша
            self._cache[file_path] = {
                'metadata': metadata,                   # Основные данные от парсера
                'timestamp': time.time(),               # Когда положили в кэш
                'file_size': file_stats.st_size,        # Размер файла (для проверки изменений)
                'file_mtime': file_stats.st_mtime,      # Время изменений (для проверки изменений)
                'ttl': ttl or self._default_ttl,        # Время жизни записи
                'file_type': file_type                  # тип файла st или md
            }
        except Exception as e:
            # В случае ошибки создаем запись с базовой информацией
            self._cache[file_path] = {
                'metadata': metadata or {
                    "name": os.path.basename(file_path),
                    "type": file_type or "unknown",
                    "size": 0,
                    "last_modified": 0
                },
                'timestamp': time.time(),
                'file_size': 0,
                'file_mtime': 0,
                'ttl': ttl or self._default_ttl,
                'file_type': file_type,
                'error': str(e)
            }


    def get(self, file_path: str) -> Optional[dict]:
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
            current_stats = os.stat(file_path)

            # Файл изменился, если изменился размер или время модификации
            return (current_stats.st_size != cached_data['file_size'] or
                    current_stats.st_mtime != cached_data['file_mtime'])
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
            'memory_usage_bytes': sum(sys.getsizeof(v) for v in self._cache.values())
        }

    #--------для MD-файлов-------------

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
