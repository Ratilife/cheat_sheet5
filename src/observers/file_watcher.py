import os
from PySide6.QtCore import QFileSystemWatcher, Signal, QObject

class FileWatcher(QObject):
    # TODO 🚧 В разработке: 08.08.2025
        # 🏆task: Создание боковой панели;
        # 🏆task: Открыть боковую панель из стартовой панели;
        # 🏆task: Работа с деревом:
        # 🏆task: Создание слушателя за файлами, за их изменениями со стороны ОС
    """Отслеживает изменения файлов и уведомляет подписчиков."""
    file_updated = Signal(str)  # Файл изменён (путь)
    file_deleted = Signal(str)  # Файл удалён (путь)
    dir_changed = Signal(str)  # Изменение в папке (новые файлы/подпапки)

    def __init__(self):
        # ✅ Реализовано: 10.08.2025
        super().__init__()   # Вызываем конструктор базового класса QObject, чтобы корректно инициализировать объект с поддержкой сигналов/слотов Qt
        # Создаём экземпляр QFileSystemWatcher, который будет следить за изменениями файлов и директорий в файловой системе
        self.watcher = QFileSystemWatcher
        self.watched_dirs = set()  # Все отслеживаемые папки
        # Подключаем собственный метод _handle_file_change к сигналу fileChanged:
        # это значит, что когда отслеживаемый файл изменится, будет автоматически вызван _handle_file_change с путём к файлу
        self.watcher.fileChanged.connect(self._handle_file_change)
        self.watcher.directoryChanged.connect(self._handle_dir_change)  # Добавили обработчик папок

    def _handle_file_change(self, path: str) -> None:
        """Обрабатывает изменение файла."""
        # ✅ Реализовано: 10.08.2025
        # Проверяет, существует ли указанный путь (файл или директория) в файловой системе
        if os.path.exists(path):
            # Если путь существует, генерирует (вызывает) сигнал/событие о том, что файл был обновлён
            self.file_updated.emit(path)
        else:
            # Если путь не существует (файл был удалён), генерирует (вызывает) сигнал/событие о том, что файл был удалён
            self.file_deleted.emit(path)

    def _add_path(self, path: str) -> bool:
        """Добавляет путь в наблюдатель."""
        # ✅ Реализовано: 10.08.2025
        # Проверяет, существует ли указанный путь в файловой системе
        if os.path.exists(path) and path not in self.watcher.files():
            # Если путь существует и ещё не отслеживается, добавляет его в наблюдатель и возвращает результат
            return self.watcher.addPath(path)
        # Если путь не существует или уже отслеживается, возвращает False
        return False

    def _handle_dir_change(self, dir_path) -> None:
        """Обрабатывает изменение в папке (новые/удалённые подпапки или файлы)."""
        # ✅ Реализовано: 10.08.2025
        self.dir_changed.emit(dir_path)
        self._rescan_directory(dir_path)  # Пересканируем папку

    def _rescan_directory(self, dir_path: str) -> None:
        """Проверяет актуальность списка подпапок и обновляет наблюдатель."""
        # ✅ Реализовано: 10.08.2025
        current_subdirs = set()
        # Собираем текущие подпапки
        for root, dirs, _ in os.walk(dir_path):
            for dir_name in dirs:
                current_subdirs.add(os.path.join(root, dir_name))

        # Удаляем несуществующие подпапки из наблюдателя
        for watched_dir in list(self.watched_dirs):
            if watched_dir.startswith(dir_path) and watched_dir not in current_subdirs:
                self.watcher.removePath(watched_dir)
                self.watched_dirs.remove(watched_dir)

        # Добавляем новые подпапки
        for subdir in current_subdirs:
            if subdir not in self.watched_dirs:
                self.watcher.addPath(subdir)
                self.watched_dirs.add(subdir)

    def _watch_subdirectories(self, dir_path: str) -> None:
        """Рекурсивно добавляет подпапки в наблюдатель."""
        # ✅ Реализовано: 10.08.2025
        for root, dirs, _ in os.walk(dir_path):
            for dir_name in dirs:
                full_path = os.path.join(root, dir_name)
                if full_path not in self.watched_dirs:
                    self.watcher.addPath(full_path)
                    self.watched_dirs.add(full_path)
    def watch_file(self, path: str) -> bool:
        """Добавляет файл для отслеживания"""
        # ✅ Реализовано: 10.08.2025
        return self._add_path(path)  # Используем уже существующий метод

    def watch_directory(self, dir_path: str)->bool:
        """Добавляет папку и все её подпапки в наблюдение."""
        #  ✅ Реализовано: 10.08.2025
        if not os.path.isdir(dir_path):
            return False

        if dir_path not in self.watched_dirs:
            self.watcher.addPath(dir_path)
            self.watched_dirs.add(dir_path)
            self._watch_subdirectories(dir_path)  # Рекурсивно добавляем подпапки
            return True
        return False
    def remove_path(self, path: str) -> None:
        """Удаляет путь из наблюдателя."""
        # TODO 🚧 В разработке: 10.08.2025 - использовать при удалении файла из дерева файлов
        # Проверяет, находится ли указанный путь среди отслеживаемых наблюдателем файлов/путей
        if path in self.watcher.files():
            # Если путь отслеживается, удаляет его из наблюдателя с помощью removePath
            self.watcher.removePath(path)

    def get_watched_files(self) -> list:
        """Возвращает список отслеживаемых файлов"""
        # TODO 🚧 В разработке: 10.08.2025 - использовать при валдации добавления/удаления, не добавлен ли файл уже в наблюдатель
        return self.watcher.files()

    def clear_watched_files(self) -> None:
        """Очищает список отслеживаемых файлов"""
        #  ⌛ Реализовано: 10.08.2025 - мертвый код оставить для будущих задач
        if self.watcher.files():
            self.watcher.removePaths(self.watcher.files())