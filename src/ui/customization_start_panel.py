import sys
from PySide6.QtWidgets import QApplication,QMainWindow
from src.ui.customization_start_panel_window import CostStartPanelWindow
from src.operation.file_operations import FileOperations

class CostStartPanel(QMainWindow):
    def __init__(self):
        super(CostStartPanel,self).__init__()
        self.ui = CostStartPanelWindow()
        self.ui.setupUi(self)
        self.file_operation = FileOperations()

        self.ui.but_dialog_create_folder.clicked.connect(self.on_dialog_create_folder)

    def on_dialog_create_folder(self):
        self.file_operation.create_root_folder()