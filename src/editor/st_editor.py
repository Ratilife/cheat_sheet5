# Редактор для .st файлов
from datetime import time
from pathlib import Path
from typing import Optional
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit

from observers.file_watcher import FileWatcher
from operation.delta_operations import DeltaOperation
from src.editor.base_editor import BaseFileEditor
from PySide6.QtCore import Signal, QTimer
from utils.delta_processor import DeltaProcessor
from src.widgets.st.st_highlighter import STHighlighter


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

        self._state_save_timer = QTimer()          # Создание таймера для отложенного сохранения состояния
        self._state_save_timer.setSingleShot(True) # Установка таймера как одноразового (он сработает только один раз после запуска)
        self._state_save_timer.timeout.connect(self.save_state) # Подключение сигнала timeout таймера к методу save_state

        self.template_context = {
                 'file_path': None,          # Путь к элементу модели дерева (файл), он же ключ к структуре элемента в кэш
                 'template_id': None,        # определение шаблона, куда вносим данные.
                 'original_structure': None, # данные из кэш, полная структуда,
                 'original_content': None,   # контекст из кэш
                 'element_path': [],         # что нужно вставить в структуру
                 'pending_deltas': [],  # ⬅️ ОЧЕРЕДЬ НЕСОХРАНЕННЫХ ИЗМЕНЕНИЙ
                 'last_saved_structure': None  # ⬅️ СТРУКТУРА НА МОМЕНТ ПОСЛЕДНЕГО СОХРАНЕНИЯ
             }


    def _init_ui(self) -> None:
        """Инициализация пользовательского интерфейса"""
        # Основной layout
        layout = QVBoxLayout(self)              # Создание вертикального слоя (layout) и привязка его к текущему виджету
        layout.setContentsMargins(0, 0, 0, 0)   # Установка внешних отступов слоя в 0 (сверху, слева, снизу, справа)
        layout.setSpacing(0)                    # Установка расстояния между элементами внутри слоя в 0

        # Создаем текстовый редактор
        self._text_edit = QTextEdit()           # Создание экземпляра QTextEdit для редактирования текста
        self._text_edit.setAcceptRichText(False)  # Режим plain text, отключение поддержки форматированного текста, редактор будет работать только с простым текстом


        # Создаем подсветку синтаксиса
        self._highlighter = STHighlighter(
            self._text_edit.document(),  # Передаем документ
            language=None  # Язык определится позже
        )

        # Добавляем редактор в layout
        layout.addWidget(self._text_edit)       # Добавление виджета текстового редактора в вертикальный слой

        # Устанавливаем layout
        self.setLayout(layout)                  # Установка созданного слоя как основного слоя для текущего виджета


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
        """Заменяет текущий объект FileWatcher на новый и настраивает его.

         Этот метод отключает все соединения сигналов от старого FileWatcher (если он был),
         устанавливает новый экземпляр FileWatcher, подключает его сигналы к соответствующим
         обработчикам внутри текущего объекта, и, если файл уже открыт и отслеживание включено,
         начинает отслеживание текущего файла с помощью нового FileWatcher.

         Args:
         file_watcher: Новый экземпляр класса FileWatcher, который будет использоваться
                       для отслеживания изменений файлов.
        """

        # TODO - мертвый код нужно определить место
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
        """Начинает отслеживание изменений текущего файла и его директории.

        Проверяет, что объект FileWatcher инициализирован, путь к файлу задан
        и отслеживание включено. Если все условия выполнены, добавляет файл
        и его родительскую директорию в список отслеживаемых файлов/директорий
        через объект _file_watcher. Используется для автоматического обнаружения
        изменений файла извне.
        """
        # Проверка, что объект FileWatcher существует, путь к файлу задан и отслеживание включено
        if self._file_watcher and self.file_path and self._watching_enabled:
            # Преобразование объекта пути к строке для передачи в FileWatcher
            file_path_str = str(self.file_path)
            # Отслеживаем сам файл и его директорию
            self._file_watcher.watch_file(file_path_str)
            # Добавление директории файла в список отслеживаемых (например, для отслеживания переименований)
            self._file_watcher.watch_directory(str(self.file_path.parent))
            print(f"DEBUG: Начато отслеживание файла {file_path_str}")

    def _stop_watching_file(self) -> None:
        """Прекращает отслеживание изменений текущего файла.

        Проверяет, что объект FileWatcher инициализирован и путь к файлу задан.
        Если условия выполнены, удаляет файл из списка отслеживаемых через
        объект _file_watcher. Используется для отключения автоматического
        обнаружения изменений файла извне.
        """
        # Проверка, что объект FileWatcher существует и путь к файлу задан
        if self._file_watcher and self.file_path:
            # Преобразование объекта пути к строке для передачи в FileWatcher
            file_path_str = str(self.file_path)
            # Удаление файла (и, возможно, директории) из списка отслеживаемых в FileWatcher
            self._file_watcher.remove_path(file_path_str)
            print(f"DEBUG: Прекращено отслеживание файла {file_path_str}")

    def _process_external_update(self, file_path: str) -> None:

        """Обрабатывает обнаруженное внешнее изменение файла после задержки (дебаунсинга).

            Метод проверяет, соответствует ли измененный файл текущему открытому файлу.
            Если да, он читает новое содержимое файла с диска, сравнивает его с текущим
            содержимым редактора и, в зависимости от результатов:
                - ничего не делает, если содержимое совпадает (ложное срабатывание);
                - автоматически обновляет содержимое редактора, если файл не был изменен
                  пользователем;
                - генерирует сигнал конфликта, если файл был изменен как пользователем,
                  так и извне.

            Args:
                file_path (str): Путь к файлу, который был изменен извне.
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
        self._state_save_timer.start(500)  # Сохраняем состояние через 500ms

    def _on_watching_paused(self, paused: bool) -> None:
        """
        Обработчик изменения статуса паузы отслеживания

        Args:
            paused: True если отслеживание приостановлено
        """
        # Можно использовать для обновления UI
        status = "приостановлено" if paused else "возобновлено"
        print(f"DEBUG: Отслеживание {status}")

    def _identify_language(self, content: str) -> None:
        """
        Определяет язык программирования по первой строке содержимого template.

        Ищет маркер @@ в первой строке и извлекает язык после него.
        Поддерживает различные варианты написания языков.
        По умолчанию распознается язык 1C, если маркер не найден.

        Поддерживаемые маркеры:
        - Java: "@@java"
        - Python: "@@python"
        - C#: "@@c#", "@@C#", "@@Csharp", "@@csharp"
        - 1C: "@@1С", "@@1с", "@@1One", "@@1one" (по умолчанию если маркер отсутствует)
        - Текст: "@@text", "@@Text", "@@TEXT"

        Формат маркера: @@[ИмяЯзыка] [пробел] [код...]

        Args:
            content: str - Содержимое template элемента для анализа

        Returns:
            None - устанавливает self.language в нормализованное значение языка
        """
        # TODO 🚧 В разработке: 06.10.2025

        language = '1c'  # ⭐ По умолчанию язык 1C

        if not content or not content.strip():
            # Если содержимое пустое - язык по умолчанию
            self.language = language
            print(f"DEBUG: Определен язык (по умолчанию): '{self.language}'")
            return

        # Получаем первую строку содержимого
        first_line = content.split('\n')[0].strip()

        # Ищем маркер @@ в первой строке
        if '@@' in first_line:
            # Разделяем строку на части до и после маркера
            parts = first_line.split('@@', 1)

            if len(parts) == 2:
                # Берем часть после маркера
                after_marker = parts[1].strip()

                if after_marker:
                    # Извлекаем маркер языка (до первого пробела или конца строки)
                    # Маркер может быть: "java", "python", "c#", "1С", "1one", "text" и т.д.
                    language_marker = after_marker.split()[0] if ' ' in after_marker else after_marker

                    # Нормализуем маркер к стандартному значению
                    language = self._normalize_language(language_marker)

                    print(f"DEBUG: Найден маркер '@@{language_marker}' → нормализован в '{language}'")
                else:
                    # Маркер @@ найден, но после него ничего нет - по умолчанию 1C
                    print(f"DEBUG: Маркер '@@' найден, но язык не указан → используется '{language}'")
            else:
                # Маркер @@ найден, но формат некорректный - по умолчанию 1C
                print(f"DEBUG: Некорректный формат маркера → используется '{language}'")
        else:
            # Маркер @@ не найден - по умолчанию 1C
            print(f"DEBUG: Маркер '@@' не найден → используется '{language}' (по умолчанию)")

        # Устанавливаем язык в self.language
        self.language = language
        print(f"DEBUG: Итоговый определенный язык: '{self.language}'")

    def _apply_pending_deltas(self):
        self.dp.apply_pending_deltas(self.template_context)



    # Реализация undo/redo аналогично MarkdownEditor
    def can_undo(self) -> bool:
        return len(self._undo_stack) > 0

    def can_redo(self) -> bool:
        return len(self._redo_stack) > 0

    def undo(self) -> bool:
        """Отменяет последнее действие редактирования текста.

        Извлекает предыдущее состояние текста из стека отмены (_undo_stack),
        сохраняет текущее состояние в стек повтора (_redo_stack), обновляет
        содержимое текстового поля (_text_edit) и внутреннее состояние (_current_state).
        Также обновляет доступность действий "отменить" и "повторить", излучая
        соответствующие сигналы (undo_available, redo_available).

        Returns:
            bool: True, если отмена выполнена успешно, иначе False.
            Возвращает False, если отмена невозможна (стек пуст) или произошла ошибка.
        """
        # Проверка, доступно ли действие "отменить"
        if not self.can_undo():
            return False   # Если действие "отменить" недоступно, метод возвращает False

        try:
            # Сохранение текущего состояния в стек повтора (для redo)
            self._redo_stack.append(self._current_state)
            # Извлечение предыдущего состояния из стека отмены
            previous_state = self._undo_stack.pop()
            # Установка текущего состояния равным извлечённому предыдущему
            self._current_state = previous_state
            # Отображение предыдущего состояния в текстовом поле
            self._text_edit.setPlainText(previous_state)

            self.undo_available.emit(self.can_undo()) # Сигнал об изменении доступности действия "отменить"
            self.redo_available.emit(self.can_redo()) # Сигнал об изменении доступности действия "повторить"
            return True  # Метод возвращает True, указывая на успешное выполнение

        except Exception as e:
            print(f"Ошибка отмены: {e}")
            return False

    def register_change(self, operation, element_path, **data):
        """Регистрирует любое изменение в очереди дельт"""
        self.dp = DeltaProcessor()
        delta = self.dp.register_change(operation, element_path, **data)
        self.template_context['pending_deltas'].append(delta)

        # Автоматически помечаем как измененный
        self.is_modified = True

    def redo(self) -> bool:
        """Повторяет последнее отменённое действие редактирования текста.

                Извлекает следующее состояние текста из стека повтора (_redo_stack),
                сохраняет текущее состояние в стек отмены (_undo_stack), обновляет
                содержимое текстового поля (_text_edit) и внутреннее состояние (_current_state).
                Также обновляет доступность действий "отменить" и "повторить", излучая
                соответствующие сигналы (undo_available, redo_available).

                Returns:
                    bool: True, если повтор выполнен успешно, иначе False.
                          Возвращает False, если повтор невозможен (стек пуст) или произошла ошибка.
        """
        # Проверка, доступно ли действие "повторить"
        if not self.can_redo():
            return False # Если действие "повторить" недоступно, метод возвращает False

        try:
            # Сохранение текущего состояния в стек отмены (для undo)
            self._undo_stack.append(self._current_state)
            # Извлечение следующего состояния из стека повтора
            next_state = self._redo_stack.pop()
            # Установка текущего состояния равным извлечённому следующему
            self._current_state = next_state
            # Отображение следующего состояния в текстовом поле
            self._text_edit.setPlainText(next_state)

            self.undo_available.emit(self.can_undo()) # Сигнал об изменении доступности действия "отменить"
            self.redo_available.emit(self.can_redo()) # Сигнал об изменении доступности действия "повторить"
            return True

        except Exception as e:
            print(f"Ошибка повтора: {e}")
            return False

    def save_old(self) -> bool:
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

    def save_old2(self) -> bool:
        """
        Сохраняет содержимое редактора в текущий файл.
        """
        if not self.file_path:   #Проверка, задан ли путь к файлу
            # Если путь не задан, вызывается метод сохранения с выбором имени файла (save as)
            return self.save_as()

        try:
            # Приостановка FileWatcher на 3 секунды, чтобы избежать ложного срабатывания при сохранении
            self._file_watcher.pause(3000)

            content = self.get_content() # Получение текущего содержимого редактора
            # TODO - 28.10.2025 - изменить, причина: портит весь файл после сохранения, подумать над логикой
            # Открытие файла для записи в кодировке UTF-8
            with open(self.file_path, 'w', encoding='utf-8') as f:
                # Запись содержимого в файл
                f.write(content)

            # Сброс флага модификации, так как файл теперь соответствует сохранённому
            self.is_modified = False

            # ⭐ ВЫЗЫВАЕМ ОЧИСТКУ СОСТОЯНИЯ ОТМЕНЫ
            self.after_save_cleanup()  #TODO 11.10.2025 тут проблема

            return True

        except Exception as e:
            self.error_occurred.emit(f"Ошибка сохранения файла: {e}", "error")
            return False

    def save(self):
        if not self.template_context:
            return

        print(f'self.template_context из метода save: {self.template_context}')
        # 1. Проверяем, изменился ли контент
        new_content = self.get_content()
        print(f'new_content: {new_content}')
        if new_content != self.template_context.get('original_content'):
            # 2. Регистрируем дельту изменения контента
            self.register_change(
                operation=DeltaOperation.UPDATE_CONTENT,
                element_path=self.template_context['element_path'],
                old_content=self.template_context.get('original_content'),
                new_content=new_content
                )

        # 3. Применяем ВСЕ накопленные дельты
        return self._apply_pending_deltas()

    def save_as(self, new_file_path: Path = None) -> bool:
        """
        Сохраняет содержимое редактора в новый файл.

        Args:
            new_file_path: Новый путь для сохранения

        Returns:
            bool: True если сохранение прошло успешно, False в противном случае
        """
        # TODO: В реальной реализации нужно запрашивать путь у пользователя Нужно переписать
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

            # TODO - 28.10.2025 - изменить, причина: портит весь файл после сохранения, подумать над логикой
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

    def set_content(self, content: str) -> None:
        """Устанавливает содержимое редактора из строки."""
        # Устанавливает переданное содержимое в текстовое поле редактора
        self._text_edit.setPlainText(content)

        # ⭐ ОБНОВЛЯЕМ СОСТОЯНИЕ ОТМЕНЫ
        self._undo_stack.clear()            # Очищает стек отмены, так как история теряется при установке нового содержимого
        self._redo_stack.clear()            # Очищает стек повтора по той же причине
        self._current_state = content       # Сохраняет новое содержимое как текущее состояние
        self.undo_available.emit(False)     # Излучает сигнал, что действие "отменить" больше недоступно
        self.redo_available.emit(False)     # Излучает сигнал, что действие "повторить" больше недоступно

        # Сбрасываем флаг модификации при установке нового содержимого
        self.is_modified = False
        # Определяем язык для подсветки по первой строке
        self._identify_language(content) # Вызывает внутренний метод для определения языка подсветки синтаксиса на основе переданного содержимого

        # Устанавливаем язык в подсветке
        if self._highlighter:
            self._highlighter.set_language(self.language)  # Например, '1c', 'python'
            self._highlighter.set_document_text(content)
            self._highlighter.rehighlight()

    def get_content(self) -> str:
        """
        Возвращает текущее содержимое редактора.

        Returns:
            str: Текстовое содержимое редактора
        """
        return self._text_edit.toPlainText()

    def set_content_old(self, content: str) -> None:
        """
        Устанавливает содержимое редактора из строки.

        Args:
            content: Содержимое для отображения
        """
        self._text_edit.setPlainText(content)
        # Сбрасываем флаг модификации при установке нового содержимого
        self.is_modified = False
        # Определяем язык для подсветки по первой строке
        self._identify_language(content)

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

    def _normalize_language(self, language_marker: str) -> str:
        """
        Нормализует маркер языка к стандартному значению.

        Args:
            language_marker: str - маркер языка после @@ (например: "java", "C#", "1С", "1one")

        Returns:
            str: Нормализованное значение языка:
                 - '1c' для языка 1C
                 - 'python' для Python
                 - 'csharp' для C#
                 - 'java' для Java
                 - 'text' для простого текста
                 - '1c' по умолчанию (если маркер не распознан)
        """
        if not language_marker:
            return '1c'  # По умолчанию


        # Приводим к нижнему регистру для сравнения
        marker_lower = language_marker.lower()

        # Словарь для нормализации различных вариантов написания
        language_map = {
            # Java
            'java': 'java',

            # Python
            'python': 'python',

            # C# - различные варианты написания
            'c#': 'csharp',
            'с#': 'csharp',  # Кириллическая С
            'csharp': 'csharp',
            'сsharp': 'csharp',  # Кириллическая С
            'c sharp': 'csharp',
            'с sharp': 'csharp',  # Кириллическая С

            # 1C - различные варианты написания
            '1c': '1c',
            '1с': '1c',  # Кириллическая С
            '1С': '1c',  # Кириллическая С (большая)
            '1one': '1c',
            '1One': '1c',
            '1ONE': '1c',
            '1c/bsl': '1c',
            'bsl': '1c',

            # Простой текст
            'text': 'text',
            'txt': 'text',
            'plain': 'text',
        }

        # Ищем точное совпадение
        if marker_lower in language_map:
            return language_map[marker_lower]

        # Проверяем варианты с пробелами и специальными символами
        marker_normalized = marker_lower.replace(' ', '').replace('_', '').replace('-', '')

        # Проверяем нормализованный маркер
        if marker_normalized in language_map:
            return language_map[marker_normalized]

        # Проверяем частичное совпадение (например, если маркер начинается с варианта)
        for key, value in language_map.items():
            if marker_normalized.startswith(key) or key.startswith(marker_normalized):
                return value

        # Если не нашли совпадение - по умолчанию 1C
        return '1c'