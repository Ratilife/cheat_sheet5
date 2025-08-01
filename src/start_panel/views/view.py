from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QInputDialog, QHBoxLayout, QStyle, QDialog
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import QByteArray, QBuffer, QIODevice, QSize, Qt, QPoint
from src.start_panel.models.model import ButtonListModel
from src.start_panel.views.view_delete_buttons import DeleteButtonsDialog
from src.start_panel.view_models.view_model_delete_buttons import DeleteButtonsViewModel
from src.start_panel.view_models.view_model import ButtonViewModel, IButtonViewModel
import base64
import sys

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

        # Инициализация кнопок
        self.update_buttons()

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
        self.buttons_layout.addWidget(self.close_button)

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
        # Очистка текущих кнопок (кроме кнопки "Добавить", "Удалить" и "Закрыть")
        for i in reversed(range(self.buttons_layout.count())):
            widget = self.buttons_layout.itemAt(i).widget()
            if widget != self.add_button and widget != self.delete_button and widget != self.close_button:
                widget.setParent(None)

        # Добавление новых кнопок между "Добавить" и "Закрыть"
        buttons = self.view_model.get_buttons()
        for i, button in enumerate(buttons):
            btn = QPushButton(button.name)
            btn.clicked.connect(lambda checked, idx=i: self.view_model.execute_program(idx))

            # Устанавливаем ширину кнопки в зависимости от длины текста
            font_metrics = btn.fontMetrics() #возвращает метрики шрифта, используемого в кнопке.
            text_width = font_metrics.horizontalAdvance(button.name) + 10  # вычисляет ширину текста кнопки + Добавляем небольшой отступ
            btn.setFixedWidth(text_width) #устанавливает ширину кнопки на основе ширины текста, добавляя небольшой отступ для удобства.

            self.buttons_layout.insertWidget(i + 2, btn)  # Вставляем кнопки после "Удалить"

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

