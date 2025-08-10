from PySide6.QtCore import QObject, Signal
class MyBaseObserver(QObject):
    """Базовый класс наблюдателя с общим функционалом"""
    # ✅ Реализовано: 10.08.2025
        #Создание базового наблюдателя
    # Сигнал при выборе файла (передает путь к файлу)
    file_selected = Signal(str, object)
    # Сигнал при изминении файла(передает путь к измененному файлу)
    file_changed = Signal(str)
    file_deleted = Signal(str)  # Путь к удаленному файлу
    # Сигналы для обновления дерева файлов в родительском окне
    file_created = Signal(str)  # Путь к созданному файлу
    file_saved = Signal(str)  # Путь к сохраненному файлу

    def __init__(self):
        # ✅ Реализовано: 10.08.2025
        super().__init__()
        self._watched_files = set()

    def watch_file(self, path):
        """Добавить файл в отслеживаемые"""
        # ✅ Реализовано: 10.08.2025
        if path not in self._watched_files:
            self._watched_files.add(path)

    def unwatch_file(self, path):
        """Прекратить отслеживание файла"""
        # ✅ Реализовано: 10.08.2025 - мертвый код оставить для дальнейших задач
        self._watched_files.discard(path)

    def is_watched(self, path):
        """Проверка, отслеживается ли файл"""
        # ✅ Реализовано: 10.08.2025
        return path in self._watched_files