from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QInputDialog, QHBoxLayout, QStyle, QDialog
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import QByteArray, QBuffer, QIODevice, QSize, Qt, QPoint
from src.start_panel.models.model import ButtonListModel
from src.start_panel.views.view_delete_buttons import DeleteButtonsDialog
from src.start_panel.view_models.view_model_delete_buttons import DeleteButtonsViewModel
from src.start_panel.view_models.view_model import ButtonViewModel, IButtonViewModel
import base64
import sys
from src.ui.customization_start_panel import CostStartPanel


class MainWindow(QMainWindow):
    def __init__(self, view_model: IButtonViewModel):

        """
            Инициализация главного окна панели управления кнопками.

            :param view_model: Экземпляр ViewModel, который управляет логикой отображения и взаимодействием с кнопками.

            Данный конструктор выполняет следующие действия:
            1. Вызывает конструктор суперкласса для инициализации базового окна.
            2. Сохраняет переданный view_model в качестве атрибута экземпляра для дальнейшего взаимодействия.
            3. Убирает стандартный заголовок окна и кнопки управления, делая окно безрамочным (FramelessWindowHint).
            4. Устанавливает фиксированную высоту окна (40 пикселей), чтобы панель имела компактный вид.
            5. Создаёт основной центральный виджет и назначает его центральным для окна.
            6. Организует основной горизонтальный layout с минимальными отступами и размещает его на центральном виджете.
            7. Создаёт дополнительный горизонтальный layout для размещения кнопок (панель кнопок) и добавляет его в основной layout.
            8. Добавляет кнопку "Добавить" с иконкой, загруженной из base64. При ошибке загрузки выводит сообщение в консоль.
               - Кнопка имеет фиксированный размер 30x30 пикселей.
               - Подключает обработчик add_button_clicked к сигналу нажатия.
            9. Инициализирует все пользовательские кнопки, вызвав метод update_buttons().
            10. Добавляет кнопку "Закрыть панель" с иконкой закрытия, загруженной из base64 либо стандартной, если загрузка не удалась.
                - Кнопка имеет фиксированный размер 30x30 пикселей.
                - Подключает обработчик close_panel к сигналу нажатия.
            11. Добавляет кнопку "Удалить" для удаления пользовательских кнопок, с иконкой из base64.
                - Кнопка имеет фиксированный размер 30x30 пикселей.
                - Подключает обработчик delete_button_clicked к сигналу нажатия.
                - Размещает кнопку сразу после кнопки "Добавить".
            12. Подписывается на сигнал buttonsChanged от view_model, чтобы автоматически обновлять панель кнопок при изменении их списка.
            13. Инициализирует переменные, необходимые для реализации перемещения окна мышью (dragging и offset).
            14. Устанавливает начальную позицию окна в верхней части экрана с помощью метода set_initial_position().
            """
            # TODO 🚧 В разработке: 04.08.2025
        super().__init__()
        self.view_model = view_model
        #self.setWindowTitle("Панель кнопок")
        
        # Убираем заголовок окна и кнопки управления
        self.setWindowFlags(Qt.FramelessWindowHint)

        # Устанавливаем фиксированную высоту окна (например, 40 пикселей)
        self.setFixedHeight(40)

        # Основной виджет
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Основной layout (горизонтальный)
        #self.main_layout = QVBoxLayout()
        self.main_layout = QHBoxLayout()
        self.main_layout.setSpacing(2)  # Уменьшаем отступ между кнопками
        self.main_layout.setContentsMargins(2, 2, 2, 2)  # Уменьшаем отступы вокруг layout
        self.central_widget.setLayout(self.main_layout)

        # Панель для кнопок 
        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.setSpacing(5)  # Устанавливаем отступ между кнопками
        self.main_layout.addLayout(self.buttons_layout)

        # Кнопка для добавления новой кнопки с иконкой
        self.add_button = QPushButton()
        icon = self.load_icon_from_base64(add_icon)
        if icon.isNull():
            print("Ошибка: Иконка не загружена!")
        else:
            self.add_button.setIcon(icon)
            # Устанавливаем размер кнопки (например, 30x30 пикселей)
            self.add_button.setFixedSize(30, 30)
            # Устанавливаем размер кнопки по размеру иконки
            #icon_size = icon.pixmap(icon.availableSizes()[0]).size()
            #self.add_button.setFixedSize(icon_size)
        self.add_button.clicked.connect(self.add_button_clicked)
        self.buttons_layout.addWidget(self.add_button)



        #Кнопка для открытия боковой панели side_panel
        self.side_panel = QPushButton()
        icon_side_panel = self.load_icon_from_base64(side_panel_icon)
        self.side_panel.setIcon(icon_side_panel)
        self.side_panel.setFixedSize(30, 30)
        self.side_panel.clicked.connect(self.open_side_panel)   # TODO 04.08.2025 - написать обработчик
        self.buttons_layout.insertWidget(2, self.side_panel)

        # Кнопка для Менеджера структуры проекта
        self.structure_manager = QPushButton()
        icon_structure_manager = self.load_icon_from_base64(sm_icon)
        self.structure_manager.setIcon(icon_structure_manager)
        self.structure_manager.setFixedSize(30, 30)
        self.structure_manager.clicked.connect(self.open_structure_manager_clicked) # TODO 04.08.2025 - написать обработчик
        self.buttons_layout.insertWidget(3, self.structure_manager)



        # Кнопка для удаления кнопок
        self.delete_button = QPushButton()
        delete_icon = self.load_icon_from_base64(delete_icon_base64)
        if delete_icon.isNull():
            print("Ошибка: Иконка не загружена!")
        else:
            self.delete_button.setIcon(delete_icon)
            self.delete_button.setFixedSize(30, 30)
        self.delete_button.clicked.connect(self.delete_button_clicked)
        self.buttons_layout.insertWidget(1, self.delete_button)  # Размещаем после кнопки "Добавить"



        # Кнопка "Закрыть панель"
        self.close_button = QPushButton()

        icon_cl = self.load_icon_from_base64(close_icon)
        if icon_cl.isNull():
            # Если иконка не загружена, используем стандартную иконку "Закрыть"
            icon_cl = self.style().standardIcon(QStyle.SP_DialogCloseButton)
        if not icon_cl.isNull():
            # Устанавливаем размер кнопки (например, 30x30 пикселей)
            self.close_button.setIcon(icon_cl)
            self.close_button.setFixedSize(30, 30)

        self.close_button.clicked.connect(self.close_panel)
        self.buttons_layout.addWidget( self.close_button)

        # Инициализация кнопок
        self.update_buttons()

        # Подписка на изменение списка кнопок
        self.view_model.buttonsChanged.connect(self.update_buttons)         # Подключаем сигнал buttonsChanged к методу update_buttons

        # Переменные для перемещения окна
        self.dragging = False
        self.offset = QPoint()

        # Устанавливаем начальную позицию окна вверху экрана
        self.set_initial_position()

    def add_button_clicked(self):
        """
        Обработчик события нажатия на кнопку "Добавить" в пользовательском интерфейсе.

        При активации этого метода отображаются два диалоговых окна для ввода пользователем:
        1. Названия новой кнопки.
        2. Пути к исполняемому файлу или программе.

        Если пользователь подтвердил оба ввода, введённые значения передаются в метод
        self.view_model.add_button для добавления новой кнопки с указанными параметрами
        в модель представления.

        Returns:
            None

        Side Effects:
            - Открывает два диалоговых окна для ввода текста.
            - Добавляет новую кнопку в модель представления при подтверждённом вводе.
        """
        name, ok1 = QInputDialog.getText(self, "Добавить кнопку", "Введите название:")
        path, ok2 = QInputDialog.getText(self, "Добавить кнопку", "Введите путь к программе:")
        if ok1 and ok2:
            self.view_model.add_button(name, path)

    def close_panel(self):
        """
        Обработчик нажатия на кнопку "Закрыть". Закрывает приложение.
        """
        self.close()

    def update_buttons(self):

        """
            Обновляет отображение пользовательских кнопок на панели в соответствии с актуальным состоянием ViewModel.

            Данный метод выполняет следующие действия:
            1. Очищает панель от всех пользовательских кнопок, оставляя только служебные кнопки "Добавить", "Удалить" и "Закрыть".
               - Для этого перебирает все виджеты в layout'е кнопок в обратном порядке и удаляет те, которые не являются служебными.
            2. Получает актуальный список кнопок из view_model с помощью метода get_buttons().
            3. Для каждой кнопки из списка:
               - Создаёт новый QPushButton с отображаемым именем кнопки.
               - Подключает сигнал нажатия этой кнопки к методу execute_program соответствующим индексом, чтобы по клику запускалась нужная программа.
               - Динамически рассчитывает ширину кнопки на основе длины текста её названия, чтобы текст полностью помещался и выглядел аккуратно, добавляя небольшой отступ.
               - Устанавливает фиксированную ширину кнопки.
               - Вставляет новую кнопку между кнопками "Удалить" и "Закрыть" (позиция i + 2, где i — индекс новой кнопки, 0 — "Добавить", 1 — "Удалить").
            4. После выполнения метода панель кнопок полностью соответствует текущему состоянию ViewModel: все пользовательские кнопки отображаются, служебные кнопки остаются на своих местах.
            """
        # TODO 🚧 В разработке: 04.08.2025
        # Очистка текущих кнопок (кроме кнопки "Добавить", "Удалить","Боковая панель" ,"Менеджер структуры" и "Закрыть")
        for i in reversed(range(self.buttons_layout.count())):
            widget = self.buttons_layout.itemAt(i).widget()
            if (widget != self.add_button and
                    widget != self.delete_button and
                    widget != self.close_button and
                    widget != self.side_panel and
                    widget != self.structure_manager):
                widget.setParent(None)

        # Добавление новых кнопок между "Менеджер структуры" и "Закрыть"
        buttons = self.view_model.get_buttons()
        for i, button in enumerate(buttons):
            btn = QPushButton(button.name)
            btn.clicked.connect(lambda checked, idx=i: self.view_model.execute_program(idx))

            # Устанавливаем ширину кнопки в зависимости от длины текста
            font_metrics = btn.fontMetrics() #возвращает метрики шрифта, используемого в кнопке.
            text_width = font_metrics.horizontalAdvance(button.name) + 10  # вычисляет ширину текста кнопки + Добавляем небольшой отступ
            btn.setFixedWidth(text_width) #устанавливает ширину кнопки на основе ширины текста, добавляя небольшой отступ для удобства.

            self.buttons_layout.insertWidget(4 + i, btn)  # Вставляем кнопки после "Менеджер структуры"

    def load_icon_from_base64(self, base64_data: str) -> QIcon:
        """
        Загружает иконку из строки в формате base64.

        :param base64_data: Строка с данными иконки в формате base64.
        :return: Объект QIcon, если загрузка прошла успешно, иначе пустая иконка.
        """
        # Декодирование base64 и создание QIcon
        if not base64_data:
            return QIcon()  # Возвращаем пустую иконку, если строка пустая
        try:
            # Добавляем символы заполнения, если длина строки не кратна 4
            padding = len(base64_data) % 4
            if padding:
                base64_data += "=" * (4 - padding)
            icon_data = base64.b64decode(base64_data)
            pixmap = QPixmap()
            pixmap.loadFromData(icon_data)
            if pixmap.isNull():
                print("Ошибка: Не удалось загрузить изображение из base64!")
            return QIcon(pixmap)
        except Exception as e:
            print(f"Ошибка при декодировании base64: {e}")
            return QIcon()

    # Обработка событий мыши для перемещения окна
    def mousePressEvent(self, event):
        """
        Обработчик события нажатия кнопки мыши. Начинает перемещение окна, если нажата левая кнопка мыши.
        """
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.globalPosition().toPoint() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        """
        Обработчик события перемещения мыши. Перемещает окно, если происходит перетаскивание.
        """
        if self.dragging:
            self.move(event.globalPosition().toPoint() - self.offset)
            event.accept()

    def mouseReleaseEvent(self, event):
        """
        Обработчик события отпускания кнопки мыши. Завершает перемещение окна.
        """
        if event.button() == Qt.LeftButton:
            self.dragging = False
            event.accept()
    def set_initial_position(self):
        """
        Устанавливает начальную позицию окна вверху экрана по центру.
        """
        # Получаем размеры экрана
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()

        # Рассчитываем позицию окна вверху экрана по центру
        x = (screen_geometry.width() - self.width()) // 2
        y = 0  # Верхняя часть экрана

        # Устанавливаем позицию окна
        self.move(x, y)        
    def closeEvent(self, event):
        """
        Обработчик события закрытия окна.
        Сохраняет кнопки перед выходом.
        """
        self.view_model.save_buttons()  # Сохраняем кнопки
        event.accept()  # Подтверждаем закрытие окна

    def delete_button_clicked(self):
        """
        Обработчик нажатия на кнопку "Удалить".
        """
        # Создаем модель, ViewModel и диалог
        view_model = DeleteButtonsViewModel(self.view_model._model)  # Передаем ButtonListModel
        dialog = DeleteButtonsDialog(view_model, self)
        # Показываем диалог
        if dialog.exec() == QDialog.Accepted:
            # Удаляем отмеченные кнопки
            selected_indices = dialog.get_selected_indices()  # TODO определен как мертвый код ПРОВЕРИТЬ
            self.view_model.remove_button(selected_indices)

    # Обработчик нажатия на кнопку Открыть Менеджер структуры проекта
    def open_structure_manager_clicked(self):
        """Открыть окно Менеджера структуры проекта"""
        #TODO 🚧 В разработке: 04.08.2025
        if not hasattr(self,'_structure_manager_window'):
            self._structure_manager_window = CostStartPanel()

        self._structure_manager_window.show()

    # Обработчик нажатия на кнопку Открыть боковую панель
    def open_side_panel(self):
        #TODO 🚧 В разработке: 04.08.2025
        pass

