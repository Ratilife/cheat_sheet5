"""
Модульные тесты для TreeModelManager.

Тестирует функциональность управления моделью дерева файлов:
- Создание моделей для вкладок
- Добавление файлов в вкладки
- Обновление файлов в моделях
- Управление связями файл-вкладка
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
from PySide6.QtCore import QModelIndex
from PySide6.QtWidgets import QTabWidget
from managers.tree_model_manager import TreeModelManager
from src.parsers.file_parser_service import FileParserService
from src.parsers.metadata_cache import MetadataCache
from src.parsers.content_cache import ContentCache


class TestTreeModelManager(unittest.TestCase):
    """Тесты для класса TreeModelManager."""

    def setUp(self):
        """Настройка тестового окружения."""
        self.parser_service = Mock(spec=FileParserService)
        self.metadata_cache = Mock(spec=MetadataCache)
        self.content_cache = Mock(spec=ContentCache)
        self.tab_widget = Mock(spec=QTabWidget)
        
        self.manager = TreeModelManager(
            parser_service=self.parser_service,
            metadata_cache=self.metadata_cache,
            content_cache=self.content_cache,
            tab_widget=self.tab_widget
        )

    def test_manager_initialization(self):
        """Тест инициализации менеджера."""
        # Assert
        self.assertIsNotNone(self.manager.parser_service, 
                            "Parser service должен быть установлен")
        self.assertIsNotNone(self.manager.metadata_cache, 
                            "Metadata cache должен быть установлен")
        self.assertIsNotNone(self.manager.content_cache, 
                            "Content cache должен быть установлен")
        self.assertEqual(len(self.manager._tab_models), 0, 
                        "Изначально не должно быть моделей")
        self.assertEqual(len(self.manager._file_to_tabs), 0, 
                        "Изначально не должно быть связей файл-вкладка")

    def test_build_model_for_tab(self):
        """Тест создания модели для вкладки."""
        # Arrange
        tab_name = "TestTab"
        file_paths = ["/test/file1.st", "/test/file2.st"]
        
        # Настраиваем моки
        parsed_data1 = {'root_name': 'File1', 'structure': []}
        parsed_data2 = {'root_name': 'File2', 'structure': []}
        
        def get_file_data_side_effect(file_path):
            if file_path == file_paths[0]:
                return parsed_data1
            elif file_path == file_paths[1]:
                return parsed_data2
            return None
        
        self.manager._get_file_data = Mock(side_effect=get_file_data_side_effect)

        # Act
        model = self.manager.build_model_for_tab(tab_name, file_paths)

        # Assert
        self.assertIsNotNone(model, "Модель должна быть создана")
        self.assertIn(tab_name, self.manager._tab_models, 
                     "Модель должна быть сохранена в _tab_models")
        self.assertEqual(self.manager._tab_models[tab_name], model, 
                        "Сохраненная модель должна совпадать")
        
        # Проверяем связи файл-вкладка
        for file_path in file_paths:
            self.assertIn(file_path, self.manager._file_to_tabs, 
                         f"Файл {file_path} должен быть в _file_to_tabs")
            self.assertIn(tab_name, self.manager._file_to_tabs[file_path], 
                         f"Вкладка должна быть связана с файлом {file_path}")

    def test_add_files_to_tab(self):
        """Тест добавления файлов в существующую вкладку."""
        # Arrange
        tab_name = "TestTab"
        file_paths = ["/test/file1.st", "/test/file2.st"]
        
        # Создаем модель для вкладки
        model = self.manager.build_model_for_tab(tab_name, [])
        
        # Настраиваем моки для добавления файлов
        parsed_data1 = {'root_name': 'File1', 'structure': []}
        parsed_data2 = {'root_name': 'File2', 'structure': []}
        
        def get_file_data_side_effect(file_path):
            if file_path == file_paths[0]:
                return parsed_data1
            elif file_path == file_paths[1]:
                return parsed_data2
            return None
        
        self.manager._get_file_data = Mock(side_effect=get_file_data_side_effect)

        # Act
        result = self.manager.add_files_to_tab(tab_name, file_paths)

        # Assert
        self.assertTrue(result, "Добавление должно быть успешным")
        self.assertEqual(model.rowCount(), 2, 
                        "В модели должно быть 2 файла")

    def test_add_files_to_nonexistent_tab(self):
        """Тест добавления файлов в несуществующую вкладку."""
        # Arrange
        tab_name = "NonexistentTab"
        file_paths = ["/test/file1.st"]

        # Act
        result = self.manager.add_files_to_tab(tab_name, file_paths)

        # Assert
        self.assertFalse(result, "Добавление должно вернуть False")

    def test_get_model(self):
        """Тест получения модели."""
        # Arrange
        tab_name = "TestTab"
        model = self.manager.build_model_for_tab(tab_name, [])

        # Act: Получаем модель по имени вкладки
        retrieved_model = self.manager.get_model(tab_name)

        # Assert
        self.assertEqual(retrieved_model, model, 
                        "Полученная модель должна совпадать")

    def test_get_model_all_models(self):
        """Тест получения всех моделей."""
        # Arrange
        model1 = self.manager.build_model_for_tab("Tab1", [])
        model2 = self.manager.build_model_for_tab("Tab2", [])

        # Act
        all_models = self.manager.get_model()

        # Assert
        self.assertIsInstance(all_models, dict, "Должен быть возвращен словарь")
        self.assertEqual(len(all_models), 2, "Должно быть 2 модели")
        self.assertIn("Tab1", all_models)
        self.assertIn("Tab2", all_models)

    def test_get_tabs_for_file(self):
        """Тест получения вкладок для файла."""
        # Arrange
        file_path = "/test/file.st"
        tab1 = "Tab1"
        tab2 = "Tab2"
        
        self.manager.build_model_for_tab(tab1, [file_path])
        self.manager.build_model_for_tab(tab2, [file_path])

        # Act
        tabs = self.manager.get_tabs_for_file(file_path)

        # Assert
        self.assertEqual(len(tabs), 2, "Должно быть 2 вкладки")
        self.assertIn(tab1, tabs)
        self.assertIn(tab2, tabs)

    def test_get_tabs_for_nonexistent_file(self):
        """Тест получения вкладок для несуществующего файла."""
        # Arrange
        file_path = "/test/nonexistent.st"

        # Act
        tabs = self.manager.get_tabs_for_file(file_path)

        # Assert
        self.assertEqual(len(tabs), 0, "Должен быть пустой список")

    def test_update_file_in_tabs(self):
        """Тест обновления файла во вкладках."""
        # Arrange
        file_path = "/test/file.st"
        tab_name = "TestTab"
        
        # Создаем модель и добавляем файл
        parsed_data = {'root_name': 'File', 'structure': []}
        self.manager._get_file_data = Mock(return_value=parsed_data)
        model = self.manager.build_model_for_tab(tab_name, [file_path])
        
        # Настраиваем мок для обновления
        updated_data = {'root_name': 'UpdatedFile', 'structure': []}
        self.content_cache.get.return_value = updated_data

        # Act
        result = self.manager.update_file_in_tabs(file_path)

        # Assert
        self.assertTrue(result, "Обновление должно быть успешным")
        self.content_cache.get.assert_called_with(file_path)

    def test_update_file_in_tabs_nonexistent_file(self):
        """Тест обновления несуществующего файла."""
        # Arrange
        file_path = "/test/nonexistent.st"

        # Act
        result = self.manager.update_file_in_tabs(file_path)

        # Assert
        self.assertFalse(result, "Обновление должно вернуть False")

    def test_set_get_tab_widget(self):
        """Тест установки и получения виджета вкладок."""
        # Arrange
        new_tab_widget = Mock(spec=QTabWidget)

        # Act
        self.manager.set_tab_widget(new_tab_widget)
        retrieved_widget = self.manager.get_tab_widget()

        # Assert
        self.assertEqual(retrieved_widget, new_tab_widget, 
                        "Полученный виджет должен совпадать")

    def test_get_active_tab_name(self):
        """Тест получения имени активной вкладки."""
        # Arrange
        self.tab_widget.count.return_value = 2
        self.tab_widget.currentIndex.return_value = 1
        self.tab_widget.tabText.return_value = "ActiveTab"

        # Act
        active_tab = self.manager.get_active_tab_name()

        # Assert
        self.assertEqual(active_tab, "ActiveTab", 
                        "Имя активной вкладки должно совпадать")

    def test_get_active_tab_name_no_tabs(self):
        """Тест получения активной вкладки, когда вкладок нет."""
        # Arrange
        self.tab_widget.count.return_value = 0

        # Act
        active_tab = self.manager.get_active_tab_name()

        # Assert
        self.assertIsNone(active_tab, "Должен вернуться None")

    def test_get_file_data_from_cache(self):
        """Тест получения данных файла из кэша."""
        # Arrange
        file_path = "/test/file.st"
        cached_data = {'root_name': 'File', 'structure': []}
        self.content_cache.get.return_value = cached_data

        # Act
        result = self.manager._get_file_data(file_path)

        # Assert
        self.assertEqual(result, cached_data, "Данные должны быть из кэша")
        self.content_cache.get.assert_called_once_with(file_path)

    def test_get_file_data_from_metadata_cache(self):
        """Тест получения данных файла из метаданных, если нет в кэше."""
        # Arrange
        file_path = "/test/file.st"
        metadata = {'root_name': 'File', 'structure': []}
        
        self.content_cache.get.return_value = None
        self.metadata_cache.get.return_value = {'metadata': metadata}

        # Act
        result = self.manager._get_file_data(file_path)

        # Assert
        self.assertEqual(result, metadata, "Данные должны быть из метаданных")
        self.metadata_cache.get.assert_called_once_with(file_path)

    def test_multiple_tabs_same_file(self):
        """Тест работы с несколькими вкладками, содержащими один файл."""
        # Arrange
        file_path = "/test/file.st"
        tab1 = "Tab1"
        tab2 = "Tab2"
        tab3 = "Tab3"
        
        parsed_data = {'root_name': 'File', 'structure': []}
        self.manager._get_file_data = Mock(return_value=parsed_data)

        # Act
        self.manager.build_model_for_tab(tab1, [file_path])
        self.manager.build_model_for_tab(tab2, [file_path])
        self.manager.build_model_for_tab(tab3, [file_path])

        # Assert
        tabs = self.manager.get_tabs_for_file(file_path)
        self.assertEqual(len(tabs), 3, "Должно быть 3 вкладки с этим файлом")
        self.assertIn(tab1, tabs)
        self.assertIn(tab2, tabs)
        self.assertIn(tab3, tabs)


if __name__ == '__main__':
    unittest.main()

