from typing import Any, Dict, List

from managers.file_manager import FileManager
from operation.delta_operations import Delta, DeltaOperation
from parsers.file_parser_service import FileParserService
from src.utils.cache_manager import get_content_cache

class DeltaProcessor:
    """
    Класс для обработки операций с дельтами.
    Отвечает за применение, отмену и валидацию дельт.
    """

    """def __init__(self):
        self._handlers = {
            DeltaOperation.UPDATE_CONTENT: self._handle_update_content,
            DeltaOperation.RENAME: self._handle_rename,
            DeltaOperation.MOVE: self._handle_move,
            DeltaOperation.DELETE: self._handle_delete,
            #DeltaOperation.CREATE: self._handle_create
        }"""
    def register_change(self, operation, element_path, **data):
        """Регистрирует любое изменение в очереди дельт"""
        delta = Delta(operation, element_path, **data)
        return delta

    def _extract_content_from_structure(self, structure) -> str:
        """
        Извлекает текстовое содержимое из структуры данных.

        Args:
            structure: Структура данных после парсинга ST-файла

        Returns:
            str: Текстовое содержимое для отображения в редакторе
        """
        if structure is None:
            return ""

        # Обрабатываем разные форматы структуры
        if isinstance(structure, tuple) and len(structure) == 2:
            # Формат: ('file', {'structure': [...]})
            file_type, content_dict = structure
            if file_type == 'file' and isinstance(content_dict, dict):
                structure = content_dict.get('structure', [])

        elif isinstance(structure, dict):
            # Формат: {'structure': [...]}
            structure = structure.get('structure', [])

        # Рекурсивно собираем контент из всех элементов
        content_parts = []

        def _extract_from_element(element):
            if isinstance(element, dict):
                # Если у элемента есть контент - добавляем его
                if 'content' in element and element['content']:
                    content_parts.append(element['content'])

                # Рекурсивно обрабатываем детей
                if 'children' in element:
                    for child in element['children']:
                        _extract_from_element(child)

        # Обрабатываем корневую структуру
        if isinstance(structure, list):
            for element in structure:
                _extract_from_element(element)

        # Объединяем все части контента
        return '\n'.join(content_parts)
    def apply_pending_deltas(self,template_context):
        """Применяет все ожидающие дельты к структуре"""
        # TODO 🚧 В разработке: 04.11.2025
        if not template_context['pending_deltas']:
            return True  # Нет изменений

        # 1. Получаем актуальную структуру
        current_structure = template_context['original_structure']

        print(f' находимся в методе _apply_pending_deltas() заходим в цикл по работе с дельтой.')
        # 2. Применяем каждую дельту
        success = self.apply_all_deltas(current_structure, template_context)
        if not success:
            return False  # Откатываем если ошибка

        # 3. Извлекаем данные из кортежа и готовим для сериализации
        if isinstance(current_structure, tuple) and len(current_structure) == 2:
            # Формат: ('file', {данные})
            element_type, structure_dict = current_structure
            if element_type == 'file' and isinstance(structure_dict, dict):
                # Используем весь словарь для сериализации
                data_for_serialization = structure_dict
            else:
                # Если формат неожиданный, создаем структуру по умолчанию
                data_for_serialization = {'structure': [], 'root_name': 'Root'}
        elif isinstance(current_structure, dict):
            # Если уже словарь, используем как есть
            data_for_serialization = current_structure
        else:
            # Неизвестный формат - создаем структуру по умолчанию
            data_for_serialization = {'structure': [], 'root_name': 'Root'}

        print(f'🔍 Данные для сериализации: {data_for_serialization}')

        # 4. Сериализуем и сохраняем
        self.parser_service = FileParserService()
        self.file_operations = FileManager()
        st_content = self.parser_service.serialize_st_structure(data_for_serialization)
        print(f'st_content :{st_content}')
        success = self.file_operations.write_file(
            template_context['file_path'],
            st_content
        )

        if success:
            print(f' данные которые, будут записаны в кэш current_structure: {current_structure}')
            # 4. Очищаем очередь и обновляем кэш
            template_context['pending_deltas'].clear()
            self.content_cache = get_content_cache()
            self.content_cache.set(template_context['file_path'], current_structure)
            template_context['last_saved_structure'] = current_structure
            template_context['original_structure'] = current_structure  # если нужно
            template_context['original_content'] = self._extract_content_from_structure(current_structure)
        return success

    def apply_all_deltas(self, current_structure, template_context):
        """
        Применяет все ожидающие дельты к текущей структуре

        Args:
            current_structure: Текущая структура данных

        Returns:
            bool: True если все дельты применены успешно, False в случае ошибки
        """
        for delta in template_context['pending_deltas']:
            success = self._apply_single_delta(current_structure, delta)
            print(f' success: {success}')
            if not success:
                return False  # Прерываем при первой ошибке
        return True

    def _apply_single_delta(self, structure, delta):
        """Применяет одну дельту к структуре"""

        # Для операции DELETE нам нужен родительский контейнер, а не сам элемент
        if delta.operation == DeltaOperation.DELETE:
            # Находим родительский контейнер
            if len(delta.element_path) > 1:
                # Путь к родителю (без последнего элемента)
                parent_path = delta.element_path[:-1]
            else:
                # Элемент в корне - родитель это сама структура
                parent_path = ['root']

            # Находим родительский контейнер
            if isinstance(structure, dict):
                parent_element = self.navigate_to_element_dict(structure, parent_path)
            elif isinstance(structure, tuple):
                parent_element = self.navigate_to_element_tuple(structure, parent_path)
            else:
                print(f"❌ Неподдерживаемый тип структуры: {type(structure)}")
                return False

            if not parent_element:
                print(f"❌ Не найден родительский элемент по пути: {parent_path}")
                return False

            print(f'parent_element: {parent_element}')
            handler = self._handle_delete
            return handler(parent_element, delta.data)

        else:

            # Выбираем метод навигации в зависимости от типа structure
            if isinstance(structure, dict):
                target_element = self.navigate_to_element_dict(structure, delta.element_path)
            elif isinstance(structure, tuple):
                target_element = self.navigate_to_element_tuple(structure, delta.element_path)
            else:
                print(f"❌ Неподдерживаемый тип структуры: {type(structure)}")
                return False

            if not target_element:
                print(f"❌ Не найден элемент по пути: {delta.element_path}")
                return False
            else:
                print(f'target_element: {target_element}')

        # Выбираем обработчик в зависимости от операции
        handlers = {
            DeltaOperation.UPDATE_CONTENT: self._handle_update_content,
            DeltaOperation.RENAME: self._handle_rename,
            DeltaOperation.MOVE: self._handle_move,
            DeltaOperation.DELETE: self._handle_delete,
            #DeltaOperation.CREATE: self._handle_create_folder
        }

        handler = handlers.get(delta.operation)
        if not handler:
            print(f"❌ Неизвестная операция: {delta.operation}")
            return False
        print(f'target_element: {target_element}')
        print(f'delta.data: {delta.data}')
        return handler(target_element, delta.data)

    def _handle_update_content(self, element, data):
        """ВАША ОПЕРАЦИЯ - изменение контента шаблона"""
        element['content'] = data['new_content']
        print(f'зашли в метод _handle_update_content element: {element}')
        return True

    def _handle_rename(self, element, data):
        """Переименование элемента"""
        # element - это родительский элемент, содержащий удаляемый элемент
        # data содержит информацию об удаляемом элементе
        element['name'] = data['new_name']
        return True

    def _handle_move(self):
        pass

    def _handle_delete(self, structure, data):
        """Обработчик удаления элемента"""
        print("🛒 Зашли в метод _handle_delete()")
        print(f'structure: {structure}')
        print(f'data: {data}')

        element_name = data.get('element_name')
        if not element_name:
            print("❌ Не указано имя элемента для удаления")
            return False

        # Обрабатываем разные форматы структуры
        if isinstance(structure, tuple) and len(structure) == 2:
            # Формат: ('file', {'structure': [...]})
            file_type, content_dict = structure
            if file_type == 'file' and 'structure' in content_dict:
                # Ищем элемент в корневой структуре
                for i, item in enumerate(content_dict['structure']):
                    if item.get('name') == element_name:
                        # Удаляем элемент из корневой структуры
                        del content_dict['structure'][i]
                        print(f"✅ Элемент '{element_name}' удален из корневой структуры")
                        return True

        elif isinstance(structure, dict):
            # Формат: {'children': [...]} (родительский элемент)
            if 'children' in structure:
                for i, child in enumerate(structure['children']):
                    if child.get('name') == element_name:
                        # Удаляем элемент из детей родителя
                        del structure['children'][i]
                        print(f"✅ Элемент '{element_name}' удален")
                        return True

        elif isinstance(structure, list):
            # Формат: [...] (список элементов)
            for i, item in enumerate(structure):
                if item.get('name') == element_name:
                    del structure[i]
                    print(f"✅ Элемент '{element_name}' удален из списка")
                    return True

        print(f"❌ Элемент '{element_name}' не найден")
        return False
    def navigate_to_element_dict(self, structure, element_path):
        """Переходит по пути ['root', 'folder1', 'template'] в структуре"""
        current = structure
        print(f'🔮🔮🔮зашли в метод _navigate_to_element() смотрим содержимое параметра structure: {structure}')
        print(f'element_path : {element_path}')
        for step in element_path[1:]:  # Пропускаем 'root'
            if 'children' not in current:
                return None

            # Ищем следующий шаг в детях
            found = None
            for child in current['children']:
                if child.get('name') == step:
                    found = child
                    break

            if not found:
                return None

            current = found

        return current

    def navigate_to_element_tuple(self, structure, element_path):
        """Переходит по пути ['root', 'НовыйШаблон', 'Текст2'] в структуре-кортеже"""
        current = structure
        print(f'🔮🔮🔮 зашли в метод _navigate_to_element_tuple()')
        print(f'element_path: {element_path}')
        print(f'structure: {structure}')

        # Пропускаем 'root' и начинаем с первого реального элемента
        path_to_follow = element_path[1:]

        for i, step in enumerate(path_to_follow):
            print(f"Ищем шаг {i + 1}: '{step}'")

            # Если текущий элемент - кортеж файла
            if isinstance(current, tuple) and len(current) == 2:
                file_type, content = current
                if file_type == 'file' and 'structure' in content:
                    # Проверяем, соответствует ли root_name первому шагу
                    if i == 0 and content.get('root_name') == step:
                        print(f"Нашли корневой элемент: '{step}'")
                        current = content['structure']
                        continue
                    elif i == 0:
                        # Ищем в списке шаблонов
                        found = None
                        for item in content['structure']:
                            if item.get('name') == step:
                                found = item
                                break

                        if found:
                            current = found
                            continue
                        else:
                            print(f"Элемент '{step}' не найден в корневой структуре")
                            return None
                    else:
                        print("Неожиданная структура на корневом уровне")
                        return None

            # Если текущий элемент - список (структура корня)
            elif isinstance(current, list):
                found = None
                for item in current:
                    if item.get('name') == step:
                        found = item
                        break

                if found:
                    current = found
                    continue
                else:
                    print(f"Элемент '{step}' не найден в списке")
                    return None

            # Если текущий элемент - словарь (шаблон или папка)
            elif isinstance(current, dict):
                if current.get('name') == step:
                    # Если это последний шаг - возвращаем найденный элемент
                    if i == len(path_to_follow) - 1:
                        return current
                    # Иначе продолжаем поиск в children
                    elif 'children' in current and current.get('type') == 'folder':
                        current = current['children']
                        continue
                    else:
                        print(f"У элемента '{current.get('name')}' нет children для продолжения пути")
                        return None
                elif 'children' in current:
                    # Ищем в детях текущего элемента
                    found = None
                    for child in current['children']:
                        if child.get('name') == step:
                            found = child
                            break

                    if found:
                        current = found
                        continue
                    else:
                        print(f"Элемент '{step}' не найден в children элемента '{current.get('name')}'")
                        return None
                else:
                    print(f"Элемент '{current.get('name')}' не соответствует '{step}' и не имеет children")
                    return None
            else:
                print(f"Неизвестный тип элемента: {type(current)}")
                return None

        return current