# Иконка в формате base64
add_icon = b'iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAACXBIWXMAAAsTAAALEwEAmpwYAAACVklEQVR4nO1ZvW4TQRBeQaCgJFDx8xIRUVK5Q5F20MwVJxD0vAIojbuEPkROxBsY3YzkAA0FzwCCB4CkIj91jgY0Z8cSVpD3btd3e+g+aSVLJ9vfNzuz+82cMR06dPBGOkyvAtO6FdwEwcwyfQOmMxD8VSymM8v0tXgmuPkoS9b6/f4V0zRQ8B4wvQKmIxD6XW7hoRXc3siSu7UT3ximt0Fo3wrm5Yn/vaxgbgUHMIJbtZAHwacgeOpL/BIhJzZLniyM+Mr+82uW6U1o4jArhGlP/ysoeRjBDSv4YdHk4WIxvdf/DBf5OsnLVMTHdJhe9xZQR9rAv+ti4Ec+S541RR6mCx9XIk9My5bpOAIBp5WOWD3nmydP41Ri2i1FXm9H30tqFp61kMMI7rtHX+2BZ9RCCoCxiG0n8mqy1KfEJgCYjtQ0ukR/PUTeBhcgRS2szhUwtsRxCgCmly47wBELeDt/B4rGI1oBX+bvQAmrHArgXgPHLjWQxyoAmM7/fwHQ+hTithcxt/0YlXgvMiv4Yq4AHTrFKgCy5IGTmbNMP2ITYJm+O0/z1LrGJgAEt0xbGxpgOrcH9o6zgMkuDILkbZCFO6YsHg7TmzE09VbwpPLcVGeVjQvgJK1EfiqCaa/B6L82vtA+1DJJA3n/rvept2RCQAetxcC1vsgfBBvuzgx5B3WkTS9U5C+DzioXczrhT++CLTk33dULxps462/gjh7bpm7o7ai2o4p3Gn8Ht0rfsIvAxACu6txGPbs2HtrZTV7g5cVnps/6TC2xusooXrN26GDajz+jYGvHi7pQwQAAAABJRU5ErkJggg=='  
close_icon = b'iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAACXBIWXMAAAsTAAALEwEAmpwYAAAB7ElEQVR4nO2Z3UrDMBTH81Amft01012oCOKt+BAqKA4miCJ44Y0PIIj4id6IdzrfwyFDbzargjYbrZVFWely2dZ1bI6dTdMkHeQP525l/1/OyTlpA4CWlpZWplXHaJYY6N4yECEYURlh+f5lwFLdGJrhMm9hdCPLNIkCwXAr+cortk7aAaeZAbyyyRDAHTsAhlbGAD4TAKg2jbpCA5Co1cmPUVJYHtAM5Mfp9801dU+PmCHswgof6gBa5qn57gcLhL2+RGrVpLT2Su2NNTUAzulx23wQX4cH/0K0zQfP1eJBpA7QWNijzYdyD0S/TPSYN1sAxVU1e4AFgsc8EdlG4wDwmicix0A/CLuwzG2eyBhkURD05Y3bPJE1iSMhOM0TmUcJHyLzFJoJu5iv5xOVAP6Gbf2p+WBPnLBPbCITILTbpAQBRANEtcpm5TkVCBASoF+fj2yxjBBAFECcIZUGBBABwDJheSFA2gBJjgeNxXnaLD+Gn2KxZAD36qLbSNWM9YISlgnnYE9BCU2MUHd4nmjCdkI4McyL28STo34mWF4NO8vJ2d2O/XsxABIDaAA8cBmAuXm0aMAPdgADlpQbx0HAW2YA73JBvXH0Gzk0BZLIu1xQbd4y0CbgkXe54H2fl7snoOWVTeKV19LS0gKy9MMZ6sLzJV+oAgAAAABJRU5ErkJggg=='  
delete_icon_base64 = b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAMAAABEpIrGAAAABGdBTUEAALGPC/xhBQAAAAFzUkdCAK7OHOkAAAAgY0hSTQAAeiYAAICEAAD6AAAAgOgAAHUwAADqYAAAOpgAABdwnLpRPAAAASxQTFRFAAAAE0VjE0diFENfFENjFUFiE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjEkVjE0VkFEVjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjE0VjFEVjE0VjE0VjE0VjE0VjE0VjE0ViFEViE0VjE0VjE0VjE0VjE0VjE0VjE0Vj////l/Ph8QAAAGN0Uk5TAAAAAAAACR0eJKzi46sjiOByaIIBFx+yHBoIquXh9fQETpH7qGtqNfEg5G2DigVzCpgOzZrEwxKpAgIEscgLmd8ZB96L7S4GZ/c/S/JIZDHvaW9QARuODMqjAQGh658CIuagHkS+7gAAAAFiS0dEY1y+LaoAAAAJcEhZcwAAbroAAG66AdbesRcAAAFmSURBVDjLvdNpU4JAGAfwng5AoVRSVATFC6/SPDPzKEtRPMtIK7Xs+3+IyJFANl/Wf57ZgeW3zM7ysLf3vwEMJwgcg53PLVaSosjjkx1iH2x2B0077KdwYF7qdDGEGqvb4/V63Nbva8bl1F8ErI/jSZL0B9SBDPjVged8rAEIwVA4QkdFMapGHelIOBQUjFuBWFw03IMYj23vFBLJlBGccQkTwMlzSGcyF+tKQ5bCTSCXLwBWLF2W1CpiUMjnTAArlq90UCkXTecJ19USy2qAZUtVYRscQqFW10G9VoAj02E2bm6bGmh670Lm7wH3SUIHBOVAQKrVljQgtVsiAjpdOa2BtNztIKDXH+hg0O8hQO4OBQ0Iw66MgNH4QQfR8QgBDPUIk0lzXU82jkGAYn/+mYMsryBgOnt53UzC23w2RUClsVhmN1kuGu9IZ8PHnF9x66z4T8svnQ+Ssm5ttaEVaee/8xf5Amp3QStp66SNAAAAJXRFWHRkYXRlOmNyZWF0ZQAyMDE3LTAxLTI2VDE5OjQxOjQ5KzAxOjAwowDHmgAAACV0RVh0ZGF0ZTptb2RpZnkAMjAxNy0wMS0yNlQxOTo0MTo0OSswMTowMNJdfyYAAABGdEVYdHNvZnR3YXJlAEltYWdlTWFnaWNrIDYuNy44LTkgMjAxNi0wNi0xNiBRMTYgaHR0cDovL3d3dy5pbWFnZW1hZ2ljay5vcmfmvzS2AAAAGHRFWHRUaHVtYjo6RG9jdW1lbnQ6OlBhZ2VzADGn/7svAAAAGHRFWHRUaHVtYjo6SW1hZ2U6OmhlaWdodAA1MTLA0FBRAAAAF3RFWHRUaHVtYjo6SW1hZ2U6OldpZHRoADUxMhx8A9wAAAAZdEVYdFRodW1iOjpNaW1ldHlwZQBpbWFnZS9wbmc/slZOAAAAF3RFWHRUaHVtYjo6TVRpbWUAMTQ4NTQ1NjEwOaMgI94AAAARdEVYdFRodW1iOjpTaXplADEwS0JC22lQBQAAAFB0RVh0VGh1bWI6OlVSSQBmaWxlOi8vLi91cGxvYWRzL2Nhcmxvc3ByZXZpL1lla2xmM3YvMTA5Ny8xNDg1NDc3MTA0LWJhc2tldF83ODU5MS5wbmcJhlfCAAAAAElFTkSuQmCC'

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