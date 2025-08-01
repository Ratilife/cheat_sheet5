import sys
from PySide6.QtWidgets import QApplication
from src.start_panel.views.view import MainWindow
from src.start_panel.view_models.view_model import ButtonViewModel
from src.start_panel.models.model import ButtonListModel


def start():
    app = QApplication([])

    # Создаем Model
    model = ButtonListModel()

    # Создаем ViewModel и передаем ей Model
    view_model = ButtonViewModel(model)

    # Создаем View и передаем ему ViewModel
    window = MainWindow(view_model)
    window.show()

    sys.exit(app.exec())

if __name__ == '__main__':
    start()
    '''
    analyzer = DeadCodeAnalyzer()
    analyzer.analyze_project(r"F:\Языки\Python\Partfolio\cheat_sheet4\cheat_sheet\srs\start_panel")  # Укажите реальный путь
    report = analyzer.get_unused_code_report()
    analyzer.save_report_to_file(report, "dead_code_report_Отладка.txt")
    '''


