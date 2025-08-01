from typing import Dict, List, Set
from PySide6.QtCore import QObject, Signal
from src.start_panel.models.model import ButtonModel

class DeleteButtonsViewModel(QObject):
    def __init__(self, model):
        super().__init__()
        self._model = model  # Ссылка на ButtonListModel (model)
        #self._delete_model = DeleteButtonsModel(model)  # Создаем DeleteButtonsModel (model_delete_buttons)
        self._selected_buttons: Set[str] = set()  # Храним имена выбранных кнопок
    # Сигнал для уведомления View об изменении данных
    buttonsUpdated = Signal()

    def get_buttons(self) -> List[ButtonModel]:
        """
        Возвращает список кнопок.
        """
        return self._model.get_buttons()

    def toggle_selection(self, name: str):
        """Переключает состояние выбора кнопки"""
        if name in self._selected_buttons:
            self._selected_buttons.remove(name)
        else:
            self._selected_buttons.add(name)
        self.selection_changed.emit()  # Уведомляем View об изменении

    def get_selected_buttons(self) -> List[str]:
        """Возвращает имена выбранных кнопок"""
        return list(self._selected_buttons)

    def get_all_buttons(self) -> List[str]:
        """Возвращает все имена кнопок (для отображения в UI)"""
        return [button.name for button in self._model.get_buttons()]



    def get_selected_indices(self) -> List[int]:
        # Возвращает индексы выбранных кнопок, а не их имена
        selected_indices = []
        for i in range(self.table.rowCount()):
            checkbox = self.table.cellWidget(i, 1)
            if checkbox.isChecked():
                selected_indices.append(i)
        return selected_indices



