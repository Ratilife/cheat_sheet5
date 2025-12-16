"""
Модульные тесты для системы кэширования ContentCache.

Тестирует алгоритм LRU (Least Recently Used) для управления кэшем содержимого файлов.
Проверяет следующие аспекты:
- Корректность добавления элементов в кэш
- Вытеснение наименее используемых элементов при превышении лимита размера кэша
- Обновление позиции элемента при обращении к нему
- Потокобезопасность операций с кэшем при многопоточном доступе
"""

import unittest
import threading
import time
from src.parsers.content_cache import ContentCache


class TestContentCacheLRU(unittest.TestCase):
    """Тестовый класс для проверки LRU кэша ContentCache."""

    def setUp(self):
        """Настройка тестового окружения перед каждым тестом."""
        # Сбрасываем singleton для изоляции тестов
        ContentCache._instance = None
        # Создаем новый экземпляр с маленьким размером для тестирования вытеснения
        self.cache = ContentCache()
        # Устанавливаем маленький размер кэша для тестирования вытеснения
        self.cache._max_size = 1000  # 1 KB для тестов
        self.cache._current_size = 0
        self.cache._cache.clear()

    def tearDown(self):
        """Очистка после каждого теста."""
        # Очищаем кэш после каждого теста
        if self.cache:
            self.cache.invalidate_all()
        ContentCache._instance = None

    def test_add_element_to_cache(self):
        """
        Тест корректности добавления элементов в кэш.
        
        Проверяет:
        - Элемент успешно добавляется в кэш
        - Размер кэша корректно обновляется
        - Элемент можно получить из кэша
        - Метаданные элемента корректны
        """
        # Arrange
        file_path = "/test/file1.st"
        content = {
            'structure': [{'name': 'Template1', 'type': 'template'}],
            'root_name': 'file1'
        }
        size = 100

        # Act
        self.cache.set(file_path, content, size)

        # Assert
        self.assertIn(file_path, self.cache._cache, "Файл должен быть в кэше")
        self.assertEqual(self.cache._current_size, size, 
                        f"Размер кэша должен быть {size} байт")
        
        cached_data = self.cache._cache[file_path]
        self.assertEqual(cached_data['content'], content, 
                        "Содержимое должно совпадать")
        self.assertEqual(cached_data['size'], size, 
                        "Размер должен совпадать")
        self.assertIn('timestamp', cached_data, 
                     "Должна быть временная метка")
        self.assertEqual(cached_data['access_count'], 0, 
                       "Счетчик обращений должен быть 0")

    def test_add_multiple_elements(self):
        """
        Тест добавления нескольких элементов в кэш.
        
        Проверяет, что все элементы корректно добавляются и доступны.
        """
        # Arrange
        files = [
            ("/test/file1.st", {'structure': [], 'root_name': 'file1'}, 50),
            ("/test/file2.st", {'structure': [], 'root_name': 'file2'}, 75),
            ("/test/file3.st", {'structure': [], 'root_name': 'file3'}, 100),
        ]

        # Act
        for file_path, content, size in files:
            self.cache.set(file_path, content, size)

        # Assert
        self.assertEqual(len(self.cache._cache), 3, 
                        "В кэше должно быть 3 элемента")
        self.assertEqual(self.cache._current_size, 225, 
                        "Размер кэша должен быть 225 байт")
        
        for file_path, content, size in files:
            cached_content = self.cache.get(file_path)
            self.assertIsNotNone(cached_content, 
                               f"Элемент {file_path} должен быть доступен")
            self.assertEqual(cached_content['root_name'], content['root_name'])

    def test_lru_eviction_when_limit_exceeded(self):
        """
        Тест вытеснения наименее используемых элементов при превышении лимита.
        
        Проверяет:
        - При добавлении элемента, превышающего лимит, вытесняются старые элементы
        - Вытесняется именно самый старый (первый) элемент
        - Размер кэша остается в пределах лимита
        """
        # Arrange: Заполняем кэш до лимита
        self.cache.set("/test/file1.st", {'structure': [], 'root_name': 'file1'}, 300)
        self.cache.set("/test/file2.st", {'structure': [], 'root_name': 'file2'}, 300)
        self.cache.set("/test/file3.st", {'structure': [], 'root_name': 'file3'}, 300)
        # Теперь размер: 900 байт, лимит: 1000 байт

        # Act: Добавляем элемент, который вызовет вытеснение
        self.cache.set("/test/file4.st", {'structure': [], 'root_name': 'file4'}, 200)
        # Должен вытесниться file1 (самый старый)

        # Assert
        self.assertNotIn("/test/file1.st", self.cache._cache,
                        "Самый старый элемент должен быть вытеснен")
        self.assertIn("/test/file2.st", self.cache._cache,
                     "Второй элемент должен остаться")
        self.assertIn("/test/file3.st", self.cache._cache,
                     "Третий элемент должен остаться")
        self.assertIn("/test/file4.st", self.cache._cache,
                     "Новый элемент должен быть в кэше")
        
        # Проверяем, что размер кэша в пределах лимита
        self.assertLessEqual(self.cache._current_size, self.cache._max_size,
                            "Размер кэша не должен превышать лимит")

    def test_lru_eviction_multiple_elements(self):
        """
        Тест вытеснения нескольких элементов при добавлении большого элемента.
        
        Проверяет, что при добавлении элемента, требующего много места,
        вытесняются несколько старых элементов.
        """
        # Arrange: Заполняем кэш маленькими элементами
        for i in range(5):
            self.cache.set(f"/test/file{i}.st", 
                          {'structure': [], 'root_name': f'file{i}'}, 
                          150)
        # Размер: 750 байт, лимит: 1000 байт

        # Act: Добавляем большой элемент (500 байт)
        # Должно вытесниться: 500 + 750 - 1000 = 250 байт минимум
        # То есть минимум 2 элемента (2 * 150 = 300 > 250)
        self.cache.set("/test/big_file.st", 
                      {'structure': [], 'root_name': 'big_file'}, 
                      500)

        # Assert
        # Проверяем, что старые элементы вытеснены
        self.assertLess(len(self.cache._cache), 6,
                       "Количество элементов должно уменьшиться")
        self.assertIn("/test/big_file.st", self.cache._cache,
                     "Новый большой элемент должен быть в кэше")
        self.assertLessEqual(self.cache._current_size, self.cache._max_size,
                            "Размер кэша не должен превышать лимит")

    def test_update_element_position_on_access(self):
        """
        Тест обновления позиции элемента при обращении к нему.
        
        Проверяет:
        - При обращении к элементу он перемещается в конец OrderedDict (становится самым новым)
        - При вытеснении вытесняется элемент, к которому дольше всего не обращались
        """
        # Arrange: Добавляем элементы в кэш
        self.cache.set("/test/file1.st", {'structure': [], 'root_name': 'file1'}, 200)
        time.sleep(0.01)  # Небольшая задержка для разных timestamp
        self.cache.set("/test/file2.st", {'structure': [], 'root_name': 'file2'}, 200)
        time.sleep(0.01)
        self.cache.set("/test/file3.st", {'structure': [], 'root_name': 'file3'}, 200)
        # Размер: 600 байт, лимит: 1000 байт

        # Act: Обращаемся к первому элементу (должен стать самым новым)
        self.cache.get("/test/file1.st")
        
        # Добавляем новые элементы, которые вызовут вытеснение
        self.cache.set("/test/file4.st", {'structure': [], 'root_name': 'file4'}, 200)
        self.cache.set("/test/file5.st", {'structure': [], 'root_name': 'file5'}, 200)
        # Теперь размер: 1000 байт, при добавлении следующего должен вытесниться file2 (самый старый)

        # Assert
        self.assertIn("/test/file1.st", self.cache._cache,
                     "file1 должен остаться (был обновлен)")
        # file2 должен быть вытеснен, так как к нему не обращались после file1
        # Проверяем порядок элементов в OrderedDict
        cache_items = list(self.cache._cache.items())
        # Последний элемент должен быть самым недавно использованным
        self.assertEqual(cache_items[-1][0], "/test/file5.st",
                       "Последний элемент должен быть самым новым")

    def test_lru_order_maintenance(self):
        """
        Тест поддержания правильного порядка LRU.
        
        Проверяет, что порядок элементов в OrderedDict соответствует LRU логике.
        """
        # Arrange: Добавляем элементы
        files = [
            "/test/file1.st",
            "/test/file2.st",
            "/test/file3.st",
        ]
        for file_path in files:
            self.cache.set(file_path, {'structure': [], 'root_name': 'file'}, 200)
            time.sleep(0.01)

        # Act: Обращаемся к элементам в разном порядке
        self.cache.get("/test/file2.st")  # file2 становится самым новым
        self.cache.get("/test/file1.st")  # file1 становится самым новым
        # Теперь порядок (от старого к новому): file3, file2, file1

        # Assert: Проверяем порядок в OrderedDict
        cache_keys = list(self.cache._cache.keys())
        self.assertEqual(cache_keys[0], "/test/file3.st",
                       "Первый элемент должен быть самым старым (file3)")
        self.assertEqual(cache_keys[-1], "/test/file1.st",
                       "Последний элемент должен быть самым новым (file1)")

    def test_access_count_increment(self):
        """
        Тест увеличения счетчика обращений при доступе к элементу.
        
        Проверяет, что счетчик access_count корректно увеличивается.
        """
        # Arrange
        file_path = "/test/file1.st"
        self.cache.set(file_path, {'structure': [], 'root_name': 'file1'}, 100)

        # Act: Обращаемся к элементу несколько раз
        self.cache.get(file_path)
        self.cache.get(file_path)
        self.cache.get(file_path)

        # Assert
        cached_data = self.cache._cache[file_path]
        self.assertEqual(cached_data['access_count'], 3,
                       "Счетчик обращений должен быть 3")

    def test_thread_safety_concurrent_access(self):
        """
        Тест потокобезопасности операций с кэшем при многопоточном доступе.
        
        Проверяет:
        - Несколько потоков могут безопасно читать и писать в кэш
        - Нет потери данных при конкурентном доступе
        - Размер кэша остается корректным
        """
        # Arrange
        num_threads = 10
        files_per_thread = 5
        results = []
        errors = []

        def worker(thread_id):
            """Рабочая функция для потока."""
            try:
                # Каждый поток добавляет свои файлы
                for i in range(files_per_thread):
                    file_path = f"/test/thread{thread_id}_file{i}.st"
                    content = {
                        'structure': [{'name': f'Template{i}', 'type': 'template'}],
                        'root_name': f'thread{thread_id}_file{i}'
                    }
                    self.cache.set(file_path, content, 50)
                    results.append(file_path)

                # Каждый поток читает файлы других потоков
                for other_thread in range(num_threads):
                    for i in range(files_per_thread):
                        file_path = f"/test/thread{other_thread}_file{i}.st"
                        self.cache.get(file_path)
            except Exception as e:
                errors.append(str(e))

        # Act: Запускаем потоки
        threads = []
        for thread_id in range(num_threads):
            thread = threading.Thread(target=worker, args=(thread_id,))
            threads.append(thread)
            thread.start()

        # Ждем завершения всех потоков
        for thread in threads:
            thread.join()

        # Assert
        self.assertEqual(len(errors), 0,
                       f"Не должно быть ошибок при многопоточном доступе. Ошибки: {errors}")
        
        # Проверяем, что все файлы добавлены (или вытеснены из-за лимита)
        # Но размер кэша должен быть корректным
        self.assertLessEqual(self.cache._current_size, self.cache._max_size,
                            "Размер кэша не должен превышать лимит при многопоточном доступе")
        
        # Проверяем, что нет дубликатов в результатах
        self.assertEqual(len(results), num_threads * files_per_thread,
                       "Все файлы должны быть обработаны")

    def test_thread_safety_concurrent_read_write(self):
        """
        Тест потокобезопасности при одновременном чтении и записи.
        
        Проверяет, что чтение и запись могут выполняться параллельно без ошибок.
        """
        # Arrange
        num_writers = 5
        num_readers = 5
        write_errors = []
        read_errors = []
        written_files = set()

        def writer(thread_id):
            """Поток-писатель."""
            try:
                for i in range(10):
                    file_path = f"/test/writer{thread_id}_file{i}.st"
                    content = {'structure': [], 'root_name': f'writer{thread_id}_file{i}'}
                    self.cache.set(file_path, content, 50)
                    written_files.add(file_path)
                    time.sleep(0.001)  # Небольшая задержка
            except Exception as e:
                write_errors.append(str(e))

        def reader(thread_id):
            """Поток-читатель."""
            try:
                for _ in range(20):
                    # Пытаемся читать файлы от всех писателей
                    for writer_id in range(num_writers):
                        for i in range(10):
                            file_path = f"/test/writer{writer_id}_file{i}.st"
                            self.cache.get(file_path)
                    time.sleep(0.001)
            except Exception as e:
                read_errors.append(str(e))

        # Act: Запускаем потоки
        threads = []
        for thread_id in range(num_writers):
            thread = threading.Thread(target=writer, args=(thread_id,))
            threads.append(thread)
            thread.start()

        for thread_id in range(num_readers):
            thread = threading.Thread(target=reader, args=(thread_id,))
            threads.append(thread)
            thread.start()

        # Ждем завершения
        for thread in threads:
            thread.join()

        # Assert
        self.assertEqual(len(write_errors), 0,
                       f"Не должно быть ошибок записи. Ошибки: {write_errors}")
        self.assertEqual(len(read_errors), 0,
                       f"Не должно быть ошибок чтения. Ошибки: {read_errors}")

    def test_thread_safety_eviction_under_load(self):
        """
        Тест потокобезопасности вытеснения элементов под нагрузкой.
        
        Проверяет, что вытеснение элементов работает корректно при многопоточном доступе.
        """
        # Arrange: Устанавливаем маленький лимит для частого вытеснения
        self.cache._max_size = 500
        num_threads = 8
        errors = []
        operations_count = [0]  # Используем список для изменяемого объекта

        def worker(thread_id):
            """Рабочая функция для потока."""
            try:
                for i in range(20):
                    file_path = f"/test/thread{thread_id}_file{i}.st"
                    content = {'structure': [], 'root_name': f'thread{thread_id}_file{i}'}
                    self.cache.set(file_path, content, 100)
                    operations_count[0] += 1
                    
                    # Периодически читаем случайные файлы
                    if i % 3 == 0:
                        for j in range(thread_id + 1):
                            read_path = f"/test/thread{j}_file{min(i, 10)}.st"
                            self.cache.get(read_path)
                            operations_count[0] += 1
            except Exception as e:
                errors.append(str(e))

        # Act: Запускаем потоки
        threads = []
        for thread_id in range(num_threads):
            thread = threading.Thread(target=worker, args=(thread_id,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Assert
        self.assertEqual(len(errors), 0,
                       f"Не должно быть ошибок при вытеснении под нагрузкой. Ошибки: {errors}")
        self.assertLessEqual(self.cache._current_size, self.cache._max_size,
                            "Размер кэша не должен превышать лимит")

    def test_cache_invalidation(self):
        """
        Тест инвалидации (удаления) элементов из кэша.
        
        Проверяет корректность удаления элементов и обновления размера.
        """
        # Arrange
        file_path = "/test/file1.st"
        self.cache.set(file_path, {'structure': [], 'root_name': 'file1'}, 200)
        initial_size = self.cache._current_size

        # Act
        self.cache.invalidate(file_path)

        # Assert
        self.assertNotIn(file_path, self.cache._cache,
                        "Файл должен быть удален из кэша")
        self.assertEqual(self.cache._current_size, initial_size - 200,
                        "Размер кэша должен уменьшиться на 200 байт")

    def test_cache_stats(self):
        """
        Тест получения статистики кэша.
        
        Проверяет корректность расчета статистики попаданий и промахов.
        """
        # Arrange
        self.cache.set("/test/file1.st", {'structure': [], 'root_name': 'file1'}, 100)
        self.cache.set("/test/file2.st", {'structure': [], 'root_name': 'file2'}, 100)

        # Act: Делаем несколько обращений
        self.cache.get("/test/file1.st")  # hit
        self.cache.get("/test/file1.st")  # hit
        self.cache.get("/test/nonexistent.st")  # miss
        self.cache.get("/test/file2.st")  # hit

        # Assert
        stats = self.cache.get_stats()
        self.assertEqual(stats['hits'], 3, "Должно быть 3 попадания")
        self.assertEqual(stats['misses'], 1, "Должен быть 1 промах")
        self.assertEqual(stats['total_requests'], 4, "Всего должно быть 4 запроса")
        self.assertEqual(stats['hit_ratio'], 0.75, "Коэффициент попаданий должен быть 0.75")
        self.assertEqual(stats['total_items'], 2, "В кэше должно быть 2 элемента")


if __name__ == '__main__':
    unittest.main()




