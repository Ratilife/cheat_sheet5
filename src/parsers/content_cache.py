import sys
import time
import threading
from typing import Optional, Dict, Any
from collections import OrderedDict
class ContentCache:
    # ✅ Реализовано: 23.08.2025
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

    def remove(self, file_path: str) -> None:
        """Удаляет файл из кэша"""
        if file_path in self._cache:
            del self._cache[file_path]

    def find_point_selection_old(self, selection_info: dict):
        print(f'зашли в метод find_point_selection')
        print(f'словарь {selection_info}')
        file_path = str(selection_info['path'])
        print(file_path)
        with self._lock:
            if not isinstance(file_path, str):
                raise TypeError("file_path должен быть строкой")

            if file_path not in self._cache:
                self._misses += 1
                return None

            # Получаем данные и обновляем позицию в LRU (перемещаем в конец)
            data = self._cache.pop(file_path)
            self._cache[file_path] = data  # ⬅️ Важно! Возвращаем обратно для LRU
            self._hits += 1
            data['access_count'] += 1

        content_data = data['content']
        print(f'data: {data}')
        print(f'content_data: {content_data}')

        # ✅ ИСПРАВЛЕНИЕ: проверяем тип данных и правильно извлекаем структуру
        if isinstance(content_data, tuple) and len(content_data) == 2:
            # Это кортеж: ('file', {'structure': [...], 'root_name': '...'})
            structure_data = content_data[1]  # берем второй элемент (словарь)
            structure_list = structure_data.get('structure', [])
            #structure_list = structure_data.get()
            print(f'✅ Извлекли структуру из кортежа')
        elif isinstance(content_data, dict):
            # Это словарь: {'structure': [...], 'root_name': '...'}
            structure_list = content_data.get('structure', [])
            print(f'✅ Извлекли структуру из словаря')
        else:
            print(f'❌ Неизвестный формат данных: {type(content_data)}')
            return None

        print(f'😊 Структура: {structure_list}')
        print(f'тип объекта {selection_info["type"]}')

        if selection_info['type'] == 'folder':
            print(f'📂Зашли в {selection_info["type"]}')
            # Ищем папку с таким же именем и уровнем
            target_folder = self.find_folder_by_name(structure_list, selection_info['name'])
            print(f'target_folder = {target_folder}')
            if target_folder:
                print(f'🟣Вставляем внутрь папки{target_folder.get("children", [])}')
                return target_folder.get('children', [])  # вставляем внутрь папки
        if selection_info['type'] == 'file':
            print('📝Зашли в file')
            # Вставляем в корень
            print(f'🟠Вставляем в корень{structure_list}')
            return structure_list
        if selection_info['type'] == 'template':
            print(f'🧾Зашли в {selection_info["type"]}')
            # Нужно найти родителя шаблона и добавить в его дочерние элементы
            target_template = self.find_folder_by_name(structure_list, selection_info['parent_name'])
            if target_template:
                print(f'🔵 Вставляем в шаблон {target_template.get("children", [])}')
                return target_template.get("children", [])
        return None

    def find_point_selection(self, selection_info: dict)-> (Optional[tuple[str, list, list, str]]
                                                            | Optional[tuple[str, list, str]]):
        # TODO 🚧 В разработке: 17.10.2025
        print(f'зашли в метод find_point_selection')
        print(f'словарь {selection_info}')
        file_path = str(selection_info['path'])
        print(file_path)

        # Инициализируем переменные заранее
        structure_data = None
        structure_list = None

        with self._lock:
            if not isinstance(file_path, str):
                raise TypeError("file_path должен быть строкой")

            if file_path not in self._cache:
                self._misses += 1
                return None

            # Получаем данные и обновляем позицию в LRU (перемещаем в конец)
            data = self._cache.pop(file_path)
            self._cache[file_path] = data  # ⬅️ Важно! Возвращаем обратно для LRU
            self._hits += 1
            data['access_count'] += 1

        content_data = data['content']
        print(f'данные из кэш data: {data}')
        print(f'content_data: {content_data}')

        # ✅ ИСПРАВЛЕНИЕ: проверяем тип данных и правильно извлекаем структуру
        if isinstance(content_data, tuple) and len(content_data) == 2:
            # Это кортеж: ('file', {'structure': [...], 'root_name': '...'})
            structure_data = content_data[1]  # берем второй элемент (словарь)
            print(f'🍆 structure_data: {structure_data}')
            structure_list = structure_data.get('structure', [])
            # structure_list = structure_data.get()
            print(f'✅ Извлекли структуру из кортежа')
        elif isinstance(content_data, dict):
            # Это словарь: {'structure': [...], 'root_name': '...'}
            structure_list = content_data.get('structure', [])
            print(f'✅ Извлекли структуру из словаря')
        else:
            print(f'❌ Неизвестный формат данных: {type(content_data)}')
            return None

        print(f'😊 Структура: {structure_list}')
        print(f'тип объекта {selection_info["type"]}')

        if selection_info['type'] == 'folder':
            print(f'📂Зашли в {selection_info["type"]}')
            # Ищем папку с таким же именем и уровнем
            target_folder = self.find_folder_by_name(structure_list, selection_info['name'])
            print(f'target_folder = {target_folder}')
            if target_folder:
                print(f'🟣Вставляем внутрь папки{target_folder.get("children", [])}')
                return selection_info['name'], structure_data, target_folder, 'folder'
                #return structure_list, target_folder.get('children', []), 'folder'  # вставляем внутрь папки
        if selection_info['type'] == 'file':
            print('📝Зашли в file')
            # Вставляем в корень
            print(f'🟠Вставляем в корень{structure_list}')

            return selection_info['name'], structure_data, 'file'
        if selection_info['type'] == 'template':
            print(f'🧾Зашли в {selection_info["type"]}')
            # Нужно найти родителя шаблона и добавить в его дочерние элементы
            target_template = self.find_folder_by_name(structure_list, selection_info['parent_name'])
            if target_template:
                print(f'🔵 Вставляем в шаблон {target_template.get("children", [])}')

                return selection_info['name'], structure_data, target_template, 'template'
        return None


    def find_folder_by_name(self, structure_list, target_name, target_type='folder'):
        """
        Рекурсивно ищет папку по имени в структуре
        """
        # TODO 🚧 В разработке: 16.10.2025
        print(f'🔍 Поиск: "{target_name}" (тип: {target_type})')
        print(f'📁 Структура для поиска: {len(structure_list)} элементов')
        print(f'📁 Первые элементы: {[elem.get("name", "no-name") for elem in structure_list[:3]]}')

        for index, element in enumerate(structure_list):
            print(f'--- Элемент {index} ---')

            # Пропускаем элементы, которые не являются словарями
            if not isinstance(element, dict):
                print(f'❌ Пропуск: не словарь')
                continue

            current_name = element.get('name')
            current_type = element.get('type')
            print(f'📝 Имя: "{current_name}", Тип: "{current_type}"')

            # Проверяем текущий элемент
            if current_name == target_name and current_type == target_type:
                print(f'✅ НАЙДЕНО: {element}')
                return element

            # Рекурсивно ищем в детях
            if 'children' in element:
                print(f'🔍 Рекурсивный поиск в детях элемента "{current_name}"')
                found = self.find_folder_by_name(element['children'], target_name, target_type)
                if found:
                    print(f'✅ Найдено в детях: {found}')
                    return found
            else:
                print(f'📭 Нет детей у элемента "{current_name}"')

        print(f'❌ Не найдено: "{target_name}" (тип: {target_type})')
        return None

    def debug_detailed_contents(self) -> Dict[str, Any]:
        """
        Подробное содержимое кэша с полными данными.
        ВНИМАНИЕ: Может быть большим по объему!
        """
        with self._lock:
            return dict(self._cache)

    def debug_show_cache_contents(self) -> Dict[str, Any]:
        """
        Показывает всё содержимое кэша для отладки.

        Returns:
            Dict[str, Any]: Словарь со всеми элементами кэша и их метаданными
        """
        with self._lock:
            contents = {}
            for file_path, data in self._cache.items():
                contents[file_path] = {
                    'size': data['size'],
                    'timestamp': data['timestamp'],
                    'access_count': data['access_count'],
                    'content_keys': list(data['content'].keys()) if isinstance(data['content'], dict) else type(
                        data['content']),
                    'content_type': type(data['content']).__name__
                }
            return contents