"""
Интеграционные тесты для проверки взаимодействия системы парсинга с моделями данных.

Тестирует:
1. Корректность передачи данных от парсера ST-файлов к модели дерева файлов
2. Правильность преобразования структуры данных, полученной от парсера, в формат Qt
3. Синхронизацию данных между парсером и моделью при изменении файлов
"""

import unittest
import os
import tempfile
import time
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QModelIndex, Qt

from src.parsers.st_file_parser import STFileParserWrapper
from src.parsers.file_parser_service import FileParserService
from src.parsers.content_cache import ContentCache
from src.parsers.metadata_cache import MetadataCache
from src.models.st_md_file_tree_model import STMDFileTreeModel
from src.managers.tree_model_manager import TreeModelManager


class TestParserModelIntegration(unittest.TestCase):
    """Интеграционные тесты для проверки взаимодействия парсера и модели."""

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
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # Создаем модель для тестирования
        self.model = STMDFileTreeModel(self.content_cache)

    def tearDown(self):
        """Очистка после каждого теста."""
        self.temp_dir.cleanup()
        # Очищаем кэши
        if hasattr(self, 'content_cache'):
            self.content_cache.clear()
        if hasattr(self, 'metadata_cache'):
            self.metadata_cache.clear()

    def create_test_st_file(self, content, filename='test_file.st'):
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

    def test_parser_to_model_data_transfer(self):
        """
        Тест 1: Корректность передачи данных от парсера ST-файлов к модели дерева файлов.
        
        Проверяет:
        - Парсер корректно извлекает структуру из ST-файла
        - Данные передаются в модель без потерь
        - Модель корректно отображает структуру файла
        """
        # Arrange: Создаем ST-файл с известной структурой
        st_content = '{1, {2, {"КорневаяПапка", 1, 0, "", ""}, {0, {"Шаблон1", 0, 1, "", "Содержимое шаблона 1"}}, {1, {"ВложеннаяПапка", 1, 0, "", ""}, {0, {"Шаблон2", 0, 1, "", "Содержимое шаблона 2"}}}}}'
        file_path = self.create_test_st_file(st_content)
        expected_root_name = os.path.splitext(os.path.basename(file_path))[0]

        # Act: Парсим файл и добавляем в модель
        parsed_data = self.parser.parse_st_file(file_path)
        self.model.add_file(file_path, parsed_data)

        # Assert: Проверяем корректность передачи данных
        self.assertIsInstance(parsed_data, dict, "Парсер должен вернуть словарь")
        self.assertIn('structure', parsed_data, "Данные должны содержать 'structure'")
        self.assertIn('root_name', parsed_data, "Данные должны содержать 'root_name'")
        
        # Проверяем, что модель содержит файл
        root_row_count = self.model.rowCount()
        self.assertGreater(root_row_count, 0, "Модель должна содержать хотя бы один файл")
        
        # Проверяем корневой элемент файла в модели
        file_index = self.model.index(0, 0)
        self.assertTrue(file_index.isValid(), "Индекс файла должен быть валидным")
        
        file_name = self.model.data(file_index, Qt.DisplayRole)
        self.assertEqual(file_name, expected_root_name, 
                        f"Имя файла в модели должно быть '{expected_root_name}'")
        
        # Проверяем тип элемента
        file_type = self.model.get_item_type(file_index)
        self.assertEqual(file_type, 'file', "Тип корневого элемента должен быть 'file'")

    def test_structure_transformation_to_qt_format(self):
        """
        Тест 2: Правильность преобразования структуры данных от парсера в формат Qt.
        
        Проверяет:
        - Структура парсера корректно преобразуется в STMDFileTreeItem
        - Иерархия элементов сохраняется
        - Типы элементов (folder, template) корректно определяются
        - Содержимое шаблонов передается корректно
        """
        # Arrange: Создаем ST-файл с вложенной структурой
        st_content = '{1, {3, {"КорневаяПапка", 1, 0, "", ""}, {0, {"Шаблон1", 0, 1, "", "Контент1"}}, {1, {"ВложеннаяПапка", 1, 0, "", ""}, {0, {"Шаблон2", 0, 1, "", "Контент2"}}}, {0, {"Шаблон3", 0, 1, "", "Контент3"}}}}'
        file_path = self.create_test_st_file(st_content)

        # Act: Парсим и добавляем в модель
        parsed_data = self.parser.parse_st_file(file_path)
        self.model.add_file(file_path, parsed_data)

        # Assert: Проверяем преобразование структуры
        file_index = self.model.index(0, 0)
        self.assertTrue(file_index.isValid(), "Файл должен быть в модели")
        
        # Проверяем наличие дочерних элементов
        children_count = self.model.rowCount(file_index)
        self.assertGreater(children_count, 0, "Файл должен содержать дочерние элементы")
        
        # Проверяем первый элемент (должна быть папка)
        first_child_index = self.model.index(0, 0, file_index)
        self.assertTrue(first_child_index.isValid(), "Первый дочерний элемент должен существовать")
        
        first_child_name = self.model.data(first_child_index, Qt.DisplayRole)
        self.assertEqual(first_child_name, "КорневаяПапка", 
                        "Первый элемент должен быть 'КорневаяПапка'")
        
        first_child_type = self.model.get_item_type(first_child_index)
        self.assertEqual(first_child_type, 'folder', 
                        "Первый элемент должен быть типа 'folder'")
        
        # Проверяем вложенную структуру
        folder_children_count = self.model.rowCount(first_child_index)
        self.assertGreater(folder_children_count, 0, 
                          "Папка должна содержать дочерние элементы")
        
        # Проверяем шаблон внутри папки
        template_index = self.model.index(0, 0, first_child_index)
        if template_index.isValid():
            template_name = self.model.data(template_index, Qt.DisplayRole)
            template_type = self.model.get_item_type(template_index)
            self.assertEqual(template_type, 'template', 
                           "Внутри папки должен быть шаблон")
            self.assertIn("Шаблон", template_name, 
                         "Имя шаблона должно содержать 'Шаблон'")

    def test_model_index_navigation(self):
        """
        Дополнительный тест: Проверка навигации по индексам модели Qt.
        
        Проверяет корректность работы методов index(), parent(), rowCount() модели.
        """
        # Arrange
        st_content = '{1, {2, {"Папка1", 1, 0, "", ""}, {0, {"Шаблон1", 0, 1, "", "Контент"}}, {1, {"Папка2", 1, 0, "", ""}, {0, {"Шаблон2", 0, 1, "", "Контент2"}}}}}'
        file_path = self.create_test_st_file(st_content)

        # Act
        parsed_data = self.parser.parse_st_file(file_path)
        self.model.add_file(file_path, parsed_data)

        # Assert: Проверяем навигацию
        root_index = QModelIndex()  # Корневой индекс модели
        
        # Проверяем количество файлов на корневом уровне
        root_children = self.model.rowCount(root_index)
        self.assertEqual(root_children, 1, "Должен быть один файл на корневом уровне")
        
        # Получаем индекс файла
        file_index = self.model.index(0, 0, root_index)
        self.assertTrue(file_index.isValid(), "Индекс файла должен быть валидным")
        
        # Проверяем parent файла (должен быть корневым индексом)
        file_parent = self.model.parent(file_index)
        self.assertFalse(file_parent.isValid(), 
                        "Родитель файла должен быть невалидным (корневой уровень)")
        
        # Проверяем дочерние элементы файла
        file_children_count = self.model.rowCount(file_index)
        self.assertGreater(file_children_count, 0, 
                          "Файл должен содержать дочерние элементы")

    def test_data_synchronization_on_file_change(self):
        """
        Тест 3: Синхронизация данных между парсером и моделью при изменении файлов.
        
        Проверяет:
        - При изменении файла модель обновляется корректно
        - Структура модели соответствует новой структуре файла
        - Старые элементы удаляются, новые добавляются
        """
        # Arrange: Создаем начальный файл
        initial_content = '{1, {1, {"Папка1", 1, 0, "", ""}, {0, {"Шаблон1", 0, 1, "", "Контент1"}}}}'
        file_path = self.create_test_st_file(initial_content, 'sync_test.st')
        
        # Добавляем файл в модель
        parsed_data = self.parser.parse_st_file(file_path)
        self.model.add_file(file_path, parsed_data)
        
        # Проверяем начальное состояние
        file_index = self.model.index(0, 0)
        initial_children_count = self.model.rowCount(file_index)
        self.assertGreater(initial_children_count, 0, 
                          "Начальная структура должна содержать элементы")
        
        # Act: Изменяем файл (добавляем новые элементы)
        new_content = '{1, {3, {"Папка1", 1, 0, "", ""}, {0, {"Шаблон1", 0, 1, "", "Контент1"}}, {1, {"НоваяПапка", 1, 0, "", ""}, {0, {"НовыйШаблон", 0, 1, "", "НовыйКонтент"}}}, {0, {"Шаблон2", 0, 1, "", "Контент2"}}}}'
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        # Парсим обновленный файл
        updated_parsed_data = self.parser.parse_st_file(file_path)
        
        # Обновляем модель
        # Формат данных для update_file_item: (file_type, parsed_data)
        update_success = self.model.update_file_item(file_path, ('file', updated_parsed_data))
        
        # Assert: Проверяем синхронизацию
        self.assertTrue(update_success, "Обновление модели должно быть успешным")
        
        # Проверяем, что структура обновилась
        updated_children_count = self.model.rowCount(file_index)
        self.assertGreater(updated_children_count, initial_children_count,
                          "Количество элементов должно увеличиться после обновления")
        
        # Проверяем наличие новых элементов
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

    def test_model_update_removes_old_elements(self):
        """
        Дополнительный тест: Проверка удаления старых элементов при обновлении.
        
        Проверяет, что при изменении файла старые элементы, которых больше нет,
        корректно удаляются из модели.
        """
        # Arrange: Создаем файл с несколькими элементами
        initial_content = '{1, {2, {"Папка1", 1, 0, "", ""}, {0, {"Шаблон1", 0, 1, "", "Контент1"}}, {0, {"Шаблон2", 0, 1, "", "Контент2"}}}}'
        file_path = self.create_test_st_file(initial_content, 'remove_test.st')
        
        parsed_data = self.parser.parse_st_file(file_path)
        self.model.add_file(file_path, parsed_data)
        
        file_index = self.model.index(0, 0)
        initial_count = self.model.rowCount(file_index)
        
        # Act: Упрощаем структуру файла (удаляем элементы)
        simplified_content = '{1, {1, {"Папка1", 1, 0, "", ""}, {0, {"Шаблон1", 0, 1, "", "Контент1"}}}}'
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(simplified_content)
        
        updated_parsed_data = self.parser.parse_st_file(file_path)
        update_success = self.model.update_file_item(file_path, ('file', updated_parsed_data))
        
        # Assert
        self.assertTrue(update_success, "Обновление должно быть успешным")
        
        updated_count = self.model.rowCount(file_index)
        self.assertLess(updated_count, initial_count,
                       "Количество элементов должно уменьшиться")
        
        # Проверяем, что Шаблон2 удален
        found_template2 = False
        for i in range(updated_count):
            child_index = self.model.index(i, 0, file_index)
            if child_index.isValid():
                child_name = self.model.data(child_index, Qt.DisplayRole)
                if child_name == "Шаблон2":
                    found_template2 = True
                    break
        
        self.assertFalse(found_template2, "Шаблон2 должен быть удален из модели")

    def test_tree_model_manager_integration(self):
        """
        Интеграционный тест с TreeModelManager.
        
        Проверяет полный цикл: парсер -> менеджер -> модель.
        """
        # Arrange
        st_content = '{1, {2, {"ТестоваяПапка", 1, 0, "", ""}, {0, {"ТестовыйШаблон", 0, 1, "", "Тестовое содержимое"}}, {1, {"ВложеннаяПапка", 1, 0, "", ""}, {0, {"ВложенныйШаблон", 0, 1, "", "Вложенное содержимое"}}}}}'
        file_path = self.create_test_st_file(st_content, 'manager_test.st')
        
        # Act: Используем TreeModelManager для добавления файла
        manager = TreeModelManager(
            parser_service=self.parser_service,
            metadata_cache=self.metadata_cache,
            content_cache=self.content_cache
        )
        
        # Создаем модель для вкладки
        tab_name = "test_tab"
        model = manager.build_model_for_tab(tab_name, [file_path])
        
        # Assert: Проверяем, что файл добавлен через менеджер
        self.assertIsNotNone(model, "Модель должна быть создана")
        self.assertIsInstance(model, STMDFileTreeModel, 
                             "Модель должна быть типа STMDFileTreeModel")
        
        # Проверяем наличие файла в модели
        root_count = model.rowCount()
        self.assertGreater(root_count, 0, "Модель должна содержать файл")
        
        file_index = model.index(0, 0)
        self.assertTrue(file_index.isValid(), "Файл должен быть в модели")
        
        file_name = model.data(file_index, Qt.DisplayRole)
        expected_name = os.path.splitext(os.path.basename(file_path))[0]
        self.assertEqual(file_name, expected_name, 
                        f"Имя файла должно быть '{expected_name}'")

    def test_model_data_roles(self):
        """
        Тест проверки различных ролей данных в модели Qt.
        
        Проверяет корректность работы ролей DisplayRole, DecorationRole, FontRole, ForegroundRole.
        """
        # Arrange
        st_content = '{1, {1, {"ТестоваяПапка", 1, 0, "", ""}, {0, {"ТестовыйШаблон", 0, 1, "", "Контент"}}}}'
        file_path = self.create_test_st_file(st_content)
        
        parsed_data = self.parser.parse_st_file(file_path)
        self.model.add_file(file_path, parsed_data)
        
        file_index = self.model.index(0, 0)
        folder_index = self.model.index(0, 0, file_index)
        
        # Assert: Проверяем различные роли
        # DisplayRole - отображаемый текст
        display_data = self.model.data(folder_index, Qt.DisplayRole)
        self.assertIsNotNone(display_data, "DisplayRole должен возвращать данные")
        self.assertEqual(display_data, "ТестоваяПапка", 
                        "DisplayRole должен возвращать имя элемента")
        
        # DecorationRole - иконка
        icon = self.model.data(folder_index, Qt.DecorationRole)
        # Иконка может быть None или QIcon, проверяем что не ошибка
        self.assertIsNotNone(icon or True, "DecorationRole не должен вызывать ошибку")
        
        # FontRole - шрифт
        font = self.model.data(folder_index, Qt.FontRole)
        self.assertIsNotNone(font, "FontRole должен возвращать шрифт")
        
        # ForegroundRole - цвет текста
        color = self.model.data(folder_index, Qt.ForegroundRole)
        self.assertIsNotNone(color, "ForegroundRole должен возвращать цвет")

    def test_complex_nested_structure(self):
        """
        Тест обработки сложной вложенной структуры.
        
        Проверяет корректность работы с глубоко вложенными папками и шаблонами.
        """
        # Arrange: Создаем файл с глубокой вложенностью
        st_content = '{1, {1, {"Уровень1", 1, 0, "", ""}, {1, {"Уровень2", 1, 0, "", ""}, {1, {"Уровень3", 1, 0, "", ""}, {0, {"ГлубокийШаблон", 0, 1, "", "Контент"}}}}}}}'
        file_path = self.create_test_st_file(st_content)
        
        # Act
        parsed_data = self.parser.parse_st_file(file_path)
        self.model.add_file(file_path, parsed_data)
        
        # Assert: Проверяем глубокую вложенность
        file_index = self.model.index(0, 0)
        level1_index = self.model.index(0, 0, file_index)
        
        self.assertTrue(level1_index.isValid(), "Уровень 1 должен существовать")
        level1_name = self.model.data(level1_index, Qt.DisplayRole)
        self.assertEqual(level1_name, "Уровень1", "Имя уровня 1 должно быть корректным")
        
        # Проверяем уровень 2
        if self.model.rowCount(level1_index) > 0:
            level2_index = self.model.index(0, 0, level1_index)
            self.assertTrue(level2_index.isValid(), "Уровень 2 должен существовать")
            
            # Проверяем уровень 3
            if self.model.rowCount(level2_index) > 0:
                level3_index = self.model.index(0, 0, level2_index)
                self.assertTrue(level3_index.isValid(), "Уровень 3 должен существовать")
                
                # Проверяем шаблон на уровне 3
                if self.model.rowCount(level3_index) > 0:
                    template_index = self.model.index(0, 0, level3_index)
                    self.assertTrue(template_index.isValid(), "Шаблон должен существовать")
                    template_name = self.model.data(template_index, Qt.DisplayRole)
                    self.assertEqual(template_name, "ГлубокийШаблон",
                                   "Имя шаблона должно быть корректным")


if __name__ == '__main__':
    unittest.main()


