import sys
import os
from PySide6.QtWidgets import QApplication
from src.start_panel.views.view import MainWindow
from src.start_panel.view_models.view_model import ButtonViewModel
from src.start_panel.models.model import ButtonListModel
from src.ui.start_panel_buttons import StartPanelButtons
from src.ui.customization_start_panel import CostStartPanel
from src.global_var.config import get_root_folder
def start():
    app = QApplication([])

    #task: Сохранить buttons.json в папке for_program корневого католога:
    root_folder_path = get_root_folder()
    # Создаем Model
    model = ButtonListModel(os.path.join(root_folder_path['path'], "for_program"))

    # Создаем ViewModel и передаем ей Model
    view_model = ButtonViewModel(model)

    # Создаем View и передаем ему ViewModel
    window = MainWindow(view_model)
    window.show()

    sys.exit(app.exec())

def run_start_panel_buttons():
    app = QApplication(sys.argv)
    window = StartPanelButtons()
    window.show()
    sys.exit(app.exec())

def run_cost_start_panel():
    app = QApplication(sys.argv)
    window = CostStartPanel()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    start()
    #run_start_panel_buttons()
    #run_cost_start_panel()


