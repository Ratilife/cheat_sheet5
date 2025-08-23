import sys
import time
import threading
from typing import Optional, Dict, Any
from collections import OrderedDict
class ContentCache:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_cache()
        return cls._instance



    def _init_cache(self, max_size: int = 100 * 1024 * 1024):  # 100 MB по умолчанию
        """Инициализация LRU-кэша"""
        self._lock = threading.RLock()
        self._cache = OrderedDict()  # Сохраняет порядок использования
        self._max_size = max_size
        self._current_size = 0
        self._hits = 0
        self._misses = 0

    def _evict_oldest(self):
        """Вытесняет самый старый элемент из кэша"""
        with self._lock:
            if not self._cache:
                return

            # LRU: вытесняем первый (самый старый) элемент
            file_path, data = self._cache.popitem(last=False)
            self._current_size -= data['size']
            print(f"Вытеснен из кэша: {file_path} ({data['size']} байт)")

    def _get_size(self, obj, depth: int = 0, max_depth: int = 50, _seen: Optional[set] = None) -> int:
        """
        Рекурсивно вычисляет размер объекта в байтах с ограничением глубины.

        Args:
            obj: Объект для вычисления размера
            depth: Текущая глубина рекурсии (внутренний параметр)
            max_depth: Максимальная глубина рекурсии
            _seen: Множество для отслеживания обработанных объектов (внутренний параметр)

        Returns:
            int: Размер объекта в байтах
        """
        # Защита от циклических ссылок
        if _seen is None:
            _seen = set()

        obj_id = id(obj)
        if obj_id in _seen:
            return 0

        # Проверка максимальной глубины рекурсии
        if depth >= max_depth:
            print(f"Предупреждение: достигнута максимальная глубина рекурсии ({max_depth}) для объекта {type(obj)}")
            return sys.getsizeof(obj)

        _seen.add(obj_id)
        size = sys.getsizeof(obj)

        try:
            if isinstance(obj, dict):
                for key, value in obj.items():
                    size += sys.getsizeof(key) + self._get_size(value, depth + 1, max_depth, _seen)
            elif isinstance(obj, (list, tuple, set, frozenset)):
                for item in obj:
                    size += self._get_size(item, depth + 1, max_depth, _seen)
            elif hasattr(obj, '__dict__'):
                # Для объектов с атрибутами
                size += self._get_size(obj.__dict__, depth + 1, max_depth, _seen)
        finally:
            _seen.remove(obj_id)

        return size

    def invalidate(self, file_path: str):
        """Удаляет данные из кэша"""
        #  TODO 🚧 В разработке: 23.08.2025 - мертвый код invalidate
        with self._lock:
            if file_path in self._cache:
                data = self._cache.pop(file_path)
                self._current_size -= data['size']

    def invalidate_all(self):
        """Очищает весь кэш"""
        #  TODO 🚧 В разработке: 23.08.2025 - мертвый код invalidate_all
        with self._lock:
            self._cache.clear()
            self._current_size = 0

    def set(self, file_path: str, content: dict, size: int = None):
        """
         Сохраняет результат парсинга файла в кэш с автоматическим LRU-вытеснением.

         Метод добавляет или обновляет данные в кэше для указанного файла, используя
         результат парсинга, полученный от методов parse_st_file() или parse_markdown_file().
         При нехватке места автоматически вытесняет редко используемые элементы.

         Args:
             file_path (str): Полный путь к файлу, используемый как ключ кэша
             content (dict): Структура данных после парсинга, содержащая:
                 - 'structure': иерархическая структура файла (списки/словари)
                 - 'root_name': имя корневого элемента
             size (int, optional): Размер данных в байтах. Если не указан, вычисляется автоматически.

         Raises:
             TypeError: Если передан некорректный тип данных для file_path или content.

         Notes:
             - Данные сохраняются в формате:
               {
                   'content': dict,       # результат парсинга (структура + root_name)
                   'size': int,           # размер данных в байтах
                   'timestamp': float,    # время добавления (time.time())
                   'access_count': int    # счетчик обращений (инициализируется 0)
               }
             - При достижении лимита размера кэша вызывается _evict_oldest()
             - Размер вычисляется как длина UTF-8 представления структуры, если не указан явно

         Example:
             >>> cache.set('/path/to/file.st',
             ...           {'structure': [...], 'root_name': 'file'},
             ...           1024)
         """
        with self._lock:
            if size is None:
                # Оценка размера структуры данных парсинга
                size = self._get_size(content)

            # Вытесняем старые данные, если не хватает места
            while self._current_size + size > self._max_size and self._cache:
                self._evict_oldest()

            # Сохраняем результат парсинга в кэш
            self._cache[file_path] = {
                'content': content,  # структура данных после парсинга
                'size': size,
                'timestamp': time.time(),
                'access_count': 0
            }
            self._current_size += size

    def get(self, file_path: str) -> Optional[dict]:
        """
        Получает результат парсинга файла из кэша.

        Метод возвращает структуру данных, полученную при парсинге файла, если она находится в кэше.
        При этом обновляется позиция элемента в LRU-кеше (перемещается в конец) и увеличивается счетчик обращений.

        Args:
            file_path (str): Полный путь к файлу, данные которого нужно получить из кэша.

        Returns:
            Optional[dict]: Структура данных парсинга или None, если файл не найден в кэше:
                - 'structure': иерархическая структура файла (списки/словари)
                - 'root_name': имя корневого элемента

        Raises:
            TypeError: Если file_path не является строкой.

        Notes:
            - При успешном получении данных обновляется статистика попаданий (hits)
            - При отсутствии данных обновляется статистика промахов (misses)
            - Элемент перемещается в конец OrderedDict (обновляется время последнего доступа)
            - Увеличивается счетчик обращений к конкретному элементу

        Example:
            >>> cached_data = cache.get('/path/to/file.st')
            >>> if cached_data:
            ...     print(cached_data['root_name'])  # 'my_file'
            ...     print(cached_data['structure'])  # [{'name': 'template1', 'type': 'template', ...}]
        """
        with self._lock:
            if not isinstance(file_path, str):
                raise TypeError("file_path должен быть строкой")

            if file_path not in self._cache:
                self._misses += 1
                return None

            # Получаем данные и обновляем позицию в LRU (перемещаем в конец)
            data = self._cache.pop(file_path)
            self._cache[file_path] = data

            # Обновляем статистику
            self._hits += 1
            data['access_count'] += 1

            return data['content']

    def get_stats(self) -> Dict[str, Any]:
        """
        Возвращает подробную статистику использования кэша.

        Собирает и возвращает метрики производительности и использования памяти кэша,
        включая информацию о попаданиях, промахах, эффективности и распределении памяти.

        Returns:
            Dict[str, Any]: Словарь со статистическими данными кэша:
                - 'total_items': int - общее количество элементов в кэше
                - 'total_size': int - текущий размер данных в кэше (байты)
                - 'max_size': int - максимальный допустимый размер кэша (байты)
                - 'memory_usage_percent': float - процент использования памяти (0-100)
                - 'hits': int - количество успешных обращений к кэшу
                - 'misses': int - количество неудачных обращений к кэшу
                - 'total_requests': int - общее количество запросов к кэшу
                - 'hit_ratio': float - коэффициент попаданий (0-1)
                - 'miss_ratio': float - коэффициент промахов (0-1)
                - 'average_item_size': float - средний размер элемента в кэше (байты)
                - 'oldest_item_timestamp': Optional[float] - время добавления самого старого элемента
                - 'newest_item_timestamp': Optional[float] - время добавления самого нового элемента
                - 'cache_age_seconds': Optional[float] - возраст самого старого элемента в секундах

        Example:
            >>> stats = cache.get_stats()
            >>> print(stats)
            {
                'total_items': 15,
                'total_size': 5242880,
                'max_size': 10485760,
                'memory_usage_percent': 50.0,
                'hits': 120,
                'misses': 30,
                'total_requests': 150,
                'hit_ratio': 0.8,
                'miss_ratio': 0.2,
                'average_item_size': 349525,
                'oldest_item_timestamp': 1690284567.123456,
                'newest_item_timestamp': 1690284599.987654,
                'cache_age_seconds': 32.863198
            }
        """
        #TODO 🚧 В разработке: 23.08.2025 - мертвый код get_stats думаю как применить
        total_requests = self._hits + self._misses

        # Расчет временных метрик
        oldest_timestamp = None
        newest_timestamp = None

        if self._cache:
            timestamps = [data['timestamp'] for data in self._cache.values()]
            oldest_timestamp = min(timestamps)
            newest_timestamp = max(timestamps)

        stats = {
            'total_items': len(self._cache),
            'total_size': self._current_size,
            'max_size': self._max_size,
            'memory_usage_percent': (self._current_size / self._max_size * 100) if self._max_size > 0 else 0,
            'hits': self._hits,
            'misses': self._misses,
            'total_requests': total_requests,
            'hit_ratio': self._hits / total_requests if total_requests > 0 else 0,
            'miss_ratio': self._misses / total_requests if total_requests > 0 else 0,
            'average_item_size': self._current_size / len(self._cache) if self._cache else 0,
            'oldest_item_timestamp': oldest_timestamp,
            'newest_item_timestamp': newest_timestamp,
            'cache_age_seconds': (time.time() - oldest_timestamp) if oldest_timestamp else None
        }

        return stats