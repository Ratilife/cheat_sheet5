"""
Модульные тесты для моделей данных дерева файлов.

Тестирует корректность построения иерархической структуры дерева файлов из данных,
полученных парсером. Проверяет:
- Преобразование плоской структуры в дерево
- Корректность установки связей между родительскими и дочерними элементами
- Обновление модели при изменении исходных данных
"""

import unittest
from unittest.mock import Mock, MagicMock
from PySide6.QtCore import QModelIndex, Qt
from models.st_md_file_tree_model import STMDFileTreeModel
from models.st_md_file_tree_item import STMDFileTreeItem
from src.parsers.content_cache import ContentCache


class TestSTMDFileTreeItem(unittest.TestCase):
    """Тесты для класса STMDFileTreeItem."""

    def setUp(self):
        """Настройка тестового окружения."""
        self.root_item = STMDFileTreeItem(["Root", "root", ""])

    def test_item_creation(self):
        """Тест создания элемента дерева."""
        # Arrange & Act
        item = STMDFileTreeItem(["TestItem", "folder", ""], self.root_item)

        # Assert
        self.assertEqual(item.item_data[0], "TestItem", "Имя должно быть 'TestItem'")
        self.assertEqual(item.item_data[1], "folder", "Тип должен быть 'folder'")
        self.assertEqual(item.type, "folder", "Свойство type должно быть 'folder'")
        self.assertEqual(item.parent_item, self.root_item, "Родитель должен быть установлен")
        self.assertEqual(len(item.child_items), 0, "Список детей должен быть пустым")

    def test_item_parent_child_relationship(self):
        """Тест установки связей родитель-дочерний элемент."""
        # Arrange
        parent = STMDFileTreeItem(["Parent", "folder", ""], self.root_item)
        child1 = STMDFileTreeItem(["Child1", "template", "content1"], parent)
        child2 = STMDFileTreeItem(["Child2", "template", "content2"], parent)

        # Act
        parent.child_items.append(child1)
        parent.child_items.append(child2)

        # Assert
        self.assertEqual(len(parent.child_items), 2, "Родитель должен иметь 2 дочерних элемента")
        self.assertEqual(child1.parent_item, parent, "Родитель child1 должен быть установлен")
        self.assertEqual(child2.parent_item, parent, "Родитель child2 должен быть установлен")
        self.assertEqual(parent.child_items[0], child1, "Первый ребенок должен быть child1")
        self.assertEqual(parent.child_items[1], child2, "Второй ребенок должен быть child2")


