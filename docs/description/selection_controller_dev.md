# модуль selection_controller.py

в модуле реализован класс TreeSelectionController унаследован от класса QObject библиотеки PySide6.QtCore
Класс TreeSelectionController это контроллер для обработки выделения элементов в дереве.
Получает контект из кэш или модели.

Основные Сигналы:
    
content_for_sidepanel = Signal(str, str, str)   *запрашиваемый данные  в окне с которым работает пользователь*
        - издает сигнал в методе **_process_content()** при работе с деревом в классе **SidePanel**
        - принимает сигнал метод on_display_content в классе  **SidePanel**
        - подключен сигнал в методе _connect_selection_signals() вклассе  **SidePanel** и запускается при инициализации
            экземпляра класса
        параметры:
                **content_type**   тип элемента: 'template', 'folder', 'file', 'markdown'
                **content**        Содержимое файла, привязано к типу контента, выводитсяв редактор 
                **path_file**      путь к файлу. Это ключ к кэш 
    
content_for_editor = Signal(str, str, str) *запрашиваемый данные  в окне с которым работает пользователь*
        - издает сигнал в методе **_process_content()** при работе с деревом в классе **FileEditorWindow**
        - принимает сигнал метод on_display_content() в классе  **FileEditorWindow** 
        - подключен сигнал в методе _connect_selection_signals() вклассе  **FileEditorWindow** и запускается при инициализации
            экземпляра класса        
        параметры:
                **content_type**   тип элемента: 'template', 'folder', 'file', 'markdown'
                **content**        Содержимое файла, привязано к типу контента, выводитсяв редактор 
                **path_file**      путь к файлу. Это ключ к кэш 

selection_changed = Signal(dict)   выбранный параметр изменен (Сигнал о изменении выделения)
        - издает сигнал в методе _handle_selection()  в классе **TreeSelectionController**
        - принимает сигнал метод selection_changed() в классе **FileEditorWindow**
        -подключен сигнал к методу _connect_selection_signals() класс **FileEditorWindow**
        - принимает сигнал  метод on_update_selection_status() класса **SidePanel**
        - подключен сигнал к методу _connect_selection_signals класса **SidePanel**
        параметры:
             metadata: {type, name, path, has_content}
    error_occurred = Signal(str)  # error_message       произошла ошибка
    content_for_element = Signal(str, str, str, dict)  # type, element_content, path, element_info 