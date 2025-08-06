from src.start_panel.models.model import ButtonListModel

def test_is_button_name_unique():
    print("\n=== Запуск теста test_is_button_name_unique ===")
    model = ButtonListModel()
    model.add_button("Кнопка 1", "/path/1")

    # Проверяем уникальность имени
    test_cases = [
        ("Кнопка 2", True,  "Свободное имя должно возвращать True"),
        ("Кнопка 1", False, "Занятое имя должно возвращать False")
    ]

    for name, expected, description in test_cases:
        result = model.is_button_name_unique(name)
        if result == expected:
            print(f"✅ Тест пройден: {description}")
        else:
            print(f"❌ Тест не пройден: {description} (ожидалось {expected}, получено {result})")
            raise AssertionError(f"Тест не пройден: {description}")

if __name__ == "__main__":
    test_is_button_name_unique()