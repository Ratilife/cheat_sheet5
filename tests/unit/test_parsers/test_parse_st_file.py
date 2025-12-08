"""
Модульные тесты для парсера ST-файлов.

Тестирует класс STFileParserWrapper на различных сценариях:
- Успешный парсинг корректного ST-файла
- Обработка несуществующих файлов
- Обработка ошибок парсинга при некорректном синтаксисе
- Обработка файлов с различными кодировками (UTF-8)
- Обработка пустых файлов
"""

import unittest
import os
import tempfile
from src.parsers.st_file_parser import STFileParserWrapper


class TestSTFileParser(unittest.TestCase):
    """Тестовый класс для парсера ST-файлов."""

    def setUp(self):
        """Настройка тестового окружения перед каждым тестом."""
        self.parser = STFileParserWrapper()
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        """Очистка после каждого теста."""
        self.temp_dir.cleanup()

    def create_test_st_file(self, content, encoding='utf-8'):
        """
        Создание временного ST-файла с заданным содержимым.
        
        Args:
            content: Содержимое файла
            encoding: Кодировка файла (по умолчанию UTF-8)
            
        Returns:
            str: Путь к созданному файлу
        """
        temp_file = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.st',
            encoding=encoding,
            dir=self.temp_dir.name,
            delete=False
        )
        temp_file.write(content)
        temp_file.close()
        return temp_file.name

    def test_successful_parsing_valid_st_file(self):
        """
        Тест успешного парсинга корректного ST-файла с валидной структурой.
        
        Проверяет:
        - Корректное извлечение структуры файла
        - Правильное определение имени корня
        - Наличие всех ожидаемых элементов (папки и шаблоны)
        """
        # Arrange: Создаем корректный ST-файл с папками и шаблонами
        st_content = '{1, {2, {"КорневаяПапка", 1, 0, "", ""}, {0, {"Шаблон1", 0, 1, "", "Содержимое шаблона 1"}}, {1, {"ВложеннаяПапка", 1, 0, "", ""}, {0, {"Шаблон2", 0, 1, "", "Содержимое шаблона 2"}}}}}'
        file_path = self.create_test_st_file(st_content)
        expected_root_name = os.path.splitext(os.path.basename(file_path))[0]

        # Act: Парсим файл
        result = self.parser.parse_st_file(file_path)

        # Assert: Проверяем результат
        self.assertIsInstance(result, dict, "Результат должен быть словарем")
        self.assertIn('structure', result, "Результат должен содержать ключ 'structure'")
        self.assertIn('root_name', result, "Результат должен содержать ключ 'root_name'")
        self.assertEqual(result['root_name'], expected_root_name, 
                        f"Имя корня должно быть '{expected_root_name}'")
        self.assertIsInstance(result['structure'], list, 
                             "Структура должна быть списком")
        
        # Проверяем, что структура не пустая
        self.assertGreater(len(result['structure']), 0, 
                          "Структура не должна быть пустой для валидного файла")
        
        # Проверяем структуру первого элемента
        if len(result['structure']) > 0:
            first_item = result['structure'][0]
            self.assertIn('name', first_item, "Элемент должен содержать 'name'")
            self.assertIn('type', first_item, "Элемент должен содержать 'type'")
            self.assertIn(first_item['type'], ['folder', 'template'], 
                         "Тип должен быть 'folder' или 'template'")

    def test_nonexistent_file_returns_empty_structure(self):
        """
        Тест обработки несуществующих файлов с корректным возвратом пустой структуры.
        
        Проверяет:
        - Возврат пустой структуры при отсутствии файла
        - Корректное определение имени корня из пути
        - Отсутствие исключений при обработке несуществующего файла
        """
        # Arrange: Путь к несуществующему файлу
        nonexistent_file = os.path.join(self.temp_dir.name, "nonexistent_file.st")
        expected_root_name = "nonexistent_file"

        # Act: Пытаемся распарсить несуществующий файл
        result = self.parser.parse_st_file(nonexistent_file)

        # Assert: Проверяем, что возвращается пустая структура
        self.assertIsInstance(result, dict, "Результат должен быть словарем")
        self.assertIn('structure', result, "Результат должен содержать ключ 'structure'")
        self.assertIn('root_name', result, "Результат должен содержать ключ 'root_name'")
        self.assertEqual(result['structure'], [], 
                        "Структура должна быть пустым списком для несуществующего файла")
        self.assertEqual(result['root_name'], expected_root_name,
                        f"Имя корня должно быть '{expected_root_name}'")

    def test_parsing_error_invalid_syntax(self):
        """
        Тест обработки ошибок парсинга при некорректном синтаксисе файла.
        
        Проверяет:
        - Возврат пустой структуры при некорректном синтаксисе
        - Корректное определение имени корня
        - Отсутствие исключений при ошибке парсинга
        """
        # Arrange: Создаем файл с некорректным синтаксисом
        invalid_content = "Это не валидный ST-файл { неполная структура"
        file_path = self.create_test_st_file(invalid_content)
        expected_root_name = os.path.splitext(os.path.basename(file_path))[0]

        # Act: Пытаемся распарсить файл с ошибкой
        result = self.parser.parse_st_file(file_path)

        # Assert: Проверяем, что возвращается пустая структура
        self.assertIsInstance(result, dict, "Результат должен быть словарем")
        self.assertIn('structure', result, "Результат должен содержать ключ 'structure'")
        self.assertIn('root_name', result, "Результат должен содержать ключ 'root_name'")
        self.assertEqual(result['structure'], [], 
                        "Структура должна быть пустым списком при ошибке парсинга")
        self.assertEqual(result['root_name'], expected_root_name,
                        f"Имя корня должно быть '{expected_root_name}'")

    def test_parsing_error_malformed_structure(self):
        """
        Дополнительный тест обработки ошибок парсинга при неправильной структуре.
        
        Проверяет обработку файла с неправильной структурой (незакрытые скобки, 
        неправильный формат заголовков и т.д.).
        """
        # Arrange: Создаем файл с неправильной структурой
        malformed_content = '{1, {2, {"Папка", 1, 0, "", ""}, {0, {"Шаблон", 0, 1, "", "content"'  # Незакрытая структура
        file_path = self.create_test_st_file(malformed_content)
        expected_root_name = os.path.splitext(os.path.basename(file_path))[0]

        # Act: Пытаемся распарсить файл
        result = self.parser.parse_st_file(file_path)

        # Assert: Проверяем, что возвращается пустая структура
        self.assertEqual(result['structure'], [], 
                        "Структура должна быть пустым списком при неправильной структуре")
        self.assertEqual(result['root_name'], expected_root_name,
                        f"Имя корня должно быть '{expected_root_name}'")

    def test_utf8_encoding_handling(self):
        """
        Тест обработки файлов с кодировкой UTF-8.
        
        Проверяет:
        - Корректную обработку русских символов
        - Корректную обработку специальных символов
        - Правильное извлечение структуры из UTF-8 файла
        """
        # Arrange: Создаем ST-файл с русскими символами и специальными символами
        st_content = '{1, {1, {"ТестоваяПапка", 1, 0, "", ""}, {0, {"ШаблонСРусским", 0, 1, "", "Содержимое: привет мир! 🎉"}}}}'
        file_path = self.create_test_st_file(st_content, encoding='utf-8')
        expected_root_name = os.path.splitext(os.path.basename(file_path))[0]

        # Act: Парсим файл
        result = self.parser.parse_st_file(file_path)

        # Assert: Проверяем результат
        self.assertIsInstance(result, dict, "Результат должен быть словарем")
        self.assertIn('structure', result, "Результат должен содержать ключ 'structure'")
        self.assertIn('root_name', result, "Результат должен содержать ключ 'root_name'")
        self.assertEqual(result['root_name'], expected_root_name,
                        f"Имя корня должно быть '{expected_root_name}'")
        
        # Проверяем, что структура не пустая
        self.assertGreater(len(result['structure']), 0,
                          "Структура не должна быть пустой для валидного UTF-8 файла")
        
        # Проверяем, что русские символы корректно извлечены
        if len(result['structure']) > 0:
            first_item = result['structure'][0]
            if first_item.get('type') == 'folder':
                self.assertIn('ТестоваяПапка', first_item.get('name', ''),
                             "Имя папки должно содержать русские символы")
            elif first_item.get('type') == 'template':
                self.assertIn('Русским', first_item.get('name', ''),
                             "Имя шаблона должно содержать русские символы")

    def test_utf8_special_characters(self):
        """
        Дополнительный тест обработки специальных символов в UTF-8.
        
        Проверяет обработку различных специальных символов и эмодзи.
        """
        # Arrange: Создаем файл со специальными символами
        st_content = '{1, {1, {"ПапкаССимволами", 1, 0, "", ""}, {0, {"Шаблон", 0, 1, "", "Содержимое: ©®™€£¥"}}}}'
        file_path = self.create_test_st_file(st_content, encoding='utf-8')

        # Act: Парсим файл
        result = self.parser.parse_st_file(file_path)

        # Assert: Проверяем, что файл обработан без ошибок
        self.assertIsInstance(result, dict, "Результат должен быть словарем")
        self.assertIn('structure', result, "Результат должен содержать ключ 'structure'")
        # Файл может быть распарсен или вернуть пустую структуру в зависимости от валидности
        self.assertIsInstance(result['structure'], list,
                             "Структура должна быть списком")

    def test_empty_file_handling(self):
        """
        Тест обработки пустых файлов.
        
        Проверяет:
        - Возврат пустой структуры для пустого файла
        - Корректное определение имени корня
        - Отсутствие исключений при обработке пустого файла
        """
        # Arrange: Создаем пустой файл
        file_path = self.create_test_st_file("")
        expected_root_name = os.path.splitext(os.path.basename(file_path))[0]

        # Act: Парсим пустой файл
        result = self.parser.parse_st_file(file_path)

        # Assert: Проверяем результат
        self.assertIsInstance(result, dict, "Результат должен быть словарем")
        self.assertIn('structure', result, "Результат должен содержать ключ 'structure'")
        self.assertIn('root_name', result, "Результат должен содержать ключ 'root_name'")
        self.assertEqual(result['structure'], [],
                        "Структура должна быть пустым списком для пустого файла")
        self.assertEqual(result['root_name'], expected_root_name,
                        f"Имя корня должно быть '{expected_root_name}'")

    def test_empty_file_with_whitespace(self):
        """
        Дополнительный тест обработки файла, содержащего только пробелы.
        
        Проверяет обработку файла с пробельными символами.
        """
        # Arrange: Создаем файл только с пробелами
        file_path = self.create_test_st_file("   \n\t  \r\n  ")
        expected_root_name = os.path.splitext(os.path.basename(file_path))[0]

        # Act: Парсим файл
        result = self.parser.parse_st_file(file_path)

        # Assert: Проверяем результат
        self.assertIsInstance(result, dict, "Результат должен быть словарем")
        self.assertEqual(result['structure'], [],
                        "Структура должна быть пустым списком для файла с пробелами")
        self.assertEqual(result['root_name'], expected_root_name,
                        f"Имя корня должно быть '{expected_root_name}'")

    def test_complex_valid_structure(self):
        """
        Дополнительный тест парсинга сложной валидной структуры.
        
        Проверяет парсинг файла с множеством вложенных папок и шаблонов.
        """
        # Arrange: Создаем сложную структуру
        st_content = '{1, {3, {"Корень", 1, 0, "", ""}, {0, {"Шаблон1", 0, 1, "", "Контент1"}}, {1, {"Папка1", 1, 0, "", ""}, {0, {"Шаблон2", 0, 1, "", "Контент2"}}}, {1, {"Папка2", 1, 0, "", ""}, {0, {"Шаблон3", 0, 1, "", "Контент3"}}}}}'
        file_path = self.create_test_st_file(st_content)

        # Act: Парсим файл
        result = self.parser.parse_st_file(file_path)

        # Assert: Проверяем результат
        self.assertIsInstance(result, dict, "Результат должен быть словарем")
        self.assertGreater(len(result['structure']), 0,
                          "Структура не должна быть пустой для валидного файла")
        
        # Проверяем наличие элементов
        structure = result['structure']
        self.assertGreaterEqual(len(structure), 1,
                               "Должен быть хотя бы один элемент в структуре")


if __name__ == '__main__':
    unittest.main()
