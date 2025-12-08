"""
Модульные тесты для FileManager.

Тестирует функциональность управления файлами проекта:
- Создание и проверка путей
- Работа с JSON файлами
- Создание структуры папок
- Запись файлов
"""

import unittest
import tempfile
import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from managers.file_manager import FileManager, FolderCreationResult


class TestFileManager(unittest.TestCase):
    """Тесты для класса FileManager."""

    def setUp(self):
        """Настройка тестового окружения."""
        self.file_manager = FileManager()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        """Очистка после каждого теста."""
        self.temp_dir.cleanup()

    def test_is_path_already_exists_file(self):
        """Тест проверки существования файла."""
        # Arrange
        test_file = self.temp_path / "test_file.txt"
        test_file.write_text("test content")

        # Act
        result = self.file_manager.is_path_already_exists(test_file)

        # Assert
        self.assertTrue(result, "Файл должен существовать")

    def test_is_path_already_exists_folder(self):
        """Тест проверки существования папки."""
        # Arrange
        test_folder = self.temp_path / "test_folder"
        test_folder.mkdir()

        # Act
        result = self.file_manager.is_path_already_exists(test_folder)

        # Assert
        self.assertTrue(result, "Папка должна существовать")

    def test_is_path_already_exists_nonexistent(self):
        """Тест проверки несуществующего пути."""
        # Arrange
        nonexistent_path = self.temp_path / "nonexistent"

        # Act
        result = self.file_manager.is_path_already_exists(nonexistent_path)

        # Assert
        self.assertFalse(result, "Путь не должен существовать")

    def test_load_json_file(self):
        """Тест загрузки JSON файла."""
        # Arrange
        test_data = {"key": "value", "number": 42, "list": [1, 2, 3]}
        json_file = self.temp_path / "test.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)

        # Act
        result = self.file_manager.load_json_file(json_file)

        # Assert
        self.assertEqual(result, test_data, "Загруженные данные должны совпадать")

    def test_load_json_file_nonexistent(self):
        """Тест загрузки несуществующего JSON файла."""
        # Arrange
        nonexistent_file = self.temp_path / "nonexistent.json"

        # Act & Assert
        with self.assertRaises(RuntimeError, msg="Должно быть исключение для несуществующего файла"):
            self.file_manager.load_json_file(nonexistent_file)

    def test_load_json_file_invalid_json(self):
        """Тест загрузки файла с невалидным JSON."""
        # Arrange
        invalid_json_file = self.temp_path / "invalid.json"
        invalid_json_file.write_text("{ invalid json }")

        # Act & Assert
        with self.assertRaises(RuntimeError, msg="Должно быть исключение для невалидного JSON"):
            self.file_manager.load_json_file(invalid_json_file)

    def test_save_data_to_json(self):
        """Тест сохранения данных в JSON файл."""
        # Arrange
        test_data = {"key": "value", "number": 42}
        json_file = self.temp_path / "output.json"

        # Act
        self.file_manager.save_data_to_json(json_file, test_data)

        # Assert
        self.assertTrue(json_file.exists(), "JSON файл должен быть создан")
        with open(json_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        self.assertEqual(loaded_data, test_data, "Сохраненные данные должны совпадать")

    def test_create_root_folder_structure(self):
        """Тест создания структуры папок из JSON конфигурации."""
        # Arrange
        config_data = {
            "root_folder": "test_project",
            "subfolders": {
                "docs": ["v1", "v2"],
                "src": ["main", "test"]
            }
        }
        config_file = self.temp_path / "config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f)

        # Act
        result = self.file_manager.create_root_folder_structure(config_file, self.temp_path)

        # Assert
        self.assertTrue(result.success, "Создание структуры должно быть успешным")
        self.assertIsNotNone(result.root_path, "Путь должен быть установлен")
        
        root_path = Path(result.root_path)
        self.assertTrue(root_path.exists(), "Корневая папка должна существовать")
        self.assertTrue((root_path / "docs" / "v1").exists(), "Подпапка docs/v1 должна существовать")
        self.assertTrue((root_path / "docs" / "v2").exists(), "Подпапка docs/v2 должна существовать")
        self.assertTrue((root_path / "src" / "main").exists(), "Подпапка src/main должна существовать")
        self.assertTrue((root_path / "src" / "test").exists(), "Подпапка src/test должна существовать")

    def test_create_root_folder_structure_already_exists(self):
        """Тест создания структуры, когда папка уже существует."""
        # Arrange
        config_data = {"root_folder": "test_project", "subfolders": {}}
        config_file = self.temp_path / "config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f)

        # Создаем папку заранее
        existing_folder = self.temp_path / "test_project"
        existing_folder.mkdir()

        # Act
        result = self.file_manager.create_root_folder_structure(config_file, self.temp_path)

        # Assert
        self.assertFalse(result.success, "Создание должно вернуть False")
        self.assertTrue(result.already_exists, "Флаг already_exists должен быть True")
        self.assertIsNotNone(result.error, "Должно быть сообщение об ошибке")

    def test_write_file(self):
        """Тест записи файла."""
        # Arrange
        file_path = self.temp_path / "subfolder" / "test.txt"
        content = "Test content\nLine 2"

        # Act
        result = self.file_manager.write_file(str(file_path), content)

        # Assert
        self.assertTrue(result, "Запись должна быть успешной")
        self.assertTrue(file_path.exists(), "Файл должен существовать")
        self.assertEqual(file_path.read_text(encoding='utf-8-sig'), content, 
                        "Содержимое файла должно совпадать")

    def test_write_file_creates_parent_directories(self):
        """Тест, что запись файла создает родительские директории."""
        # Arrange
        file_path = self.temp_path / "deep" / "nested" / "path" / "file.txt"
        content = "Content"

        # Act
        result = self.file_manager.write_file(str(file_path), content)

        # Assert
        self.assertTrue(result, "Запись должна быть успешной")
        self.assertTrue(file_path.parent.exists(), "Родительские директории должны быть созданы")
        self.assertTrue(file_path.exists(), "Файл должен существовать")

    def test_write_file_empty_content(self):
        """Тест записи файла с пустым содержимым."""
        # Arrange
        file_path = self.temp_path / "empty.txt"

        # Act
        result = self.file_manager.write_file(str(file_path), "")

        # Assert
        self.assertTrue(result, "Запись должна быть успешной")
        self.assertTrue(file_path.exists(), "Файл должен существовать")
        self.assertEqual(file_path.read_text(encoding='utf-8-sig'), "", 
                        "Содержимое должно быть пустым")

    def test_write_file_empty_path(self):
        """Тест записи файла с пустым путем."""
        # Act
        result = self.file_manager.write_file("", "content")

        # Assert
        self.assertFalse(result, "Запись должна вернуть False для пустого пути")

    def test_create_files_dict_with_paths(self):
        """Тест создания словаря файлов с путями."""
        # Arrange: Создаем структуру папок и файлов
        (self.temp_path / "subfolder1").mkdir()
        (self.temp_path / "subfolder2").mkdir()
        
        (self.temp_path / "subfolder1" / "file1.st").write_text("content1")
        (self.temp_path / "subfolder1" / "file2.md").write_text("content2")
        (self.temp_path / "subfolder2" / "file3.st").write_text("content3")
        (self.temp_path / "root_file.txt").write_text("content")  # Должен быть проигнорирован

        # Act
        result = self.file_manager.create_files_dict_with_paths(self.temp_path)

        # Assert
        self.assertIn("subfolder1", result, "subfolder1 должна быть в результате")
        self.assertIn("subfolder2", result, "subfolder2 должна быть в результате")
        self.assertEqual(len(result["subfolder1"]), 2, 
                        "subfolder1 должна содержать 2 файла")
        self.assertEqual(len(result["subfolder2"]), 1, 
                        "subfolder2 должна содержать 1 файл")
        # Проверяем, что только .st и .md файлы включены
        for file_path in result["subfolder1"]:
            self.assertTrue(file_path.endswith(('.st', '.md')), 
                          "Должны быть только .st и .md файлы")

    def test_create_files_dict_with_paths_empty_folders(self):
        """Тест создания словаря с пустыми папками."""
        # Arrange
        (self.temp_path / "empty_folder1").mkdir()
        (self.temp_path / "empty_folder2").mkdir()

        # Act
        result = self.file_manager.create_files_dict_with_paths(self.temp_path)

        # Assert
        self.assertIn("empty_folder1", result, "Пустая папка должна быть в результате")
        self.assertIn("empty_folder2", result, "Пустая папка должна быть в результате")
        self.assertEqual(len(result["empty_folder1"]), 0, 
                        "Пустая папка должна иметь пустой список")
        self.assertEqual(len(result["empty_folder2"]), 0, 
                        "Пустая папка должна иметь пустой список")

    @patch('managers.file_manager.QFileDialog')
    def test_dialog_st_md_files(self, mock_dialog):
        """Тест диалога выбора ST/MD файлов."""
        # Arrange
        mock_dialog.getOpenFileNames.return_value = (
            ["/path/to/file1.st", "/path/to/file2.md"], 
            "ST Files (*.st);;Markdown Files (*.md)"
        )

        # Act
        result = self.file_manager.dialog_st_md_files()

        # Assert
        self.assertEqual(len(result), 2, "Должно быть выбрано 2 файла")
        mock_dialog.getOpenFileNames.assert_called_once()

    @patch('managers.file_manager.QFileDialog')
    def test_dialog_save_st_md_files(self, mock_dialog):
        """Тест диалога сохранения ST/MD файлов."""
        # Arrange
        mock_dialog.getSaveFileName.return_value = ("/path/to/file.st", "ST Files (*.st)")

        # Act
        result = self.file_manager.dialog_save_st_md_files()

        # Assert
        self.assertEqual(result, "/path/to/file.st", "Должен быть возвращен путь к файлу")
        mock_dialog.getSaveFileName.assert_called_once()


if __name__ == '__main__':
    unittest.main()

