# Редактор для .md файлов
from PySide6.QtCore import Signal, QTimer
from PySide6.QtWidgets import QWidget, QVBoxLayout
from typing import Optional
from editor.base_editor import BaseFileEditor
from observers.file_watcher import FileWatcher
from parsers.md_file_parser import MarkdownListener
from widgets.markdown_converter import MarkdownConverter
from widgets.markdown_viewer_widget import MarkdownViewer
from pathlib import Path

class MarkdownEditor(BaseFileEditor):
    """
       Редактор для Markdown-файлов с поддержкой отслеживания внешних изменений.
       Наследует функциональность BaseFileEditor и добавляет специфичную для Markdown.
    """

    # Новые сигналы для работы с FileWatcher
    external_update_detected = Signal(str)          # Обнаружено внешнее изменение
    file_conflict_detected = Signal(str, str)       # Конфликт изменений (наш, внешний)
    file_became_readonly = Signal(str)              # Файл стал доступен только для чтения
    watching_status_changed = Signal(bool)          # Изменение статуса отслеживания
    def __init__(self, parent: Optional[QWidget] = None, file_watcher: Optional[FileWatcher] = None):
        """
            Инициализация редактора Markdown.

            Args:
                parent: Родительский виджет
                file_watcher: Опциональный FileWatcher для отслеживания изменений файлов
        """
        super().__init__(parent=parent)
        # Сохраняем переданный FileWatcher или создаем новый
        self._file_watcher = file_watcher or FileWatcher()

        # Создаем viewer для отображения Markdown (композиция!)
        self._viewer = MarkdownViewer(parent=self)

        # Флаг для временного отключения отслеживания
        self._watching_paused = False
        self._watching_enabled = False  # Добавляем флаг включенного отслеживания

        # Таймер для дебаунсинга множественных изменений
        self._debounce_timer = QTimer()
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.setInterval(300)  # 300ms задержка

        # Путь к файлу, который временно изменяется
        self._pending_external_update: Optional[str] = None

        # Инициализируем UI и соединения
        self._init_ui()
        self._setup_connections()

        # Устанавливаем начальное состояние
        self._update_watching_state(False)  # По умолчанию отслеживание выключено

        self.converter = MarkdownConverter()

    def _init_ui(self) -> None:
        """Инициализация пользовательского интерфейса"""
        # Основной layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Добавляем viewer в layout
        layout.addWidget(self._viewer.get_editor_widget())

        # Устанавливаем layout
        self.setLayout(layout)

    def _setup_connections(self) -> None:
        """Настройка сигналов и соединений"""
        # Подключаем таймер дебаунсинга
        self._debounce_timer.timeout.connect(self._handle_debounced_update)

        # Подключаем сигналы FileWatcher
        self._file_watcher.file_updated.connect(self._on_external_file_update)
        self._file_watcher.file_deleted.connect(self._on_external_file_deleted)
        self._file_watcher.dir_changed.connect(self._on_directory_changed)

        # Подключаем сигналы viewer к нашим обработчикам
        self._viewer.text_changed.connect(self._on_viewer_text_changed)

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
        Позволяет заменить или установить watcher после создания редактора.

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
            self._file_watcher.file_updated.connect(self._on_external_file_update)
            self._file_watcher.file_deleted.connect(self._on_external_file_deleted)
            self._file_watcher.dir_changed.connect(self._on_directory_changed)

    def _disconnect_file_watcher(self) -> None:
        """Отключает сигналы FileWatcher"""
        if self._file_watcher:
            try:
                self._file_watcher.file_updated.disconnect(self._on_external_file_update)
                self._file_watcher.file_deleted.disconnect(self._on_external_file_deleted)
                self._file_watcher.dir_changed.disconnect(self._on_directory_changed)
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

    def _pause_watching(self, duration: int = 2000) -> None:
        """
        Временно приостанавливает отслеживание на указанное время.
        Полезно при сохранении файла чтобы избежать циклических обновлений.

        Args:
            duration: Длительность паузы в миллисекундах
        """
        self._watching_paused = True
        self._update_watching_state(False)

        # Таймер для автоматического возобновления
        QTimer.singleShot(duration, self._resume_watching)

    def _resume_watching(self) -> None:
        """Возобновляет отслеживание после паузы"""
        self._watching_paused = False
        self._update_watching_state(True)
        if self.file_path:
            self._start_watching_file()

    def _handle_debounced_update(self) -> None:
        """
        Обрабатывает обновление после дебаунсинга.
        Вызывается по таймауту таймера дебаунсинга.
        """
        if self._pending_external_update:
            self._process_external_update(self._pending_external_update)
            self._pending_external_update = None

    def _process_external_update(self, file_path: str) -> None:
        """Обрабатывает внешнее изменение файла после дебаунсинга"""
        if Path(file_path) != self.file_path:
            return  # Не наш файл

        try:
            # 1. Создаем парсер и парсим файл
            md_parser = MarkdownListener()
            parsed_data = md_parser.parse_markdown_file(file_path)

            # 2. Извлекаем содержимое из результата парсинга
            external_content = parsed_data['structure'][0]['content']  # Берем content из структуры

            # 3. Сравниваем с текущими данными редактора
            current_content = self.get_content()

            if current_content == external_content:
                return  # Содержимое одинаковое - ложное срабатывание

            elif not self.is_modified:
                # Мы не редактировали - автоматически обновляем
                self.set_content(external_content)
                # Используем сигнал вместо прямого обращения к UI
                self.external_update_detected.emit("Файл обновлен внешней программой")

            else:
                # КОНФЛИКТ: мы редактируем и файл изменен извне
                self.file_conflict_detected.emit(current_content, external_content)

        except Exception as e:
            self.error_occurred.emit(f"Ошибка обработки внешнего изменения: {e}", "warning")


    def _on_external_file_update(self, file_path: str) -> None:
        """
        Обработчик сигнала обновления файла из FileWatcher.
        Использует дебаунсинг для избежания множественных срабатываний.

        Args:
            file_path: Путь к измененному файлу
        """
        if self._watching_paused:
            return  # Игнорируем если отслеживание приостановлено

        # Дебаунсим: откладываем обработку и перезапускаем таймер
        self._pending_external_update = file_path
        self._debounce_timer.start()

    def _on_external_file_deleted(self, file_path: str) -> None:
        """
        Обработчик сигнала удаления файла из FileWatcher.

        Args:
            file_path: Путь к удаленному файлу
        """
        if Path(file_path) == self.file_path:
            self.file_became_readonly.emit(file_path)
            self._viewer.set_readonly(True)                                             #TODO 10.09.2025 тут будет ошибка
            self.statusBar().showMessage("Файл удален внешней программой", 3000)        #TODO 10.09.2025 тут будет ошибка

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
        Обработчик изменения текста в viewer'е.
        Устанавливает флаг модификации и обновляет состояние.
        """
        self.is_modified = True

