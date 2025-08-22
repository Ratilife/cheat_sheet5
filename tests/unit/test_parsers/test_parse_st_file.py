import unittest
from unittest.mock import Mock, patch, MagicMock
import os
import tempfile
from src.parsers.st_file_parser import ParseTreeWalker  # замените на ваш класс


class TestParseStFile(unittest.TestCase):

    def setUp(self):
        """Настройка тестового окружения перед каждым тестом"""
        self.parser = ParseTreeWalker()
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        """Очистка после каждого теста"""
        self.temp_dir.cleanup()

    def create_test_st_file(self, content):
        """Создание временного ST-файла с заданным содержимым"""
        temp_file = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.st',
            encoding='utf-8',
            dir=self.temp_dir.name,
            delete=False
        )
        temp_file.write(content)
        temp_file.close()
        return temp_file.name

    def test_successful_parsing(self):
        """Тест успешного парсинга корректного файла"""
        # Arrange (подготовка)
        st_content = """
        PROGRAM MainProgram
        VAR
            x: INT;
        END_VAR
        END_PROGRAM
        """
        file_path = self.create_test_st_file(st_content)

        # Act (действие)
        result = self.parser.parse_st_file(file_path)

        # Assert (проверка)
        self.assertIsInstance(result, dict)
        self.assertIn('structure', result)
        self.assertIn('root_name', result)
        self.assertEqual(result['root_name'], os.path.splitext(os.path.basename(file_path))[0])
        # Дополнительные проверки структуры в зависимости от вашего парсера

    def test_file_not_found(self):
        """Тест обработки несуществующего файла"""
        # Act & Assert
        result = self.parser.parse_st_file("nonexistent_file.st")

        self.assertEqual(result['structure'], [])
        self.assertIsInstance(result['root_name'], str)

    @patch('your_module.FileStream')
    @patch('your_module.STFileLexer')
    @patch('your_module.CommonTokenStream')
    @patch('your_module.STFileParser')
    def test_parsing_error_handling(self, mock_parser, mock_tokens, mock_lexer, mock_file_stream):
        """Тест обработки ошибок парсинга с помощью моков"""
        # Arrange
        mock_file_stream.side_effect = Exception("Parsing error")
        file_path = "test_file.st"

        # Act
        result = self.parser.parse_st_file(file_path)

        # Assert
        self.assertEqual(result['structure'], [])
        self.assertEqual(result['root_name'], 'test_file')

    def test_encoding_handling(self):
        """Тест обработки файла с различными кодировками"""
        st_content = "PROGRAM TestProgram END_PROGRAM"
        file_path = self.create_test_st_file(st_content)

        result = self.parser.parse_st_file(file_path)

        self.assertIsNotNone(result)
        self.assertEqual(result['root_name'], os.path.splitext(os.path.basename(file_path))[0])

    def test_empty_file(self):
        """Тест обработки пустого файла"""
        file_path = self.create_test_st_file("")

        result = self.parser.parse_st_file(file_path)

        self.assertEqual(result['structure'], [])
        self.assertIsInstance(result['root_name'], str)


if __name__ == '__main__':
    unittest.main()