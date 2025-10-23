# Разработка кроссплатформенного средства оптимизации ключевой учебной информации для подготовки IT-специалистов на основе фоновой обработки структурированных данных

## **Краткое описание**
### *Что делает проект?*
### Стартовая панель
#### Обзор
*Стартовая панель* - это центральный элемент управления приложением, предоставляющий быстрый доступ к часто используемым файлам и приложениям. Панель сочетает в себе предустановленные системные кнопки и пользовательские кнопки для максимальной гибкости и удобства.

#### ⚡ Основные возможности
#####  Быстрый запуск
Пользователь может создавать собственные кнопки для мгновенного доступа к:
- **Приложениям** (Notepad++, VSCode, Android Studio, Telegram и др.)
- **Файлам** любых форматов
- **Папкам** и директориям
- **Внешним программам** и утилитам

![Стартовая панель.png](docs/pictures/Стартовая панель.png)

### **Структура проекта**
```txt
cheat_sheet/ (или cheat_chest)
├── .venv/                    # Виртуальное окружение Python
├── docs/                     # Документация
├── ex/                       # Примеры
├── old/                      # Устаревшие файлы
├── src/ (01.08.2025 15:56)   # Исходный код
│   ├── ANTLR4/               # Система парсинга ANTLR4
│   │   ├── 1c_grammar/       # Грамматика 1С
│   │   ├── ch_grammar/       # Грамматика C#
│   │   ├── java_grammar/     # Грамматика Java
│   │   ├── py_grammar/       # Грамматика Python
│   │   ├── st_grammar/       # Грамматика Structured Text
│   │   ├── __init__.py
│   │   ├── STFile.g4
│   │   ├── STFile.interp
│   │   ├── STFile.tokens
│   │   ├── STFileLexer.interp
│   │   ├── STFileLexer.py
│   │   ├── STFileLexer.tokens
│   │   ├── STFileListener.py
│   │   └── STFileParser.py
│   ├── controllers/          # Контроллеры
│   │   ├── __init__.py
│   │   └── selection_controller.py
│   ├── dialogs/              # Диалоговые окна
│   │   ├── __init__.py
│   │   └── dialog_manager.py
│   ├── editor/               # Система редакторов
│   │   ├── __init__.py
│   │   ├── base_editor.py
│   │   ├── editor_factory.py
│   │   ├── editor_manager.py
│   │   ├── markdown_editor.py
│   │   ├── plain_text_editor.py
│   │   └── st_editor.py
│   ├── global_var/           # Глобальные переменные
│   │   ├── __init__.py
│   │   └── config.py
│   ├── managers/             # Менеджеры приложения
│   │   ├── __init__.py
│   │   ├── dynamic_tabs.py
│   │   ├── file_manager.py
│   │   ├── root_folder_structure_basic.json
│   │   ├── toolbar_manager.py
│   │   ├── tree_model_manager.py
│   │   └── ui_manager.py
│   ├── models/               # Модели данных
│   │   ├── __init__.py
│   │   ├── st_md_file_tree_item.py
│   │   └── st_md_file_tree_model.py
│   ├── observers/            # Наблюдатели
│   │   ├── __init__.py
│   │   ├── file_watcher.py
│   │   └── my_base_observer.py
│   ├── operation/            # Операции
│   │   ├── __init__.py
│   │   └── file_operations.py
│   ├── parsers/              # Парсеры
│   │   ├── __init__.py
│   │   ├── background_parser.py
│   │   ├── content_cache.py
│   │   ├── file_parser_service.py
│   │   ├── md_file_parser.py
│   │   ├── metadata_cache.py
│   │   └── st_file_parser.py
│   ├── start_panel/          # Стартовая панель (MVVM)
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── model.py
│   │   ├── view_models/
│   │   │   ├── __init__.py
│   │   │   ├── view_model.py
│   │   │   └── view_model_delete_buttons.py
│   │   ├── views/
│   │   │   ├── __init__.py
│   │   │   ├── view.py
│   │   │   └── view_delete_buttons.py
│   │   └── __init__.py
│   ├── ui/                   # Пользовательский интерфейс
│   │   └── files_qt_designer/
│   │       ├── __init__.py
│   │       ├── customization_start_panel.py
│   │       ├── customization_start_panel_window.py
│   │       ├── file_editor.py
│   │       ├── side_panel.py
│   │       ├── start_panel_buttons.py
│   │       └── start_panel_buttons_window.py
│   ├── utils/                # Утилиты
│   │   ├── md/               # Markdown утилиты
│   │   │   ├── __init__.py
│   │   │   ├── markdown_converter.py
│   │   │   ├── markdown_highlighter.py
│   │   │   ├── markdown_styles.py
│   │   │   └── markdown_viewer_widget.py
│   │   ├── st/               # Structured Text утилиты
│   │   │   ├── __init__.py
│   │   │   └── st_highlighter.py
│   │   ├── __init__.py
│   │   └── clipboard_manager.py
│   └── widgets/              # Виджеты
├── tests/                    # Тесты
├── buttons — konwa.json      # Конфигурация кнопок
├── main.py                   # Главный файл приложения
├── method_tracer.py          # Трассировщик методов
├── pytest.ini               # Конфигурация pytest
├── README.MD                # Документация
└── requirements.txt         # Зависимости проекта
```

#### **Основные характеристики проекта:**
    🐍 Python приложение с виртуальным окружением
    🏗️ Модульная архитектура с четким разделением ответственности
    📝 Редактор сниппетов с поддержкой Markdown и Structured Text
    🔍 ANTLR4 для синтаксического анализа различных языков
    🎯 MVVM паттерн в стартовой панели
    ⚡ Кэширование и фоновый парсинг для производительности
    👀 Система наблюдателей для отслеживания изменений
    🎨 Гибкая система UI с Qt


