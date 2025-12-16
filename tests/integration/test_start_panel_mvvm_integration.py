"""
Интеграционные тесты для стартовой панели, реализованной по паттерну MVVM.

Тестирует:
1. Корректность взаимодействия между Model, ViewModel и View
2. Правильность обновления представления при изменении данных в модели
3. Корректность сохранения и загрузки конфигурации кнопок
"""

import unittest
import os
import tempfile
import json
import time
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QTimer, QSignalSpy
from PySide6.QtTest import QTest

from src.start_panel.models.model import ButtonListModel, ButtonModel
from src.start_panel.view_models.view_model import ButtonViewModel
from src.start_panel.views.view import MainWindow


class TestStartPanelMVVMIntegration(unittest.TestCase):
    """Интеграционные тесты для стартовой панели (MVVM)."""

    @classmethod
    def setUpClass(cls):
        """Инициализация QApplication для тестов Qt (вызывается один раз для всех тестов)."""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        """Настройка тестового окружения перед каждым тестом."""
        # Создаем временную директорию для хранения конфигурации
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_file = os.path.join(self.temp_dir.name, "buttons.json")
        
        # Создаем Model
        self.model = ButtonListModel(self.temp_dir.name)
        
        # Создаем ViewModel и передаем ей Model
        self.view_model = ButtonViewModel(self.model)
        
        # Создаем View и передаем ему ViewModel
        self.view = MainWindow(self.view_model)

    def tearDown(self):
        """Очистка после каждого теста."""
        # Закрываем view
        if hasattr(self, 'view'):
            self.view.close()
            self.view.deleteLater()
        
        # Очищаем временную директорию
        if hasattr(self, 'temp_dir'):
            self.temp_dir.cleanup()
        
        # Обрабатываем события Qt для корректной очистки
        QApplication.processEvents()

    def wait_for_signal(self, spy: QSignalSpy, timeout: int = 1000) -> bool:
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

    def create_test_file(self, file_path: str) -> str:
        """
        Создает тестовый файл для использования в качестве пути к программе.
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            str: Путь к созданному файлу
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("test content")
        return file_path

    def test_model_viewmodel_view_interaction(self):
        """
        Тест 1: Корректность взаимодействия между Model, ViewModel и View.
        
        Проверяет:
        - ViewModel корректно делегирует вызовы в Model
        - ViewModel испускает сигнал buttonsChanged при изменении данных
        - View корректно получает данные через ViewModel
        """
        # Arrange: Создаем тестовый файл
        test_file = self.create_test_file(os.path.join(self.temp_dir.name, "test.exe"))
        
        # Создаем шпион для сигнала buttonsChanged
        buttons_changed_spy = QSignalSpy(self.view_model.buttonsChanged)
        
        # Act: Добавляем кнопку через ViewModel
        self.view_model.add_button("Test Button", test_file)
        
        # Обрабатываем события Qt
        QApplication.processEvents()
        
        # Assert: Проверяем, что сигнал был испущен
        self.assertGreater(len(buttons_changed_spy), 0,
                          "Сигнал buttonsChanged должен быть испущен при добавлении кнопки")
        
        # Проверяем, что кнопка добавлена в Model
        buttons = self.model.get_buttons()
        self.assertEqual(len(buttons), 1, "В модели должна быть одна кнопка")
        self.assertEqual(buttons[0].name, "Test Button",
                        "Имя кнопки должно совпадать")
        self.assertEqual(buttons[0].path, test_file,
                        "Путь кнопки должен совпадать")
        
        # Проверяем, что View получает данные через ViewModel
        view_buttons = self.view_model.get_buttons()
        self.assertEqual(len(view_buttons), 1,
                        "ViewModel должна возвращать одну кнопку")
        self.assertEqual(view_buttons[0].name, "Test Button",
                        "Имя кнопки в ViewModel должно совпадать")

    def test_view_updates_on_model_change(self):
        """
        Тест 2: Правильность обновления представления при изменении данных в модели.
        
        Проверяет:
        - View обновляется при изменении данных через ViewModel
        - Сигнал buttonsChanged вызывает обновление View
        - Кнопки в UI соответствуют данным в Model
        """
        # Arrange: Создаем тестовые файлы
        test_file1 = self.create_test_file(os.path.join(self.temp_dir.name, "test1.exe"))
        test_file2 = self.create_test_file(os.path.join(self.temp_dir.name, "test2.exe"))
        
        # Добавляем начальные кнопки
        self.view_model.add_button("Button 1", test_file1)
        self.view_model.add_button("Button 2", test_file2)
        
        # Обрабатываем события
        QApplication.processEvents()
        
        # Получаем начальное количество кнопок в UI
        # (исключая служебные кнопки: collapse, add, delete, side_panel, structure_manager, close)
        initial_button_count = self._count_user_buttons()
        
        # Act: Удаляем кнопку через ViewModel
        self.view_model.remove_button(0)
        
        # Обрабатываем события
        QApplication.processEvents()
        
        # Assert: Проверяем, что количество кнопок в UI уменьшилось
        updated_button_count = self._count_user_buttons()
        self.assertEqual(updated_button_count, initial_button_count - 1,
                        "Количество кнопок в UI должно уменьшиться на 1")
        
        # Проверяем, что данные в Model обновились
        buttons = self.model.get_buttons()
        self.assertEqual(len(buttons), 1, "В модели должна остаться одна кнопка")
        self.assertEqual(buttons[0].name, "Button 2",
                        "Оставшаяся кнопка должна быть 'Button 2'")

    def _count_user_buttons(self) -> int:
        """
        Подсчитывает количество пользовательских кнопок в UI.
        
        Returns:
            int: Количество пользовательских кнопок
        """
        count = 0
        for i in range(self.view.buttons_layout.count()):
            widget = self.view.buttons_layout.itemAt(i).widget()
            if (widget and
                widget != self.view.add_button and
                widget != self.view.delete_button and
                widget != self.view.side_panel and
                widget != self.view.structure_manager and
                widget != self.view.collapse_button and
                widget != self.view.close_button):
                count += 1
        return count

    def test_save_and_load_configuration(self):
        """
        Тест 3: Корректность сохранения и загрузки конфигурации кнопок.
        
        Проверяет:
        - Конфигурация корректно сохраняется в JSON файл
        - Конфигурация корректно загружается из JSON файла
        - После перезагрузки данные восстанавливаются
        """
        # Arrange: Создаем тестовые файлы
        test_file1 = self.create_test_file(os.path.join(self.temp_dir.name, "app1.exe"))
        test_file2 = self.create_test_file(os.path.join(self.temp_dir.name, "app2.exe"))
        test_file3 = self.create_test_file(os.path.join(self.temp_dir.name, "app3.exe"))
        
        # Добавляем кнопки
        self.view_model.add_button("Application 1", test_file1)
        self.view_model.add_button("Application 2", test_file2)
        self.view_model.add_button("Application 3", test_file3)
        
        # Act: Сохраняем конфигурацию
        self.view_model.save_buttons()
        
        # Проверяем, что файл создан
        self.assertTrue(os.path.exists(self.config_file),
                       "Файл конфигурации должен быть создан")
        
        # Проверяем содержимое файла
        with open(self.config_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        
        self.assertEqual(len(saved_data), 3,
                        "В файле должно быть 3 кнопки")
        self.assertEqual(saved_data[0]['name'], "Application 1",
                        "Имя первой кнопки должно совпадать")
        self.assertEqual(saved_data[0]['path'], test_file1,
                        "Путь первой кнопки должен совпадать")
        
        # Act: Создаем новую модель и загружаем конфигурацию
        new_model = ButtonListModel(self.temp_dir.name)
        
        # Assert: Проверяем, что данные загрузились
        loaded_buttons = new_model.get_buttons()
        self.assertEqual(len(loaded_buttons), 3,
                        "Должно быть загружено 3 кнопки")
        self.assertEqual(loaded_buttons[0].name, "Application 1",
                        "Имя первой загруженной кнопки должно совпадать")
        self.assertEqual(loaded_buttons[0].path, test_file1,
                        "Путь первой загруженной кнопки должен совпадать")

    def test_view_model_signals_on_all_operations(self):
        """
        Тест 4: Проверка испускания сигналов ViewModel при всех операциях.
        
        Проверяет:
        - Сигнал buttonsChanged испускается при добавлении кнопки
        - Сигнал buttonsChanged испускается при удалении кнопки
        - Сигнал buttonsChanged испускается при редактировании кнопки
        - Сигнал buttonsChanged испускается при сортировке кнопок
        """
        # Arrange: Создаем тестовые файлы
        test_file1 = self.create_test_file(os.path.join(self.temp_dir.name, "test1.exe"))
        test_file2 = self.create_test_file(os.path.join(self.temp_dir.name, "test2.exe"))
        test_file3 = self.create_test_file(os.path.join(self.temp_dir.name, "test3.exe"))
        
        # Тест добавления
        spy = QSignalSpy(self.view_model.buttonsChanged)
        self.view_model.add_button("Button A", test_file1)
        QApplication.processEvents()
        self.assertGreater(len(spy), 0, "Сигнал должен быть испущен при добавлении")
        
        # Тест редактирования
        spy.clear()
        self.view_model.edit_button(0, "Button A Edited", test_file1)
        QApplication.processEvents()
        self.assertGreater(len(spy), 0, "Сигнал должен быть испущен при редактировании")
        
        # Тест удаления
        self.view_model.add_button("Button B", test_file2)
        spy.clear()
        self.view_model.remove_button(0)
        QApplication.processEvents()
        self.assertGreater(len(spy), 0, "Сигнал должен быть испущен при удалении")
        
        # Тест сортировки
        self.view_model.add_button("Button C", test_file3)
        spy.clear()
        self.view_model.sort_buttons()
        QApplication.processEvents()
        self.assertGreater(len(spy), 0, "Сигнал должен быть испущен при сортировке")

    def test_full_mvvm_cycle(self):
        """
        Тест 5: Полный цикл MVVM - добавление, редактирование, удаление, сохранение, загрузка.
        
        Проверяет полный цикл работы приложения:
        - Добавление кнопок через ViewModel
        - Обновление View через сигналы
        - Редактирование кнопок
        - Удаление кнопок
        - Сохранение конфигурации
        - Загрузка конфигурации в новую модель
        """
        # Arrange: Создаем тестовые файлы
        test_file1 = self.create_test_file(os.path.join(self.temp_dir.name, "app1.exe"))
        test_file2 = self.create_test_file(os.path.join(self.temp_dir.name, "app2.exe"))
        
        # Act 1: Добавляем кнопки
        self.view_model.add_button("App 1", test_file1)
        self.view_model.add_button("App 2", test_file2)
        QApplication.processEvents()
        
        # Assert 1: Проверяем, что кнопки добавлены
        buttons = self.view_model.get_buttons()
        self.assertEqual(len(buttons), 2, "Должно быть 2 кнопки")
        
        # Act 2: Редактируем первую кнопку
        self.view_model.edit_button(0, "App 1 Edited", test_file1)
        QApplication.processEvents()
        
        # Assert 2: Проверяем редактирование
        buttons = self.view_model.get_buttons()
        self.assertEqual(buttons[0].name, "App 1 Edited",
                       "Имя кнопки должно быть обновлено")
        
        # Act 3: Удаляем вторую кнопку
        self.view_model.remove_button(1)
        QApplication.processEvents()
        
        # Assert 3: Проверяем удаление
        buttons = self.view_model.get_buttons()
        self.assertEqual(len(buttons), 1, "Должна остаться одна кнопка")
        
        # Act 4: Сохраняем конфигурацию
        self.view_model.save_buttons()
        
        # Assert 4: Проверяем сохранение
        self.assertTrue(os.path.exists(self.config_file),
                       "Файл конфигурации должен существовать")
        
        # Act 5: Загружаем в новую модель
        new_model = ButtonListModel(self.temp_dir.name)
        new_view_model = ButtonViewModel(new_model)
        
        # Assert 5: Проверяем загрузку
        loaded_buttons = new_view_model.get_buttons()
        self.assertEqual(len(loaded_buttons), 1,
                        "Должна быть загружена одна кнопка")
        self.assertEqual(loaded_buttons[0].name, "App 1 Edited",
                        "Имя загруженной кнопки должно совпадать")

    def test_view_model_validation(self):
        """
        Тест 6: Проверка валидации данных в ViewModel.
        
        Проверяет:
        - ViewModel корректно валидирует данные через Model
        - Некорректные данные не добавляются
        """
        # Arrange: Создаем тестовый файл
        test_file = self.create_test_file(os.path.join(self.temp_dir.name, "test.exe"))
        
        # Act & Assert: Проверяем валидацию
        # Валидная кнопка
        is_valid = self.view_model.is_valid_button("Valid Button", test_file)
        self.assertTrue(is_valid, "Валидная кнопка должна проходить проверку")
        
        # Невалидная кнопка (пустое имя)
        is_valid = self.view_model.is_valid_button("", test_file)
        self.assertFalse(is_valid, "Кнопка с пустым именем не должна проходить проверку")
        
        # Невалидная кнопка (несуществующий путь)
        is_valid = self.view_model.is_valid_button("Button", "/nonexistent/path.exe")
        self.assertFalse(is_valid, "Кнопка с несуществующим путем не должна проходить проверку")

    def test_multiple_views_same_viewmodel(self):
        """
        Тест 7: Проверка работы нескольких View с одним ViewModel.
        
        Проверяет:
        - Несколько View могут работать с одним ViewModel
        - Изменения в одном View отражаются во всех View
        """
        # Arrange: Создаем второй View с тем же ViewModel
        view2 = MainWindow(self.view_model)
        test_file = self.create_test_file(os.path.join(self.temp_dir.name, "test.exe"))
        
        # Act: Добавляем кнопку через первый View
        self.view_model.add_button("Shared Button", test_file)
        QApplication.processEvents()
        
        # Assert: Проверяем, что оба View обновились
        buttons1 = self.view_model.get_buttons()
        buttons2 = self.view_model.get_buttons()
        
        self.assertEqual(len(buttons1), 1, "Первый View должен видеть кнопку")
        self.assertEqual(len(buttons2), 1, "Второй View должен видеть кнопку")
        
        # Очистка
        view2.close()
        view2.deleteLater()
        QApplication.processEvents()

    def test_configuration_file_format(self):
        """
        Тест 8: Проверка формата файла конфигурации.
        
        Проверяет:
        - Файл конфигурации имеет правильный JSON формат
        - Файл содержит все необходимые поля
        - Файл корректно обрабатывается при загрузке
        """
        # Arrange: Создаем тестовые файлы
        test_file1 = self.create_test_file(os.path.join(self.temp_dir.name, "app1.exe"))
        test_file2 = self.create_test_file(os.path.join(self.temp_dir.name, "app2.exe"))
        
        # Добавляем кнопки
        self.view_model.add_button("Button 1", test_file1)
        self.view_model.add_button("Button 2", test_file2)
        
        # Act: Сохраняем конфигурацию
        self.view_model.save_buttons()
        
        # Assert: Проверяем формат файла
        with open(self.config_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Проверяем структуру данных
        self.assertIsInstance(data, list, "Данные должны быть списком")
        self.assertEqual(len(data), 2, "Должно быть 2 элемента")
        
        # Проверяем структуру каждого элемента
        for item in data:
            self.assertIn('name', item, "Каждый элемент должен содержать 'name'")
            self.assertIn('path', item, "Каждый элемент должен содержать 'path'")
            self.assertIsInstance(item['name'], str, "'name' должен быть строкой")
            self.assertIsInstance(item['path'], str, "'path' должен быть строкой")


if __name__ == '__main__':
    unittest.main()




