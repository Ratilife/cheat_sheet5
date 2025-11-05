# Редактор для .st файлов
from datetime import time
from pathlib import Path
from typing import Optional
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit

from observers.file_watcher import FileWatcher
from operation.delta_operations import DeltaOperation
from src.editor.base_editor import BaseFileEditor
from PySide6.QtCore import Signal, QTimer


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


    def _init_ui(self) -> None:
        """Инициализация пользовательского интерфейса"""
        # Основной layout
        layout = QVBoxLayout(self)              # Создание вертикального слоя (layout) и привязка его к текущему виджету
        layout.setContentsMargins(0, 0, 0, 0)   # Установка внешних отступов слоя в 0 (сверху, слева, снизу, справа)
        layout.setSpacing(0)                    # Установка расстояния между элементами внутри слоя в 0

        # Создаем текстовый редактор
        self._text_edit = QTextEdit()           # Создание экземпляра QTextEdit для редактирования текста
        self._text_edit.setAcceptRichText(False)  # Режим plain text, отключение поддержки форматированного текста, редактор будет работать только с простым текстом

        # TODO: Здесь позже добавим подсветку синтаксиса
        # self._highlighter = STHighlighter(self._text_edit.document())

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
         Определяет язык программирования по первой строке содержимого.
         Ищет маркер @@ и извлекает текст после него до первого пробела.

         Args:
             content: Содержимое файла для анализа

         Returns:
             str: Название языка в нижнем регистре или пустая строка если не найден
         """
        # TODO 🚧 В разработке: 06.10.2025

        language = ""

        # Получаем первую строку
        first_line = content.split('\n')[0].strip()

        # Ищем маркер @@
        if '@@' in first_line:
            # Берем часть строки после @@
            after_marker = first_line.split('@@', 1)[1].strip()

            if after_marker:
                # Берем первое слово после маркера (до первого пробела)
                language = after_marker.split()[0]

        # Приводим к нижнему регистру
        self.language = language.lower()

        print(f"DEBUG: Определен язык: '{self.language}'")

    def _apply_delta_to_structure(self, delta):
        # TODO 🚧 В разработке: 03.11.2025 мертвый код
        # 1. Получаем актуальную структуру из кэша
        current_structure = self.content_cache.get(self.template_context['file_path'])

        # 2. Находим целевой элемент по пути
        target_element = self._navigate_to_element(current_structure, delta['element_path'])

        if not target_element:
            return False

        # 3. Применяем изменение
        target_element['content'] = delta['new_content']

        # 4. Сериализуем ТОЛЬКО если структура изменилась
        if current_structure != self.template_context['original_structure']:
            st_content = self.parser_service.serialize_st_structure(current_structure)
            self.file_operations.write_file(self.template_context['file_path'], st_content)

        # 5. Обновляем кэш
        self.content_cache.set(self.template_context['file_path'], current_structure)

        return True

    def _apply_pending_deltas(self):
        """Применяет все ожидающие дельты к структуре"""
        # TODO 🚧 В разработке: 04.11.2025
        if not self.template_context['pending_deltas']:
            return True  # Нет изменений

        # 1. Получаем актуальную структуру
        current_structure = self.template_context['original_structure']

        # 2. Применяем каждую дельту
        for delta in self.template_context['pending_deltas']:
            success = self._apply_single_delta(current_structure, delta)
            if not success:
                return False  # Откатываем если ошибка

        # 3. Сериализуем и сохраняем
        st_content = self.parser_service.serialize_st_structure(current_structure)
        success = self.file_operations.write_file(
            self.template_context['file_path'],
            st_content
        )

        if success:
            # 4. Очищаем очередь и обновляем кэш
            self.template_context['pending_deltas'].clear()
            self.content_cache.set(self.template_context['file_path'], current_structure)
            self.template_context['last_saved_structure'] = current_structure.copy()

        return success
    def _apply_single_delta(self, structure, delta):
        """Применяет одну дельту к структуре"""

        # Находим целевой элемент
        target_element = self._navigate_to_element(structure, delta.element_path)
        if not target_element:
            print(f"❌ Не найден элемент по пути: {delta.element_path}")
            return False

        # Выбираем обработчик в зависимости от операции
        handlers = {
            DeltaOperation.UPDATE_CONTENT: self._handle_update_content,
            DeltaOperation.RENAME: self._handle_rename,
            DeltaOperation.MOVE: self._handle_move,
            DeltaOperation.DELETE: self._handle_delete,
            DeltaOperation.CREATE: self._handle_create
        }

        handler = handlers.get(delta.operation)
        if not handler:
            print(f"❌ Неизвестная операция: {delta.operation}")
            return False

        return handler(target_element, delta.data)

    def _handle_update_content(self, element, data):
        """ВАША ОПЕРАЦИЯ - изменение контента шаблона"""
        element['content'] = data['new_content']
        return True

    def _handle_rename(self, element, data):
        """Переименование элемента"""
        element['name'] = data['new_name']
        return True

    def _navigate_to_element(self, structure, element_path):
        """Переходит по пути ['root', 'folder1', 'template'] в структуре"""
        current = structure

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

