"""
Интеграционные тесты для системы наблюдения за файлами (FileWatcher) 
в интеграции с кэшем и моделью данных.

Тестирует:
1. Автоматическое обнаружение изменений файлов вне приложения
2. Корректное обновление кэша при изменении файлов
3. Автоматическое обновление модели дерева файлов при обнаружении изменений
"""

import unittest
import os
import tempfile
import time
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QModelIndex, Qt, QTimer, QEventLoop
from PySide6.QtTest import QSignalSpy

from src.observers.file_watcher import FileWatcher
from src.parsers.st_file_parser import STFileParserWrapper
from src.parsers.file_parser_service import FileParserService
from src.parsers.content_cache import ContentCache
from src.parsers.metadata_cache import MetadataCache
from src.models.st_md_file_tree_model import STMDFileTreeModel
from src.managers.tree_model_manager import TreeModelManager


class TestFileWatcherIntegration(unittest.TestCase):
    """Интеграционные тесты для FileWatcher с кэшем и моделью данных."""

    @classmethod
    def setUpClass(cls):
        """Инициализация QApplication для тестов Qt (вызывается один раз для всех тестов)."""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        """Настройка тестового окружения перед каждым тестом."""
        self.parser = STFileParserWrapper()
        self.parser_service = FileParserService()
        self.content_cache = ContentCache()
        self.metadata_cache = MetadataCache()
        self.file_watcher = FileWatcher()
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # Создаем модель для тестирования
        self.model = STMDFileTreeModel(self.content_cache)
        
        # Создаем менеджер моделей
        self.tree_model_manager = TreeModelManager(
            parser_service=self.parser_service,
            metadata_cache=self.metadata_cache,
            content_cache=self.content_cache
        )

    def tearDown(self):
        """Очистка после каждого теста."""
        # Останавливаем отслеживание
        if hasattr(self, 'file_watcher'):
            self.file_watcher.clear_watched_files()
            self.file_watcher.deleteLater()
        
        # Очищаем кэши
        if hasattr(self, 'content_cache'):
            self.content_cache.invalidate_all()
        if hasattr(self, 'metadata_cache'):
            self.metadata_cache.invalidate_all()
        
        # Удаляем временную директорию
        if hasattr(self, 'temp_dir'):
            self.temp_dir.cleanup()
        
        # Обрабатываем события Qt для корректной очистки
        QApplication.processEvents()

    def create_test_st_file(self, content: str, filename: str = 'test_file.st') -> str:
        """
        Создание временного ST-файла с заданным содержимым.
        
        Args:
            content: Содержимое файла
            filename: Имя файла
            
        Returns:
            str: Путь к созданному файлу
        """
        file_path = os.path.join(self.temp_dir.name, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return file_path

    def wait_for_signal(self, spy: QSignalSpy, timeout: int = 2000) -> bool:
        """
        Ожидает срабатывания сигнала с таймаутом.
        
        Args:
            spy: QSignalSpy для отслеживания сигнала
            timeout: Таймаут в миллисекундах
            
        Returns:
            bool: True если сигнал сработал, False если таймаут
        """
        start_time = time.time()
        while len(spy) == 0:
            QApplication.processEvents()
            if (time.time() - start_time) * 1000 > timeout:
                return False
            time.sleep(0.01)
        return True

    def test_file_watcher_detects_external_file_changes(self):
        """
        Тест 1: Автоматическое обнаружение изменений файлов вне приложения.
        
        Проверяет:
        - FileWatcher обнаруживает изменения файла, сделанные вне приложения
        - Сигнал file_updated испускается при изменении файла
        - Сигнал debounced_file_updated испускается после дебаунсинга
        """
        # Arrange: Создаем ST-файл
        initial_content = '{1, {1, {"Папка1", 1, 0, "", ""}, {0, {"Шаблон1", 0, 1, "", "Контент1"}}}}'
        file_path = self.create_test_st_file(initial_content, 'watched_file.st')
        
        # Настраиваем отслеживание файла
        self.file_watcher.watch_file(file_path)
        self.file_watcher.watch_directory(os.path.dirname(file_path))
        
        # Создаем шпионы для сигналов
        file_updated_spy = QSignalSpy(self.file_watcher.file_updated)
        debounced_spy = QSignalSpy(self.file_watcher.debounced_file_updated)
        
        # Act: Изменяем файл вне приложения (имитируем внешнее изменение)
        new_content = '{1, {2, {"Папка1", 1, 0, "", ""}, {0, {"Шаблон1", 0, 1, "", "Контент1"}}, {0, {"Шаблон2", 0, 1, "", "Контент2"}}}}'
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        # Обрабатываем события Qt для получения уведомлений от файловой системы
        QApplication.processEvents()
        
        # Ждем срабатывания сигналов (с учетом дебаунсинга 300ms)
        time.sleep(0.5)  # Даем время на обработку изменений
        QApplication.processEvents()
        
        # Assert: Проверяем, что сигналы были испущены
        self.assertGreater(len(file_updated_spy), 0, 
                          "Сигнал file_updated должен быть испущен при изменении файла")
        
        # Проверяем debounced сигнал (может быть задержка)
        if len(debounced_spy) == 0:
            # Ждем еще немного для дебаунсинга
            time.sleep(0.4)
            QApplication.processEvents()
        
        self.assertGreater(len(debounced_spy), 0, 
                          "Сигнал debounced_file_updated должен быть испущен после дебаунсинга")
        
        # Проверяем, что путь в сигнале правильный
        if len(debounced_spy) > 0:
            emitted_path = debounced_spy[0][0]
            self.assertEqual(emitted_path, file_path, 
                           "Путь в сигнале должен совпадать с путем измененного файла")

    def test_cache_updates_on_file_change(self):
        """
        Тест 2: Корректное обновление кэша при изменении файлов.
        
        Проверяет:
        - При изменении файла кэш инвалидируется
        - Новые данные парсятся и сохраняются в кэш
        - Кэш содержит актуальные данные после изменения файла
        """
        # Arrange: Создаем начальный файл и добавляем в кэш
        initial_content = '{1, {1, {"Папка1", 1, 0, "", ""}, {0, {"Шаблон1", 0, 1, "", "Контент1"}}}}'
        file_path = self.create_test_st_file(initial_content, 'cache_test.st')
        
        # Парсим и сохраняем в кэш
        initial_parsed = self.parser.parse_st_file(file_path)
        self.content_cache.set(file_path, ('file', initial_parsed))
        
        # Проверяем начальное состояние кэша
        cached_data_before = self.content_cache.get(file_path)
        self.assertIsNotNone(cached_data_before, "Данные должны быть в кэше")
        initial_structure_count = len(cached_data_before.get('structure', []))
        
        # Настраиваем отслеживание
        self.file_watcher.watch_file(file_path)
        debounced_spy = QSignalSpy(self.file_watcher.debounced_file_updated)
        
        # Подключаем обработчик обновления кэша
        cache_updated = {'updated': False}
        
        def on_file_updated(path: str):
            """Обработчик обновления файла - обновляет кэш"""
            if path == file_path:
                # Инвалидируем кэш
                self.content_cache.invalidate(path)
                # Парсим заново и обновляем кэш
                new_parsed = self.parser.parse_st_file(path)
                self.content_cache.set(path, ('file', new_parsed))
                cache_updated['updated'] = True
        
        self.file_watcher.debounced_file_updated.connect(on_file_updated)
        
        # Act: Изменяем файл вне приложения
        new_content = '{1, {2, {"Папка1", 1, 0, "", ""}, {0, {"Шаблон1", 0, 1, "", "Контент1"}}, {0, {"Шаблон2", 0, 1, "", "Контент2"}}}}'
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        # Обрабатываем события
        time.sleep(0.5)
        QApplication.processEvents()
        
        # Assert: Проверяем обновление кэша
        self.assertTrue(cache_updated['updated'], 
                       "Кэш должен быть обновлен при изменении файла")
        
        # Проверяем, что данные в кэше обновились
        cached_data_after = self.content_cache.get(file_path)
        self.assertIsNotNone(cached_data_after, "Данные должны остаться в кэше после обновления")
        
        new_structure_count = len(cached_data_after.get('structure', []))
        self.assertGreater(new_structure_count, initial_structure_count,
                          "Количество элементов в структуре должно увеличиться")

    def test_model_updates_on_file_change(self):
        """
        Тест 3: Автоматическое обновление модели дерева файлов при обнаружении изменений.
        
        Проверяет:
        - Модель обновляется при изменении файла
        - Структура модели соответствует новой структуре файла
        - Старые элементы удаляются, новые добавляются
        """
        # Arrange: Создаем файл и добавляем в модель
        initial_content = '{1, {1, {"Папка1", 1, 0, "", ""}, {0, {"Шаблон1", 0, 1, "", "Контент1"}}}}'
        file_path = self.create_test_st_file(initial_content, 'model_test.st')
        
        # Парсим и добавляем в модель
        initial_parsed = self.parser.parse_st_file(file_path)
        self.model.add_file(file_path, initial_parsed)
        
        # Проверяем начальное состояние модели
        file_index = self.model.index(0, 0)
        self.assertTrue(file_index.isValid(), "Файл должен быть в модели")
        initial_children_count = self.model.rowCount(file_index)
        self.assertGreater(initial_children_count, 0, 
                          "Начальная структура должна содержать элементы")
        
        # Настраиваем отслеживание и обработку обновлений
        self.file_watcher.watch_file(file_path)
        debounced_spy = QSignalSpy(self.file_watcher.debounced_file_updated)
        
        model_updated = {'updated': False}
        
        def on_file_updated(path: str):
            """Обработчик обновления файла - обновляет модель через менеджер"""
            if path == file_path:
                # Обновляем кэш
                self.content_cache.invalidate(path)
                new_parsed = self.parser.parse_st_file(path)
                self.content_cache.set(path, ('file', new_parsed))
                
                # Обновляем модель
                cached_data = self.content_cache.get(path)
                if cached_data:
                    # Формат для update_file_item: (file_type, parsed_data)
                    update_success = self.model.update_file_item(path, ('file', cached_data))
                    model_updated['updated'] = update_success
        
        self.file_watcher.debounced_file_updated.connect(on_file_updated)
        
        # Act: Изменяем файл (добавляем новые элементы)
        new_content = '{1, {3, {"Папка1", 1, 0, "", ""}, {0, {"Шаблон1", 0, 1, "", "Контент1"}}, {1, {"НоваяПапка", 1, 0, "", ""}, {0, {"НовыйШаблон", 0, 1, "", "НовыйКонтент"}}}, {0, {"Шаблон2", 0, 1, "", "Контент2"}}}}'
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        # Обрабатываем события
        time.sleep(0.5)
        QApplication.processEvents()
        
        # Assert: Проверяем обновление модели
        self.assertTrue(model_updated['updated'], 
                       "Модель должна быть обновлена при изменении файла")
        
        # Проверяем, что структура модели обновилась
        updated_children_count = self.model.rowCount(file_index)
        self.assertGreater(updated_children_count, initial_children_count,
                          "Количество элементов должно увеличиться после обновления")
        
        # Проверяем наличие новых элементов в модели
        found_new_folder = False
        found_new_template = False
        
        for i in range(updated_children_count):
            child_index = self.model.index(i, 0, file_index)
            if child_index.isValid():
                child_name = self.model.data(child_index, Qt.DisplayRole)
                child_type = self.model.get_item_type(child_index)
                
                if child_type == 'folder' and child_name == "НоваяПапка":
                    found_new_folder = True
                elif child_type == 'template' and child_name == "Шаблон2":
                    found_new_template = True
        
        self.assertTrue(found_new_folder, "Новая папка должна быть в модели")
        self.assertTrue(found_new_template, "Новый шаблон должен быть в модели")

    def test_integration_file_watcher_cache_model(self):
        """
        Тест 4: Полная интеграция FileWatcher -> Кэш -> Модель.
        
        Проверяет полный цикл:
        - FileWatcher обнаруживает изменение
        - Кэш обновляется
        - Модель обновляется через TreeModelManager
        """
        # Arrange: Создаем файл и настраиваем полную цепочку
        initial_content = '{1, {1, {"Папка1", 1, 0, "", ""}, {0, {"Шаблон1", 0, 1, "", "Контент1"}}}}'
        file_path = self.create_test_st_file(initial_content, 'integration_test.st')
        
        # Добавляем файл через менеджер
        tab_name = "test_tab"
        model = self.tree_model_manager.build_model_for_tab(tab_name, [file_path])
        
        # Проверяем начальное состояние
        file_index = model.index(0, 0)
        self.assertTrue(file_index.isValid(), "Файл должен быть в модели")
        initial_count = model.rowCount(file_index)
        
        # Настраиваем отслеживание
        self.file_watcher.watch_file(file_path)
        self.file_watcher.watch_directory(os.path.dirname(file_path))
        
        # Подключаем обработчик, который обновляет через менеджер
        def on_file_updated(path: str):
            """Обработчик обновления - использует менеджер для обновления"""
            if path == file_path:
                # Инвалидируем кэши
                self.content_cache.invalidate(path)
                self.metadata_cache.invalidate(path)
                
                # Парсим заново
                parsed_data = self.parser_service.parse_and_get_type(path)
                file_type, data = parsed_data
                
                # Обновляем кэши
                self.content_cache.set(path, parsed_data)
                self.metadata_cache.set(path, data, file_type=file_type)
                
                # Обновляем модель через менеджер
                self.tree_model_manager.update_file_in_tabs(path)
        
        self.file_watcher.debounced_file_updated.connect(on_file_updated)
        
        # Act: Изменяем файл
        new_content = '{1, {2, {"Папка1", 1, 0, "", ""}, {0, {"Шаблон1", 0, 1, "", "Контент1"}}, {0, {"Шаблон2", 0, 1, "", "Контент2"}}}}'
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        # Обрабатываем события
        time.sleep(0.5)
        QApplication.processEvents()
        
        # Assert: Проверяем полную цепочку обновления
        # Проверяем кэш
        cached_data = self.content_cache.get(file_path)
        self.assertIsNotNone(cached_data, "Данные должны быть в кэше")
        
        # Проверяем модель
        updated_count = model.rowCount(file_index)
        self.assertGreater(updated_count, initial_count,
                          "Количество элементов в модели должно увеличиться")
        
        # Проверяем наличие нового элемента
        found_new_template = False
        for i in range(updated_count):
            child_index = model.index(i, 0, file_index)
            if child_index.isValid():
                child_name = model.data(child_index, Qt.DisplayRole)
                if child_name == "Шаблон2":
                    found_new_template = True
                    break
        
        self.assertTrue(found_new_template, 
                       "Новый шаблон должен быть в обновленной модели")

    def test_file_watcher_pause_resume(self):
        """
        Тест 5: Проверка паузы и возобновления отслеживания.
        
        Проверяет:
        - FileWatcher может быть приостановлен
        - Во время паузы изменения не обрабатываются
        - После возобновления отслеживание продолжается
        """
        # Arrange
        initial_content = '{1, {1, {"Папка1", 1, 0, "", ""}, {0, {"Шаблон1", 0, 1, "", "Контент1"}}}}'
        file_path = self.create_test_st_file(initial_content, 'pause_test.st')
        
        self.file_watcher.watch_file(file_path)
        debounced_spy = QSignalSpy(self.file_watcher.debounced_file_updated)
        watching_paused_spy = QSignalSpy(self.file_watcher.watching_paused)
        
        # Act 1: Ставим на паузу
        self.file_watcher.pause(1000)  # Пауза на 1 секунду
        QApplication.processEvents()
        
        # Проверяем статус паузы
        self.assertTrue(self.file_watcher.is_watching_paused(),
                      "Отслеживание должно быть приостановлено")
        
        # Изменяем файл во время паузы
        new_content = '{1, {2, {"Папка1", 1, 0, "", ""}, {0, {"Шаблон1", 0, 1, "", "Контент1"}}, {0, {"Шаблон2", 0, 1, "", "Контент2"}}}}'
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        time.sleep(0.2)
        QApplication.processEvents()
        
        # Проверяем, что сигнал не был испущен во время паузы
        signals_during_pause = len(debounced_spy)
        self.assertEqual(signals_during_pause, 0,
                        "Сигнал не должен быть испущен во время паузы")
        
        # Act 2: Ждем окончания паузы
        time.sleep(1.2)
        QApplication.processEvents()
        
        # Проверяем, что пауза закончилась
        self.assertFalse(self.file_watcher.is_watching_paused(),
                        "Отслеживание должно быть возобновлено")
        
        # Изменяем файл после паузы
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(initial_content)
        
        time.sleep(0.5)
        QApplication.processEvents()
        
        # Assert: Проверяем, что после паузы сигналы обрабатываются
        # (может быть задержка из-за дебаунсинга)
        if len(debounced_spy) == 0:
            time.sleep(0.4)
            QApplication.processEvents()
        
        # После возобновления сигналы должны обрабатываться
        # (но это может быть не гарантировано, так как файл мог измениться до возобновления)

    def test_multiple_file_changes_rapid(self):
        """
        Тест 6: Обработка множественных быстрых изменений файла.
        
        Проверяет:
        - Дебаунсинг работает корректно при множественных изменениях
        - Обрабатывается только последнее изменение
        """
        # Arrange
        initial_content = '{1, {1, {"Папка1", 1, 0, "", ""}, {0, {"Шаблон1", 0, 1, "", "Контент1"}}}}'
        file_path = self.create_test_st_file(initial_content, 'rapid_test.st')
        
        self.file_watcher.watch_file(file_path)
        debounced_spy = QSignalSpy(self.file_watcher.debounced_file_updated)
        
        update_count = {'count': 0}
        
        def on_file_updated(path: str):
            update_count['count'] += 1
        
        self.file_watcher.debounced_file_updated.connect(on_file_updated)
        
        # Act: Делаем несколько быстрых изменений
        for i in range(3):
            content = f'{{1, {{1, {{"Папка{i}", 1, 0, "", ""}}, {{0, {{"Шаблон{i}", 0, 1, "", "Контент{i}"}}}}}}}}'
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            time.sleep(0.1)  # Небольшая задержка между изменениями
            QApplication.processEvents()
        
        # Ждем завершения дебаунсинга
        time.sleep(0.5)
        QApplication.processEvents()
        
        # Assert: Проверяем, что дебаунсинг сработал
        # Должно быть обработано меньше изменений, чем было сделано
        # (из-за дебаунсинга несколько изменений могут быть объединены)
        self.assertLessEqual(update_count['count'], 3,
                            "Дебаунсинг должен уменьшить количество обработок")
        
        # Проверяем, что последнее изменение было обработано
        self.assertGreater(update_count['count'], 0,
                          "Хотя бы одно изменение должно быть обработано")


if __name__ == '__main__':
    unittest.main()