# Иконка в формате base64
add_icon = b'iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAACXBIWXMAAAsTAAALEwEAmpwYAAACVklEQVR4nO1ZvW4TQRBeQaCgJFDx8xIRUVK5Q5F20MwVJxD0vAIojbuEPkROxBsY3YzkAA0FzwCCB4CkIj91jgY0Z8cSVpD3btd3e+g+aSVLJ9vfNzuz+82cMR06dPBGOkyvAtO6FdwEwcwyfQOmMxD8VSymM8v0tXgmuPkoS9b6/f4V0zRQ8B4wvQKmIxD6XW7hoRXc3siSu7UT3ximt0Fo3wrm5Yn/vaxgbgUHMIJbtZAHwacgeOpL/BIhJzZLniyM+Mr+82uW6U1o4jArhGlP/ysoeRjBDSv4YdHk4WIxvdf/DBf5OsnLVMTHdJhe9xZQR9rAv+ti4Ec+S541RR6mCx9XIk9My5bpOAIBp5WOWD3nmydP41Ri2i1FXm9H30tqFp61kMMI7rtHX+2BZ9RCCoCxiG0n8mqy1KfEJgCYjtQ0ukR/PUTeBhcgRS2szhUwtsRxCgCmly47wBELeDt/B4rGI1oBX+bvQAmrHArgXgPHLjWQxyoAmM7/fwHQ+hTithcxt/0YlXgvMiv4Yq4AHTrFKgCy5IGTmbNMP2ITYJm+O0/z1LrGJgAEt0xbGxpgOrcH9o6zgMkuDILkbZCFO6YsHg7TmzE09VbwpPLcVGeVjQvgJK1EfiqCaa/B6L82vtA+1DJJA3n/rvept2RCQAetxcC1vsgfBBvuzgx5B3WkTS9U5C+DzioXczrhT++CLTk33dULxps462/gjh7bpm7o7ai2o4p3Gn8Ht0rfsIvAxACu6txGPbs2HtrZTV7g5cVnps/6TC2xusooXrN26GDajz+jYGvHi7pQwQAAAABJRU5ErkJggg=='  
close_icon = b'iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAACXBIWXMAAAsTAAALEwEAmpwYAAAB7ElEQVR4nO2Z3UrDMBTH81Amft01012oCOKt+BAqKA4miCJ44Y0PIIj4id6IdzrfwyFDbzargjYbrZVFWely2dZ1bI6dTdMkHeQP525l/1/OyTlpA4CWlpZWplXHaJYY6N4yECEYURlh+f5lwFLdGJrhMm9hdCPLNIkCwXAr+cortk7aAaeZAbyyyRDAHTsAhlbGAD4TAKg2jbpCA5Co1cmPUVJYHtAM5Mfp9801dU+PmCHswgof6gBa5qn57gcLhL2+RGrVpLT2Su2NNTUAzulx23wQX4cH/0K0zQfP1eJBpA7QWNijzYdyD0S/TPSYN1sAxVU1e4AFgsc8EdlG4wDwmicix0A/CLuwzG2eyBhkURD05Y3bPJE1iSMhOM0TmUcJHyLzFJoJu5iv5xOVAP6Gbf2p+WBPnLBPbCITILTbpAQBRANEtcpm5TkVCBASoF+fj2yxjBBAFECcIZUGBBABwDJheSFA2gBJjgeNxXnaLD+Gn2KxZAD36qLbSNWM9YISlgnnYE9BCU2MUHd4nmjCdkI4McyL28STo34mWF4NO8vJ2d2O/XsxABIDaAA8cBmAuXm0aMAPdgADlpQbx0HAW2YA73JBvXH0Gzk0BZLIu1xQbd4y0CbgkXe54H2fl7snoOWVTeKV19LS0gKy9MMZ6sLzJV+oAgAAAABJRU5ErkJggg=='  
delete_icon_base64 = b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAMAAABEpIrGAAAABGdBTUEAALGPC/xhBQAAAAFzUkdCAK7OHOkAAAAgY0hSTQAAeiYAAICEAAD6AAAAgOgAAHUwAADqYAAAOpgAABdwnLpRPAAAASxQTFRFAAAAE0VjE0diFENfFENjFUFiE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjEkVjE0VkFEVjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjFEVjE0VjE0VjE0VjE0VjE0VjE0ViFEViE0VjE0VjE0VjE0VjE0VjE0VjE0Vj////l/Ph8QAAAGN0Uk5TAAAAAAAACR0eJKzi46sjiOByaIIBFx+yHBoIquXh9fQETpH7qGtqNfEg5G2DigVzCpgOzZrEwxKpAgIEscgLmd8ZB96L7S4GZ/c/S/JIZDHvaW9QARuODMqjAQGh658CIuagHkS+7gAAAAFiS0dEY1y+LaoAAAAJcEhZcwAAbroAAG66AdbesRcAAAFmSURBVDjLvdNpU4JAGAfwng5AoVRSVATFC6/SPDPzKEtRPMtIK7Xs+3+IyJFANl/Wf57ZgeW3zM7ysLf3vwEMJwgcg53PLVaSosjjkx1iH2x2B0077KdwYF7qdDGEGqvb4/V63Nbva8bl1F8ErI/jSZL0B9SBDPjVged8rAEIwVA4QkdFMapGHelIOBQUjFuBWFw03IMYj23vFBLJlBGccQkTwMlzSGcyF+tKQ5bCTSCXLwBWLF2W1CpiUMjnTAArlq90UCkXTecJ19USy2qAZUtVYRscQqFW10G9VoAj02E2bm6bGmh670Lm7wH3SUIHBOVAQKrVljQgtVsiAjpdOa2BtNztIKDXH+hg0O8hQO4OBQ0Iw66MgNH4QQfR8QgBDPUIk0lzXU82jkGAYn/+mYMsryBgOnt53UzC23w2RUClsVhmN1kuGu9IZ8PHnF9x66z4T8svnQ+Ssm5ttaEVaee/8xf5Amp3QStp66SNAAAAJXRFWHRkYXRlOmNyZWF0ZQAyMDE3LTAxLTI2VDE5OjQxOjQ5KzAxOjAwowDHmgAAACV0RVh0ZGF0ZTptb2RpZnkAMjAxNy0wMS0yNlQxOTo0MTo0OSswMTowMNJdfyYAAABGdEVYdHNvZnR3YXJlAEltYWdlTWFnaWNrIDYuNy44LTkgMjAxNi0wNi0xNiBRMTYgaHR0cDovL3d3dy5pbWFnZW1hZ2ljay5vcmfmvzS2AAAAGHRFWHRUaHVtYjo6RG9jdW1lbnQ6OlBhZ2VzADGn/7svAAAAGHRFWHRUaHVtYjo6SW1hZ2U6OmhlaWdodAA1MTLA0FBRAAAAF3RFWHRUaHVtYjo6SW1hZ2U6OldpZHRoADUxMhx8A9wAAAAZdEVYdFRodW1iOjpNaW1ldHlwZQBpbWFnZS9wbmc/slZOAAAAF3RFWHRUaHVtYjo6TVRpbWUAMTQ4NTQ1NjEwOaMgI94AAAARdEVYdFRodW1iOjpTaXplADEwS0JC22lQBQAAAFB0RVh0VGh1bWI6OlVSSQBmaWxlOi8vLi91cGxvYWRzL2Nhcmxvc3ByZXZpL1lla2xmM3YvMTA5Ny8xNDg1NDc3MTA0LWJhc2tldF83ODU5MS5wbmcJhlfCAAAAAElFTkSuQmCC'
sm_icon = b'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'
side_panel_icon = b'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'
if __name__ == "__main__":
    app = QApplication([])

    # Создаем Model
    model = ButtonListModel()

    # Создаем ViewModel и передаем ей Model
    view_model = ButtonViewModel(model)

    # Создаем View и передаем ему ViewModel
    window = MainWindow(view_model)
    window.show()

    sys.exit(app.exec())