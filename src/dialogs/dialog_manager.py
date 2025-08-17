from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import QTimer
from typing import Optional
from enum import Enum, auto


class MessageType(Enum):
    INFO = auto()      # Информационные сообщения (нейтральные)
    WARNING = auto()   # Предупреждения (потенциальные проблемы)
    ERROR = auto()     # Ошибки (критические проблемы)
    SUCCESS = auto()   # Сообщения об успешном выполнении

class DialogManager:
    """Класс для управления диалоговыми окнами с пользователем"""

    # TODO 🚧 В разработке: 03.08.2025 - нужно проверить работу и протестировать
        #task:  Диалог с пользователем
    def __init__(self, parent_window=None, console_output: bool = True, gui_output: bool = False):
        """
        :param console_output: вывод в консоль
        :param gui_output: вывод в GUI (если доступно)
        :param parent_window: родительское окно для модальных диалогов
        """
        # TODO 🚧 В разработке: 03.08.2025 - нужно проверить работу и протестировать
        self.parent_window = parent_window
        self.console_output = console_output
        self.gui_output = gui_output

    def show_message(
            self,
            message: str,
            msg_type: MessageType = MessageType.INFO,
            details: Optional[str] = None,
            exception: Optional[Exception] = None,
            timeout_ms: Optional[int] = None
    ) -> None:
        """
        Основной метод для показа сообщений пользователю

        :param message: основное сообщение
        :param msg_type: тип сообщения (из enum MessageType)
        :param details: дополнительные детали (опционально)
        :param exception: связанное исключение (опционально)
        """
        # TODO 🚧 В разработке: 03.08.2025 - нужно проверить работу и протестировать
        if self.console_output:
            self._console_output(message, msg_type, details, exception)

        if self.gui_output:
            self._gui_output(message, msg_type, details, exception,timeout_ms)

    def _console_output(
            self,
            message: str,
            msg_type: MessageType,
            details: Optional[str],
            exception: Optional[Exception]
    ) -> None:
        """Вывод сообщения в консоль"""
        prefix = {
            MessageType.INFO: "[INFO]",
            MessageType.WARNING: "[WARNING]",
            MessageType.ERROR: "[ERROR]",
            MessageType.SUCCESS: "[SUCCESS]"
        }.get(msg_type, "[INFO]")

        print(f"{prefix} {message}")
        if details:
            print(f"Детали: {details}")
        if exception:
            print(f"Исключение: {str(exception)}")

    def _gui_output(
            self,
            message: str,
            msg_type: MessageType,
            details: Optional[str],
            exception: Optional[Exception],
            timeout_ms: Optional[int] = None
    ) -> None:
        """Вывод сообщения в GUI (заглушка для реализации)"""
        # TODO 🚧 В разработке: 03.08.2025 - нужно проверить работу и протестировать

        # Реализация будет зависеть от используемого GUI-фреймворка
        msg_box = QMessageBox(self.parent_window)

        # Установка текста
        msg_box.setText(message)

        # Настройка типа сообщения
        if msg_type == MessageType.INFO:
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setWindowTitle("Информация")
        elif msg_type == MessageType.WARNING:
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setWindowTitle("Предупреждение")
        elif msg_type == MessageType.ERROR:
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle("Ошибка")
        elif msg_type == MessageType.SUCCESS:
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setWindowTitle("Успех")
            msg_box.setStyleSheet("""
                    QMessageBox { background-color: #e8f5e9; }
                    QLabel { color: #2e7d32; }
                """)

        # Добавление деталей и информации об исключении
        full_details = []  # ?
        if details:
            full_details.append(details)
        if exception:
            full_details.append(f"Исключение: {str(exception)}")

        if full_details:
            msg_box.setDetailedText("\n\n".join(full_details))

        # Добавление таймера для автоматического закрытия
        if timeout_ms is not None and timeout_ms > 0:
            timer = QTimer(msg_box)
            timer.setSingleShot(True)
            timer.timeout.connect(msg_box.close)
            timer.start(timeout_ms)
        # Показ диалога
        msg_box.exec()

    # Специализированные методы для удобства
    def show_info(self, message: str, details: Optional[str] = None, timeout_ms: Optional[int] = None) -> None:
        """Показать информационное сообщение"""
        # TODO 🚧 В разработке: 03.08.2025 - нужно проверить работу и протестировать
        self.show_message(message, MessageType.INFO, details,timeout_ms)

    def show_warning(self, message: str, details: Optional[str] = None, timeout_ms: Optional[int] = None) -> None:
        """Показать предупреждение"""
        # TODO 🚧 В разработке: 03.08.2025 - нужно проверить работу и протестировать
        self.show_message(message, MessageType.WARNING, details, timeout_ms)

    def show_error(
            self,
            message: str,
            details: Optional[str] = None,
            exception: Optional[Exception] = None,
            timeout_ms: Optional[int] = None
    ) -> None:
        """Показать ошибку"""
        # TODO 🚧 В разработке: 03.08.2025 - нужно проверить работу и протестировать
        self.show_message(message, MessageType.ERROR, details, exception, timeout_ms)

    def show_success(self, message: str, details: Optional[str] = None, timeout_ms: Optional[int] = None) -> None:
        """Показать сообщение об успехе"""
        # TODO 🚧 В разработке: 03.08.2025 - нужно проверить работу и протестировать
        self.show_message(message, MessageType.SUCCESS, details,timeout_ms)

    def show_question(
            self,
            question: str,
            title: str = "Подтверждение",
            default_button: QMessageBox.StandardButton = QMessageBox.StandardButton.No,
            timeout_ms: Optional[int] = None
    ) -> bool:
        """
        Показать диалог с вопросом (Да/Нет)

        :param question: текст вопроса
        :param title: заголовок окна
        :param default_button: кнопка по умолчанию (Yes/No)
        :return: True если пользователь выбрал "Да", False если "Нет"
        """
        # TODO 🚧 В разработке: 03.08.2025 - нужно проверить работу и протестировать
        if not self.gui_output:
            if self.console_output:
                print(
                    f"[QUESTION] {question} (ответ: {'Да' if default_button == QMessageBox.StandardButton.Yes else 'Нет'})")
            return default_button == QMessageBox.StandardButton.Yes

        msg_box = QMessageBox(self.parent_window)
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setWindowTitle(title)
        msg_box.setText(question)
        msg_box.setStandardButtons(
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )
        msg_box.setDefaultButton(default_button)

        # Добавление таймера для автоматического закрытия
        if timeout_ms is not None and timeout_ms > 0:
            timer = QTimer(msg_box)
            timer.setSingleShot(True)
            timer.timeout.connect(msg_box.close)
            timer.start(timeout_ms)

        result = msg_box.exec()
        return result == QMessageBox.StandardButton.Yes