import sys
from PySide6.QtWidgets import QApplication,QMainWindow
from src.ui.customization_start_panel_window import CostStartPanelWindow


class CostStartPanel(QMainWindow):
    def __init__(self):
        super(CostStartPanel,self).__init__()
        self.ui = CostStartPanelWindow()
        self.ui.setupUi(self)

