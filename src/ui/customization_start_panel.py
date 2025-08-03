from PySide6.QtWidgets import QMainWindow, QMessageBox
from src.ui.customization_start_panel_window import CostStartPanelWindow
from src.operation.file_operations import FileOperations

class CostStartPanel(QMainWindow):

    def __init__(self):
        # TODO 🚧 В разработке: 01.08.2025
        super(CostStartPanel,self).__init__()
        self.ui = CostStartPanelWindow()
        self.ui.setupUi(self)
        self.file_operation = FileOperations()

        self.ui.but_dialog_create_folder.clicked.connect(self._on_dialog_create_folder)
        self.ui.but_close_window.clicked.connect(self.close) # Закрытие окна
        self.ui.but_close_save_minutes.clicked.connect(self._on_save_and_close)

    def _on_dialog_create_folder(self):
        # ✅ Реализовано: 03.08.2025
            # task: Создание корневой папки
        path_root_folder = self.file_operation.create_root_folder()
        if path_root_folder:  # Проверяем, что путь был получен
            self.ui.path_root_folder.setText(path_root_folder)  # Устанавливаем текст в QLineEdit

    def _on_save_and_close(self):
        # # TODO 🚧 В разработке: 03.08.2025 - нужно проверить работу и протестировать
            #task: Работа с окном Настройка для стартовой панели

        root_path = self._get_root_path()
        if not root_path:
            return
        self.file_operation.save_path_root_folder(root_path,"for_program")


    def _get_root_path(self) -> str:
        """Получает и проверяет путь из QLineEdit."""
        # TODO 🚧 В разработке: 03.08.2025 - нужно проверить работу и протестировать
            # task: Работа с окном Настройка для стартовой панели
        root_path = self.ui.path_root_folder.text().strip()
        if not root_path:
            QMessageBox.warning(self, "Ошибка", "Корневая папка не указана!")
            return ""
        return root_path