class TestSTMDFileTreeModel(unittest.TestCase):
    """Тесты для класса STMDFileTreeModel."""

    def setUp(self):
        """Настройка тестового окружения."""
        self.content_cache = Mock(spec=ContentCache)
        self.model = STMDFileTreeModel(self.content_cache)

    def test_model_initialization(self):
        """Тест инициализации модели."""
        # Assert
        self.assertIsNotNone(self.model.root_item, "Корневой элемент должен быть создан")
        self.assertEqual(self.model.root_item.item_data[0], "Root", 
                        "Имя корневого элемента должно быть 'Root'")
        self.assertEqual(self.model.rowCount(), 0, 
                        "Изначально модель должна быть пустой")

    def test_build_tree_from_flat_structure(self):
        """Тест преобразования плоской структуры в дерево."""
        # Arrange: Плоская структура с вложенностью
        structure = [
            {
                'name': 'Template1',
                'type': 'template',
                'content': 'Content1'
            },
            {
                'name': 'Folder1',
                'type': 'folder',
                'children': [
                    {
                        'name': 'Template2',
                        'type': 'template',
                        'content': 'Content2'
                    },
                    {
                        'name': 'Folder2',
                        'type': 'folder',
                        'children': [
                            {
                                'name': 'Template3',
                                'type': 'template',
                                'content': 'Content3'
                            }
                        ]
                    }
                ]
            }
        ]

        # Act: Строим дерево
        file_item = STMDFileTreeItem(["TestFile", "file", "/test/file.st"], self.model.root_item)
        self.model._build_tree(structure, file_item)

        # Assert: Проверяем структуру
        self.assertEqual(len(file_item.child_items), 2, 
                        "Должно быть 2 элемента верхнего уровня")
        
        # Проверяем первый элемент (Template1)
        template1 = file_item.child_items[0]
        self.assertEqual(template1.item_data[0], 'Template1')
        self.assertEqual(template1.item_data[1], 'template')
        self.assertEqual(template1.item_data[2], 'Content1')
        self.assertEqual(template1.parent_item, file_item)

        # Проверяем второй элемент (Folder1)
        folder1 = file_item.child_items[1]
        self.assertEqual(folder1.item_data[0], 'Folder1')
        self.assertEqual(folder1.item_data[1], 'folder')
        self.assertEqual(len(folder1.child_items), 2, 
                        "Folder1 должен иметь 2 дочерних элемента")

        # Проверяем вложенные элементы Folder1
        template2 = folder1.child_items[0]
        self.assertEqual(template2.item_data[0], 'Template2')
        self.assertEqual(template2.parent_item, folder1)

        folder2 = folder1.child_items[1]
        self.assertEqual(folder2.item_data[0], 'Folder2')
        self.assertEqual(len(folder2.child_items), 1, 
                        "Folder2 должен иметь 1 дочерний элемент")

        # Проверяем глубоко вложенный элемент
        template3 = folder2.child_items[0]
        self.assertEqual(template3.item_data[0], 'Template3')
        self.assertEqual(template3.parent_item, folder2)

    def test_add_file_to_model(self):
        """Тест добавления файла в модель."""
        # Arrange
        file_path = "/test/file.st"
        parsed_data = {
            'root_name': 'TestFile',
            'structure': [
                {
                    'name': 'Template1',
                    'type': 'template',
                    'content': 'Content1'
                }
            ]
        }

        # Act
        self.model.add_file(file_path, parsed_data)

        # Assert
        self.assertEqual(self.model.rowCount(), 1, 
                        "В модели должен быть 1 файл")
        
        index = self.model.index(0, 0)
        self.assertTrue(index.isValid(), "Индекс должен быть валидным")
        
        item = index.internalPointer()
        self.assertEqual(item.item_data[0], 'TestFile', 
                        "Имя файла должно быть 'TestFile'")
        self.assertEqual(item.item_data[1], 'file', 
                        "Тип должен быть 'file'")
        self.assertEqual(item.item_data[2], file_path, 
                        "Путь должен совпадать")
        self.assertEqual(len(item.child_items), 1, 
                        "Файл должен иметь 1 дочерний элемент")

    def test_parent_child_relationships_in_model(self):
        """Тест корректности установки связей родитель-дочерний в модели."""
        # Arrange
        structure = [
            {
                'name': 'Folder1',
                'type': 'folder',
                'children': [
                    {
                        'name': 'Template1',
                        'type': 'template',
                        'content': 'Content1'
                    }
                ]
            }
        ]

        # Act
        file_item = STMDFileTreeItem(["TestFile", "file", "/test/file.st"], self.model.root_item)
        self.model._build_tree(structure, file_item)

        # Assert: Проверяем связи
        folder1 = file_item.child_items[0]
        template1 = folder1.child_items[0]

        # Проверяем связь Template1 -> Folder1
        self.assertEqual(template1.parent_item, folder1, 
                        "Родитель Template1 должен быть Folder1")

        # Проверяем связь Folder1 -> File
        self.assertEqual(folder1.parent_item, file_item, 
                        "Родитель Folder1 должен быть File")

        # Проверяем связь File -> Root
        self.assertEqual(file_item.parent_item, self.model.root_item, 
                        "Родитель File должен быть Root")

    def test_index_and_parent_methods(self):
        """Тест методов index() и parent() для навигации по дереву."""
        # Arrange
        structure = [
            {
                'name': 'Folder1',
                'type': 'folder',
                'children': [
                    {
                        'name': 'Template1',
                        'type': 'template',
                        'content': 'Content1'
                    }
                ]
            }
        ]

        file_item = STMDFileTreeItem(["TestFile", "file", "/test/file.st"], self.model.root_item)
        self.model._build_tree(structure, file_item)
        self.model.root_item.child_items.append(file_item)

        # Act & Assert: Проверяем индексы
        file_index = self.model.index(0, 0)
        self.assertTrue(file_index.isValid(), "Индекс файла должен быть валидным")

        folder_index = self.model.index(0, 0, file_index)
        self.assertTrue(folder_index.isValid(), "Индекс папки должен быть валидным")

        template_index = self.model.index(0, 0, folder_index)
        self.assertTrue(template_index.isValid(), "Индекс шаблона должен быть валидным")

        # Проверяем parent()
        folder_parent = self.model.parent(folder_index)
        self.assertEqual(folder_parent, file_index, 
                        "Родитель папки должен быть файлом")

        template_parent = self.model.parent(template_index)
        self.assertEqual(template_parent, folder_index, 
                        "Родитель шаблона должен быть папкой")

    def test_row_count(self):
        """Тест подсчета строк (дочерних элементов)."""
        # Arrange
        structure = [
            {'name': 'Template1', 'type': 'template', 'content': 'Content1'},
            {'name': 'Template2', 'type': 'template', 'content': 'Content2'},
            {
                'name': 'Folder1',
                'type': 'folder',
                'children': [
                    {'name': 'Template3', 'type': 'template', 'content': 'Content3'}
                ]
            }
        ]

        # Act
        file_item = STMDFileTreeItem(["TestFile", "file", "/test/file.st"], self.model.root_item)
        self.model._build_tree(structure, file_item)
        self.model.root_item.child_items.append(file_item)

        # Assert
        self.assertEqual(self.model.rowCount(), 1, 
                        "Корневой уровень должен иметь 1 элемент")

        file_index = self.model.index(0, 0)
        self.assertEqual(self.model.rowCount(file_index), 3, 
                        "Файл должен иметь 3 дочерних элемента")

        folder_index = self.model.index(2, 0, file_index)
        self.assertEqual(self.model.rowCount(folder_index), 1, 
                        "Папка должна иметь 1 дочерний элемент")

    def test_update_file_item(self):
        """Тест обновления элемента файла при изменении данных."""
        # Arrange: Добавляем файл
        file_path = "/test/file.st"
        initial_data = {
            'root_name': 'TestFile',
            'structure': [
                {'name': 'Template1', 'type': 'template', 'content': 'Content1'}
            ]
        }
        self.model.add_file(file_path, initial_data)

        # Act: Обновляем файл новыми данными
        new_data = ('file', {
            'root_name': 'UpdatedFile',
            'structure': [
                {'name': 'Template2', 'type': 'template', 'content': 'Content2'},
                {'name': 'Template3', 'type': 'template', 'content': 'Content3'}
            ]
        })
        result = self.model.update_file_item(file_path, new_data)

        # Assert
        self.assertTrue(result, "Обновление должно быть успешным")
        
        index = self.model.index(0, 0)
        item = index.internalPointer()
        self.assertEqual(item.item_data[0], 'UpdatedFile', 
                        "Имя должно быть обновлено")
        self.assertEqual(len(item.child_items), 2, 
                        "Должно быть 2 дочерних элемента после обновления")

    def test_update_file_item_removes_old_children(self):
        """Тест, что при обновлении старые дочерние элементы удаляются."""
        # Arrange
        file_path = "/test/file.st"
        initial_data = {
            'root_name': 'TestFile',
            'structure': [
                {'name': 'Template1', 'type': 'template', 'content': 'Content1'},
                {'name': 'Template2', 'type': 'template', 'content': 'Content2'},
                {'name': 'Template3', 'type': 'template', 'content': 'Content3'}
            ]
        }
        self.model.add_file(file_path, initial_data)

        # Act: Обновляем с меньшим количеством элементов
        new_data = ('file', {
            'root_name': 'UpdatedFile',
            'structure': [
                {'name': 'Template4', 'type': 'template', 'content': 'Content4'}
            ]
        })
        self.model.update_file_item(file_path, new_data)

        # Assert
        index = self.model.index(0, 0)
        item = index.internalPointer()
        self.assertEqual(len(item.child_items), 1, 
                        "Должен остаться только 1 дочерний элемент")
        self.assertEqual(item.child_items[0].item_data[0], 'Template4', 
                        "Оставшийся элемент должен быть Template4")

    def test_data_method_returns_correct_values(self):
        """Тест метода data() для получения данных элементов."""
        # Arrange
        structure = [
            {'name': 'Template1', 'type': 'template', 'content': 'Content1'}
        ]
        file_item = STMDFileTreeItem(["TestFile", "file", "/test/file.st"], self.model.root_item)
        self.model._build_tree(structure, file_item)
        self.model.root_item.child_items.append(file_item)

        # Act & Assert
        file_index = self.model.index(0, 0)
        
        # Проверяем DisplayRole
        display_data = self.model.data(file_index, Qt.DisplayRole)
        self.assertEqual(display_data, "TestFile", 
                        "DisplayRole должен возвращать имя файла")

        # Проверяем UserRole + 2 (тип элемента)
        item_type = self.model.data(file_index, Qt.UserRole + 2)
        self.assertEqual(item_type, "file", 
                        "UserRole + 2 должен возвращать тип элемента")

    def test_remove_row(self):
        """Тест удаления строки из модели."""
        # Arrange
        structure = [
            {'name': 'Template1', 'type': 'template', 'content': 'Content1'},
            {'name': 'Template2', 'type': 'template', 'content': 'Content2'}
        ]
        file_item = STMDFileTreeItem(["TestFile", "file", "/test/file.st"], self.model.root_item)
        self.model._build_tree(structure, file_item)
        self.model.root_item.child_items.append(file_item)

        # Act
        file_index = self.model.index(0, 0)
        result = self.model.removeRow(0, file_index)

        # Assert
        self.assertTrue(result, "Удаление должно быть успешным")
        self.assertEqual(len(file_item.child_items), 1, 
                        "Должен остаться 1 дочерний элемент")
        self.assertEqual(file_item.child_items[0].item_data[0], 'Template2', 
                        "Оставшийся элемент должен быть Template2")

    def test_complex_hierarchical_structure(self):
        """Тест построения сложной иерархической структуры."""
        # Arrange: Сложная структура с несколькими уровнями вложенности
        structure = [
            {
                'name': 'Folder1',
                'type': 'folder',
                'children': [
                    {
                        'name': 'Folder2',
                        'type': 'folder',
                        'children': [
                            {
                                'name': 'Folder3',
                                'type': 'folder',
                                'children': [
                                    {'name': 'Template1', 'type': 'template', 'content': 'Content1'}
                                ]
                            }
                        ]
                    }
                ]
            }
        ]

        # Act
        file_item = STMDFileTreeItem(["TestFile", "file", "/test/file.st"], self.model.root_item)
        self.model._build_tree(structure, file_item)

        # Assert: Проверяем все уровни вложенности
        folder1 = file_item.child_items[0]
        self.assertEqual(folder1.item_data[0], 'Folder1')
        self.assertEqual(len(folder1.child_items), 1)

        folder2 = folder1.child_items[0]
        self.assertEqual(folder2.item_data[0], 'Folder2')
        self.assertEqual(len(folder2.child_items), 1)

        folder3 = folder2.child_items[0]
        self.assertEqual(folder3.item_data[0], 'Folder3')
        self.assertEqual(len(folder3.child_items), 1)

        template1 = folder3.child_items[0]
        self.assertEqual(template1.item_data[0], 'Template1')
        self.assertEqual(template1.parent_item, folder3)

    def test_add_multiple_files(self):
        """Тест добавления нескольких файлов в модель."""
        # Arrange
        files_data = [
            ("/test/file1.st", {'root_name': 'File1', 'structure': []}),
            ("/test/file2.st", {'root_name': 'File2', 'structure': []}),
            ("/test/file3.md", {'root_name': 'File3', 'structure': []})
        ]

        # Act
        for file_path, parsed_data in files_data:
            self.model.add_file(file_path, parsed_data)

        # Assert
        self.assertEqual(self.model.rowCount(), 3, 
                        "В модели должно быть 3 файла")
        
        for i, (file_path, _) in enumerate(files_data):
            index = self.model.index(i, 0)
            item = index.internalPointer()
            self.assertEqual(item.item_data[2], file_path, 
                           f"Путь файла {i+1} должен совпадать")


if __name__ == '__main__':
    unittest.main()

