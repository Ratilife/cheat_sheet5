#Файл контейнер связывает окно и систему
import sys
from PySide6.QtWidgets import QApplication,QMainWindow
from src.ui.start_panel_buttons_window import StartPanelButtonsWindow

class StartPanelButtons(QMainWindow):
    def __init__(self):
        super(StartPanelButtons,self).__init__()
        self.ui = StartPanelButtonsWindow()
        self.ui.setupUi(self)

if __name__ == "__name__":
    app = QApplication(sys.argv)

    window = StartPanelButtons()
    window.show()
    sys.exit(app.exec())
