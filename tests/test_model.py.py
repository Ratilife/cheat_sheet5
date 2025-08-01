import pytest
from src.start_panel.models.model import ButtonListModel, ButtonModel

def test_add_button():
    # Arrange: Создаем модель и тестовые данные
    model = ButtonListModel()
    name = "Test Button"
    path = "/fake/path"

    # Act: Добавляем кнопку
    model.add_button(name, path)

    # Assert: Проверяем, что кнопка добавилась
    buttons = model.get_buttons()
    assert len(buttons) == 1
    assert buttons[0].name == name
    assert buttons[0].path == path

def test_remove_button():
    # Arrange
    model = ButtonListModel()
    model.add_button("Button 1", "/path/1")
    model.add_button("Button 2", "/path/2")

    # Act: Удаляем первую кнопку
    model.remove_button(0)

    # Assert
    buttons = model.get_buttons()
    assert len(buttons) == 1
    assert buttons[0].name == "Button 2"