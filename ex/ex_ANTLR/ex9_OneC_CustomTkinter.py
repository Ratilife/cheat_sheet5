import customtkinter as ctk
import tkinter as tk
from antlr4 import *
from OneC.BSLLexer import BSLLexer

def apply_syntax_highlighting(text_widget, text):
    # Очистка форматирования
    text_widget.delete("1.0", tk.END)

    # Удаляем ВСЕ теги перед применением новых
    for tag_name in text_widget.tag_names():
        text_widget.tag_delete(tag_name)

    text_widget.insert(tk.END, text)

    # Проверка и подготовка текста для лексера
    # Убеждаемся, что текст - это строка (не bytes)
    if isinstance(text, bytes):
        # Если текст в байтах, декодируем в UTF-8
        text = text.decode('utf-8')
    
    # Убеждаемся, что текст в правильной кодировке (UTF-8)
    # Tkinter уже работает с Unicode, но на всякий случай проверяем
    if not isinstance(text, str):
        text = str(text)
    
    # Создаем InputStream для лексера
    # InputStream принимает строку и автоматически конвертирует в байты UTF-8
    input_stream = InputStream(text)
    
    # Создаем лексер ANTLR
    lexer = BSLLexer(input_stream)
    token = lexer.nextToken()
    
    # ОТЛАДКА: проверяем первые несколько символов текста
    if len(text) > 0:
        print(f"Первый символ текста: '{text[0]}' (код: {ord(text[0])})")
        print(f"Тип текста: {type(text)}")
        print(f"Длина текста: {len(text)}")

    # Цвета для подсветки
    colors = {
        'DOT': 'red',
        'LBRACK': 'red',
        'RBRACK': 'red',
        'LPAREN': 'red',
        'RPAREN': 'red',
        'COLON': 'red',
        'SEMICOLON': 'red',
        'COMMA': 'red',
        'ASSIGN': 'red',
        'PLUS': 'red',
        'MINUS': 'red',
        'LESS_OR_EQUAL': 'red',
        'NOT_EQUAL': 'red',
        'LESS': 'red',
        'GREATER_OR_EQUAL': 'red',
        'GREATER': 'red',
        'MUL': 'red',
        'QUOTIENT': 'red',
        'MODULO': 'red',
        'QUESTION': 'red',
        'AMPERSAND': 'brown',
        'PREPROC_DELETE': 'red',
        'PREPROC_INSERT': 'red',
        'PREPROC_ENDINSERT': 'red',
        'TRUE': 'red',
        'FALSE': 'red',
        'UNDEFINED': 'red',
        'NULL': 'red',
        'PROCEDURE_KEYWORD': 'red',
        'FUNCTION_KEYWORD': 'red',
        'ENDPROCEDURE_KEYWORD': 'red',
        'ENDFUNCTION_KEYWORD': 'red',
        'EXPORT_KEYWORD': 'red',
        'VAL_KEYWORD': 'red',
        'ENDIF_KEYWORD': 'red',
        'ENDDO_KEYWORD': 'red',
        'IF_KEYWORD': 'red',
        'ELSIF_KEYWORD': 'red',
        'ELSE_KEYWORD': 'red',
        'THEN_KEYWORD': 'red',
        'WHILE_KEYWORD': 'red',
        'DO_KEYWORD': 'red',
        'FOR_KEYWORD': 'red',
        'TO_KEYWORD': 'red',
        'EACH_KEYWORD': 'red',
        'IN_KEYWORD': 'red',
        'TRY_KEYWORD': 'red',
        'EXCEPT_KEYWORD': 'red',
        'ENDTRY_KEYWORD': 'red',
        'RETURN_KEYWORD': 'red',
        'CONTINUE_KEYWORD': 'red',
        'RAISE_KEYWORD': 'red',
        'VAR_KEYWORD': 'red',
        'NOT_KEYWORD': 'red',
        'OR_KEYWORD': 'red',
        'AND_KEYWORD': 'red',
        'NEW_KEYWORD': 'red',
        'GOTO_KEYWORD': 'red',
        'BREAK_KEYWORD': 'red',
        'EXECUTE_KEYWORD': 'red',
        'ADDHANDLER_KEYWORD': 'red',
        'REMOVEHANDLER_KEYWORD': 'red',
        'ASYNC_KEYWORD': 'red',

        'DECIMAL': '#9400D3',
        'FLOAT': '#9400D3',
        'STRING': 'black',
        'UNKNOWN': '#9400D3',
        'IDENTIFIER': 'blue',
        'LINE_COMMENT': 'green',
        'PREPROC_USE_KEYWORD': 'brown',
        'PREPROC_REGION': 'brown',
        'PREPROC_END_REGION': 'red',
        'PREPROC_NOT_KEYWORD': 'red',
        'PREPROC_OR_KEYWORD': 'red',
        'PREPROC_AND_KEYWORD': 'red',
        'PREPROC_IF_KEYWORD': 'red',
        'PREPROC_THEN_KEYWORD': 'red',
        'PREPROC_ELSIF_KEYWORD': 'red',
        'PREPROC_ENDIF_KEYWORD': 'red',
        'PREPROC_ELSE_KEYWORD': 'red',
        'PREPROC_MOBILEAPPCLIENT_SYMBOL': 'red',
        'PREPROC_MOBILEAPPSERVER_SYMBOL': 'red',
        'PREPROC_MOBILECLIENT_SYMBOL': 'red',
        'PREPROC_THICKCLIENTORDINARYAPPLICATION_SYMBOL': 'red',
        'PREPROC_THICKCLIENTMANAGEDAPPLICATION_SYMBOL': 'red',
        'PREPROC_EXTERNALCONNECTION_SYMBOL': 'red',
        'PREPROC_THINCLIENT_SYMBOL': 'red',
        'PREPROC_WEBCLIENT_SYMBOL': 'red',
        'PREPROC_ATCLIENT_SYMBOL': 'red',
        'PREPROC_CLIENT_SYMBOL': 'red',
        'PREPROC_ATSERVER_SYMBOL': 'red',
        'PREPROC_SERVER_SYMBOL': 'red',
        'PREPROC_MOBILE_STANDALONE_SERVER': 'red',
        'ANNOTATION_ATSERVERNOCONTEXT_SYMBOL': 'brown',
        'ANNOTATION_ATCLIENTATSERVERNOCONTEXT_SYMBOL': 'brown',
        'ANNOTATION_ATCLIENTATSERVER_SYMBOL': 'brown',
        'ANNOTATION_ATCLIENT_SYMBOL': 'brown',
        'ANNOTATION_ATSERVER_SYMBOL': 'brown',
        'ANNOTATION_BEFORE_SYMBOL': 'brown',
        'ANNOTATION_AFTER_SYMBOL': 'brown',
        'ANNOTATION_AROUND_SYMBOL': 'brown',
        'ANNOTATION_CHANGEANDVALIDATE_SYMBOL': 'brown',
        'ANNOTATION_CUSTOM_SYMBOL': 'brown',
        'ANNOTATION_WHITE_SPACE': 'brown',
        'ANNOTATION_UNKNOWN': 'brown',
    }

    for token_name, color in colors.items():
        text_widget.tag_configure(token_name, foreground=color)

    # Проходим по токенам
    while token.type != Token.EOF:
        token_type = lexer.symbolicNames[token.type]
        token_text = token.text  # Текст токена

        # ОТЛАДКА: выводим информацию о токене
        print(f"Текст: '{token_text}' | Тип: {token_type} | Тип токена (число): {token.type}")
        
        # Проверяем, является ли это ключевым словом, но распознано как IDENTIFIER
        keywords_map = {
            'Процедура': 'PROCEDURE_KEYWORD',
            'КонецПроцедуры': 'ENDPROCEDURE_KEYWORD',
            'Функция': 'FUNCTION_KEYWORD',
            'КонецФункции': 'ENDFUNCTION_KEYWORD',
            'Если': 'IF_KEYWORD',
            'ИначеЕсли': 'ELSIF_KEYWORD',
            'Иначе': 'ELSE_KEYWORD',
            'Тогда': 'THEN_KEYWORD',
            'Пока': 'WHILE_KEYWORD',
        }
        
        # Если токен распознан как IDENTIFIER, но это ключевое слово - исправляем
        if token_type == 'IDENTIFIER' and token_text in keywords_map:
            print(f"⚠️ ИСПРАВЛЕНИЕ: '{token_text}' распознано как IDENTIFIER, исправляем на {keywords_map[token_text]}")
            token_type = keywords_map[token_text]

        if token_type in colors:
            # Находим нужный фрагмент текста
            start_line, start_column = token.line, token.column
            end_line = start_line
            end_column = start_column + len(token.text)

            # Формируем строки для Tkinter тегов
            start_tag = f"{start_line}.{start_column}"
            end_tag = f"{end_line}.{end_column}"

            # Добавляем тег и настраиваем форматирование
            text_widget.tag_add(token_type, start_tag, end_tag)


        token = lexer.nextToken()


