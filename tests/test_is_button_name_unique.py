from src.start_panel.models.model import ButtonListModel
def test_is_button_name_unique():
    model = ButtonListModel()
    model.add_button("1C", r"C:\Program Files\\1cv8\common\\1cestart.exe")
    
    # Проверяем уникальность имени
    assert model.is_button_name_unique("Notepad++") == True  # Имя свободно
    assert model.is_button_name_unique("Кнопка 1") == False  # Имя занято