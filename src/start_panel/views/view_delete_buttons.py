# Модуль для диалогового окна удаления кнопок с использованием PySide6
from typing import List                                                                                                   # Импортируем List для аннотаций типов
from PySide6.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QCheckBox   # Импортируем необходимые классы для создания GUI
from PySide6.QtCore import Qt                                                                                             # Импортируем Qt для использования констант

class DeleteButtonsDialog(QDialog):
    """
    Класс для диалогового окна, позволяющего пользователю выбирать кнопки для удаления.
    """
    def __init__(self, view_model, parent=None):
        """
        Инициализация диалогового окна.
        
        :param view_model: Модель представления, содержащая данные о кнопках.
        :param parent: Родительский виджет (по умолчанию None).
        """
        super().__init__(parent)                    # Вызов конструктора родительского класса
        self.view_model = view_model                # Сохранение ссылки на модель представления
        self.setWindowTitle("Удаление кнопок")      # Установка заголовка окна 
        self.setModal(True)                         # Установка окна как модального

        # Основной layout
        layout = QVBoxLayout(self)                  # Создание вертикального layout для размещения элементов

        # 1. Таблица для кнопок
        self.table = QTableWidget()                                         # Создание таблицы
        self.table.setColumnCount(2)                                        # Установка количества колонок
        self.table.setHorizontalHeaderLabels(["Имя кнопки", "Удалить"])     # Установка заголовков колонок
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.horizontalHeader().setStretchLastSection(True)

        # 2. Кнопки управления
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(self.reject)

        # Сборка интерфейса
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addWidget(self.table)
        layout.addLayout(button_layout)

        # Инициализация данных
        self.update_table()
        self.view_model.selection_changed.connect(self.update_table)

    def update_table(self):
        """Обновляет содержимое таблицы"""
        # TODO 🚧 В разработке: 04.08.2025 - не работает метод update_table()
        self.table.setRowCount(0)  # Очищаем перед обновлением

        buttons = self.view_model.get_all_buttons()
        self.table.setRowCount(len(buttons))

        for i, name in enumerate(buttons):
            # Ячейка с именем
            name_item = QTableWidgetItem(name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(i, 0, name_item)

            # Чекбокс
            checkbox = QCheckBox()
            checkbox.setChecked(name in self.view_model.get_selected_buttons())
            checkbox.stateChanged.connect(
                lambda state, n=name: self.view_model.toggle_selection(n)
            )
            self.table.setCellWidget(i, 1, checkbox)

    def get_selected_buttons(self) -> List[str]:
        """Возвращает выбранные для удаления кнопки"""
        return self.view_model.get_selected_buttons()   # Возвращает список выбранных кнопок

    

                 
    