# Настройка темы CustomTkinter
ctk.set_appearance_mode("System")  # "System", "Light", "Dark"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"

# Создаем главное окно
app = ctk.CTk()
app.title("1C Syntax Highlighter")
app.geometry("900x700")

# Получаем цвет фона для Text виджета, чтобы он соответствовал теме
if ctk.get_appearance_mode() == "Dark":
    text_bg = "#1a1a1a"
    text_fg = "#ffffff"
    cursor_color = "#ffffff"
else:
    text_bg = "#ffffff"
    text_fg = "#000000"
    cursor_color = "#000000"


# Фрейм для размещения элементов
main_frame = ctk.CTkFrame(app)
main_frame.pack(fill="both", expand=True, padx=20, pady=20)

# Метка
label = ctk.CTkLabel(main_frame, text="Введите код на 1С:", font=("Arial", 14))
label.pack(pady=(0, 10))

# Фрейм для текстового поля с прокруткой
text_frame = ctk.CTkFrame(main_frame)
text_frame.pack(fill="both", expand=True, pady=(0, 10))

# Создаем стандартный Text виджет для поддержки подсветки синтаксиса
text_widget = tk.Text(
    text_frame,
    wrap="word",
    font=("Courier", 12),
    bg=text_bg,
    fg=text_fg,
    insertbackground=cursor_color,
    relief="flat",
    borderwidth=0,
    padx=10,
    pady=10
)

# Создаем Scrollbar для Text виджета
scrollbar = ctk.CTkScrollbar(text_frame, orientation="vertical", command=text_widget.yview)
text_widget.configure(yscrollcommand=scrollbar.set)

# Размещаем Text и Scrollbar
text_widget.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")


def on_text_change(event=None):
    """Обработчик изменения текста"""
    text = text_widget.get("1.0", tk.END)
    if text.strip():  # Подсветка только если есть текст
        apply_syntax_highlighting(text_widget, text.rstrip())


def on_button_click():
    """Обработчик нажатия кнопки"""
    text = text_widget.get("1.0", tk.END)
    if text.strip():  # Подсветка только если есть текст
        apply_syntax_highlighting(text_widget, text.rstrip())


# Привязываем событие изменения текста (при вводе, вставке и т.д.)
text_widget.bind("<KeyRelease>", on_text_change)
text_widget.bind("<Button-1>", on_text_change)  # При клике (для вставки через контекстное меню)

# Кнопка для подсветки синтаксиса
button = ctk.CTkButton(
    main_frame,
    text="Подсветить синтаксис",
    command=on_button_click,
    font=("Arial", 14),
    height=40
)
button.pack(pady=10)

# Запуск приложения
app.mainloop()
