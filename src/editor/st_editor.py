# Редактор для .st файлов
from pathlib import Path
from typing import Optional
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit

from observers.file_watcher import FileWatcher
from src.editor.base_editor import BaseFileEditor
from PySide6.QtCore import Signal
class STEditor(BaseFileEditor):
    # Новые сигналы для работы с FileWatcher
    external_update_detected = Signal(str)  # Обнаружено внешнее изменение
    file_conflict_detected = Signal(str, str)  # Конфликт изменений (наш, внешний)
    file_became_readonly = Signal(str)  # Файл стал доступен только для чтения
    watching_status_changed = Signal(bool)  # Изменение статуса отслеживания

    def __init__(self, parent: Optional[QWidget] = None, file_watcher: Optional[FileWatcher] = None):
        super().__init__(parent=parent)
        # Сохраняем переданный FileWatcher или создаем новый
        self._file_watcher = file_watcher or FileWatcher()

        # Основной текстовый редактор (пока простой QTextEdit)
        self._text_edit = None

        # Флаг включенного отслеживания
        self._watching_enabled = False

        # Инициализируем UI и соединения
        self._init_ui()
        self._setup_connections()

        # Устанавливаем начальное состояние
        self._update_watching_state(False)  # По умолчанию отслеживание выключено

    def _init_ui(self) -> None:
        """Инициализация пользовательского интерфейса"""
        # Основной layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Создаем текстовый редактор
        self._text_edit = QTextEdit()
        self._text_edit.setAcceptRichText(False)  # Режим plain text

        # TODO: Здесь позже добавим подсветку синтаксиса
        # self._highlighter = STHighlighter(self._text_edit.document())

        # Добавляем редактор в layout
        layout.addWidget(self._text_edit)

        # Устанавливаем layout
        self.setLayout(layout)

    def _setup_connections(self) -> None:
        """Настройка сигналов и соединений"""
        # Подключаем FileWatcher
        self._connect_file_watcher()

        # Подключаем сигналы текстового редактора
        self._text_edit.textChanged.connect(self._on_viewer_text_changed)

    def _update_watching_state(self, enabled: bool) -> None:
        """
        Обновляет состояние отслеживания и испускает сигнал

        Args:
            enabled: Включено ли отслеживание
        """
        self._watching_enabled = enabled
        self.watching_status_changed.emit(enabled)

    def get_editor_widget(self) -> QWidget:
        """
        Возвращает виджет редактора для встраивания в UI.
        Переопределяем метод базового класса.

        Returns:
            QWidget: Виджет редактора
        """
        return self

    def set_file_watcher(self, file_watcher: FileWatcher) -> None:
        """
        Устанавливает FileWatcher для отслеживания изменений файлов.

        Args:
            file_watcher: Экземпляр FileWatcher для отслеживания
        """
        if self._file_watcher:
            # Отключаем старые соединения если watcher уже был установлен
            self._disconnect_file_watcher()

        self._file_watcher = file_watcher
        self._connect_file_watcher()

        # Если уже есть открытый файл - начинаем отслеживать его
        if self.file_path and self._watching_enabled:
            self._start_watching_file()

    def _connect_file_watcher(self) -> None:
        """Подключает сигналы FileWatcher к обработчикам"""
        if self._file_watcher:
            self._file_watcher.debounced_file_updated.connect(self._process_external_update)
            self._file_watcher.file_deleted.connect(self._on_external_file_deleted)
            self._file_watcher.dir_changed.connect(self._on_directory_changed)
            self._file_watcher.watching_paused.connect(self._on_watching_paused)

    def _disconnect_file_watcher(self) -> None:
        """Отключает сигналы FileWatcher"""
        if self._file_watcher:
            try:
                self._file_watcher.debounced_file_updated.disconnect(self._process_external_update)
                self._file_watcher.file_deleted.disconnect(self._on_external_file_deleted)
                self._file_watcher.dir_changed.disconnect(self._on_directory_changed)
                self._file_watcher.watching_paused.disconnect(self._on_watching_paused)
            except RuntimeError:
                # Игнорируем ошибки если сигналы не были подключены
                pass

    def _start_watching_file(self) -> None:
        """Начинает отслеживание текущего файла"""
        if self._file_watcher and self.file_path and self._watching_enabled:
            file_path_str = str(self.file_path)
            # Отслеживаем сам файл и его директорию
            self._file_watcher.watch_file(file_path_str)
            self._file_watcher.watch_directory(str(self.file_path.parent))
            print(f"DEBUG: Начато отслеживание файла {file_path_str}")

    def _stop_watching_file(self) -> None:
        """Прекращает отслеживание текущего файла"""
        if self._file_watcher and self.file_path:
            file_path_str = str(self.file_path)
            self._file_watcher.remove_path(file_path_str)
            print(f"DEBUG: Прекращено отслеживание файла {file_path_str}")

    def _process_external_update(self, file_path: str) -> None:
        """
        Обрабатывает внешнее изменение файла после дебаунсинга

        Args:
            file_path: Путь к измененному файлу
        """
        if Path(file_path) != self.file_path:
            return  # Не наш файл

        try:
            # Читаем внешнее содержимое
            with open(file_path, 'r', encoding='utf-8') as f:
                external_content = f.read()

            # Сравниваем с текущими данными редактора
            current_content = self.get_content()

            if current_content == external_content:
                return  # Содержимое одинаковое - ложное срабатывание

            elif not self.is_modified:
                # Мы не редактировали - автоматически обновляем
                self.set_content(external_content)
                self.external_update_detected.emit("Файл обновлен внешней программой")

            else:
                # КОНФЛИКТ: мы редактируем и файл изменен извне
                self.file_conflict_detected.emit(current_content, external_content)

        except Exception as e:
            self.error_occurred.emit(f"Ошибка обработки внешнего изменения: {e}", "warning")

    def _on_external_file_deleted(self, file_path: str) -> None:
        """
        Обработчик сигнала удаления файла из FileWatcher.

        Args:
            file_path: Путь к удаленному файлу
        """
        if Path(file_path) == self.file_path:
            self.file_became_readonly.emit(file_path)

    def _on_directory_changed(self, dir_path: str) -> None:
        """
        Обработчик сигнала изменения директории из FileWatcher.

        Args:
            dir_path: Путь к измененной директории
        """
        # Можно использовать для обновления связанных файлов
        print(f"DEBUG: Изменения в директории {dir_path}")

    def _on_viewer_text_changed(self) -> None:
        """
        Обработчик изменения текста в редакторе.
        Устанавливает флаг модификации и обновляет состояние.
        """
        self.is_modified = True

    def _on_watching_paused(self, paused: bool) -> None:
        """
        Обработчик изменения статуса паузы отслеживания

        Args:
            paused: True если отслеживание приостановлено
        """
        # Можно использовать для обновления UI
        status = "приостановлено" if paused else "возобновлено"
        print(f"DEBUG: Отслеживание {status}")

    def save(self) -> bool:
        """
        Сохраняет содержимое редактора в текущий файл.

        Returns:
            bool: True если сохранение прошло успешно, False в противном случае
        """
        if not self.file_path:
            # Если файла нет, ведем себя как save_as()
            return self.save_as()

        try:
            # Временно приостанавливаем отслеживание
            self._file_watcher.pause(3000)  # Пауза на 3 секунды

            # Получаем содержимое из редактора
            content = self.get_content()

            # Сохраняем в файл
            with open(self.file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            # Сбрасываем флаг модификации
            self.is_modified = False

            return True

        except Exception as e:
            self.error_occurred.emit(f"Ошибка сохранения файла: {e}", "error")
            return False

    def save_as(self, new_file_path: Path = None) -> bool:
        """
        Сохраняет содержимое редактора в новый файл.

        Args:
            new_file_path: Новый путь для сохранения

        Returns:
            bool: True если сохранение прошло успешно, False в противном случае
        """
        # TODO: В реальной реализации нужно запрашивать путь у пользователя
        if new_file_path is None:
            # Временная заглушка - сохраняем в тот же путь с суффиксом
            if self.file_path:
                new_file_path = self.file_path.with_suffix('.copy.st')
            else:
                self.error_occurred.emit("Не указан путь для сохранения", "error")
                return False

        try:
            # Прекращаем отслеживание старого файла
            if self.file_path:
                self._stop_watching_file()

            # Получаем содержимое из редактора
            content = self.get_content()

            # Сохраняем в новый файл
            with open(new_file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            # Обновляем путь и начинаем отслеживание нового файла
            self._file_path = new_file_path
            self._start_watching_file()

            # Сбрасываем флаг модификации
            self.is_modified = False

            # Испускаем сигнал о сохранении под новым именем
            self.file_saved_as.emit(new_file_path)

            return True

        except Exception as e:
            self.error_occurred.emit(f"Ошибка сохранения файла: {e}", "error")
            return False

    def get_content(self) -> str:
        """
        Возвращает текущее содержимое редактора.

        Returns:
            str: Текстовое содержимое редактора
        """
        return self._text_edit.toPlainText()

    def set_content(self, content: str) -> None:
        """
        Устанавливает содержимое редактора из строки.

        Args:
            content: Содержимое для отображения
        """
        self._text_edit.setPlainText(content)
        # Сбрасываем флаг модификации при установке нового содержимого
        self.is_modified = False

    # Дополнительные методы для работы с файлами
    def load(self, file_path: Path) -> bool:
        """
        Загружает содержимое файла в редактор.
        Реализация абстрактного метода BaseFileEditor.

        Args:
            file_path: Путь к файлу для загрузки

        Returns:
            bool: True если загрузка прошла успешно
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            self._file_path = file_path
            self.set_content(content)

            # Начинаем отслеживание файла
            self._update_watching_state(True)
            self._start_watching_file()

            return True

        except Exception as e:
            self.error_occurred.emit(f"Ошибка загрузки файла: {e}", "error")
            return False