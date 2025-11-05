#delta_operations.py
import time
from typing import List, Any, Dict
from enum import Enum


class DeltaOperation(Enum):
    """
    Перечисление всех возможных операций над элементами структуры.
    ТОЛЬКО КОНСТАНТЫ, без логики!
    """
    UPDATE_CONTENT = "update_content"  # Изменение текста шаблона
    RENAME = "rename"                  # Переименование элемента
    MOVE = "move"                      # Перемещение между папками
    DELETE = "delete"                  # Удаление элемента
    CREATE = "create"                  # Создание нового элемента

    # МОЖНО добавить вспомогательные методы, но НЕ бизнес-логику:
    def __str__(self):
        return self.value

    @classmethod
    def get_all_operations(cls):
        """Просто возвращает список всех операций"""
        return list(cls)


class Delta:
    """
        Объект, представляющий одно атомарное изменение в структуре ST-файла.
        Содержит всю информацию, необходимую для применения и отмены операции.
    """
    def __init__(self, operation: DeltaOperation, element_path: List[str], **kwargs):
        """
               Args:
                   operation: Тип операции из DeltaOperation
                   element_path: Путь к элементу ['root', 'parent', 'element']
                   **kwargs: Дополнительные данные для операции
        """
        self.operation = operation
        self.element_path = element_path  # ['root', 'parent', 'element']
        self.timestamp = time.time()
        self.data = kwargs  # дополнительные данные для операции Просто сохраняем ВСЁ что передали

    def to_dict(self) -> Dict[str, Any]:
        """
        Сериализует дельту в словарь для:
        - Логирования
        - Сохранения в файл
        - Отладки
        """
        return {
            'operation': self.operation.value,  # .value чтобы получить строку
            'element_path': self.element_path,
            'timestamp': self.timestamp,
            'data': self.data
        }

    def get_element_name(self) -> str:
        """
        Возвращает имя целевого элемента (последний элемент в пути)
        """
        return self.element_path[-1] if self.element_path else ""

    def get_parent_path(self) -> List[str]:
        """
        Возвращает путь к родительскому элементу
        """
        return self.element_path[:-1] if len(self.element_path) > 1 else ['root']

    def is_valid(self) -> bool:
        """
        Проверяет, что дельта содержит все необходимые данные
        """
        if not self.operation or not self.element_path:
            return False

        required_fields = {
            DeltaOperation.UPDATE_CONTENT: ['old_content', 'new_content'],
            DeltaOperation.RENAME: ['old_name', 'new_name'],
            DeltaOperation.CREATE: ['element_type', 'element_name']
        }

        required = required_fields.get(self.operation, [])
        return all(field in self.data for field in required)

    def create_reverse_delta(self) -> 'Delta':
        """
        Создает обратную дельту для отмены операции
        """
        reverse_operations = {
            DeltaOperation.UPDATE_CONTENT: DeltaOperation.UPDATE_CONTENT,
            DeltaOperation.RENAME: DeltaOperation.RENAME,
            DeltaOperation.MOVE: DeltaOperation.MOVE,
            DeltaOperation.DELETE: DeltaOperation.CREATE,  # Удаление → Создание
            DeltaOperation.CREATE: DeltaOperation.DELETE  # Создание → Удаление
        }

        reverse_data = {}

        if self.operation == DeltaOperation.UPDATE_CONTENT:
            # Для отмены изменения контента меняем местами старый и новый текст
            reverse_data = {
                'old_content': self.data['new_content'],
                'new_content': self.data['old_content']
            }

        elif self.operation == DeltaOperation.RENAME:
            # Для отмены переименования меняем местами старое и новое имя
            reverse_data = {
                'old_name': self.data['new_name'],
                'new_name': self.data['old_name']
            }

        elif self.operation == DeltaOperation.MOVE:
            # Для отмены перемещения меняем местами старый и новый путь
            reverse_data = {
                'old_path': self.data['new_path'],
                'new_path': self.data['old_path']
            }

        elif self.operation == DeltaOperation.DELETE:
            # Для отмены удаления нам нужны данные для создания элемента
            reverse_data = {
                'element_type': self.data['element_type'],
                'element_name': self.data['element_name'],
                'content': self.data.get('content', ''),
                'children': self.data.get('children', [])
            }

        elif self.operation == DeltaOperation.CREATE:
            # Для отмены создания просто удаляем (данные не нужны)
            reverse_data = {}  # Пусто - просто удаляем элемент

        return Delta(
            operation=reverse_operations[self.operation],
            element_path=self.element_path,
            **reverse_data
        )