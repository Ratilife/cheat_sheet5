from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor
from PySide6.QtCore import Qt
from antlr4 import InputStream
from antlr4 import Token
from ANTLR4.one_c_grammar import BSLLexer
class STHighlighter(QSyntaxHighlighter):
    """
        Класс для подсветки синтаксиса в .st файлах.
        Поддерживает множественные языки через ANTLR лексеры.
    """

    def __init__(self, parent=None, language=None):
        """
        Args:
            parent: QTextDocument - документ текста из QTextEdit
            language: str - язык программирования ('1c', 'python', 'csharp', 'java')
        """
        super().__init__(parent)
        self.language = language  # Язык по умолчанию
        self._init_color_map()  # Инициализация цветов

    def _init_color_map(self):
        """Инициализация цветовой схемы для токенов"""
        # Общие цвета для всех языков
        self.color_map = {
            # 1C/BSL
            '1c': {'DOT': 'red',
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
        },
            # Python
            'python': {}, # Будет заполнено позже
            # C#
            'csharp': {},
            # Java
            'java': {}
        }

    def set_language(self, language: str):
        """
        Устанавливает язык программирования для подсветки синтаксиса.

        Этот метод:
        1. Сохраняет язык в self.language
        2. Нормализует язык (приводит к нижнему регистру)
        3. Вызывает rehighlight() для переподсветки всего документа
        4. Позволяет динамически менять язык подсветки

        Args:
            language: str - название языка:
                       - '1c' или 'bsl' для языка 1C/BSL
                       - 'python' для Python
                       - 'csharp' или 'cs' для C#
                       - 'java' для Java
                       - '' или None если язык не определен
        """
        # 1. Нормализация языка
        if language:
            language = language.lower()
            # Можно сделать маппинг синонимов
            language_map = {
                'bsl': '1c',
                'cs': 'csharp',
                'c#': 'csharp'
            }
            language = language_map.get(language, language)
        else:
            language = None

        # 2. Сохранение языка
        old_language = self.language
        self.language = language

        # 3. Переподсветка, если язык изменился
        if old_language != self.language:
            self.rehighlight()  # ← Ключевой момент!

    def highlightBlock(self, text: str):
        """
        Автоматически вызывается Qt для каждой строки текста.
        Это переопределенный метод из QSyntaxHighlighter.

        Args:
            text: str - текст текущей строки
        """
        if not self.language:
            return  # Если язык не определен, не подсвечиваем

        # Вызываем соответствующий метод подсветки
        if self.language == '1c':
            self._apply_1c_highlighting(text)
        elif self.language == 'python':
            self._apply_python_highlighting(text)
        elif self.language == 'csharp':
            self._apply_csharp_highlighting(text)
        elif self.language == 'java':
            self._apply_java_highlighting(text)

    def _apply_token_format(self, token, token_type: str, lang: str):
        """
        Применяет форматирование к токену

        Args:
            token: ANTLR Token объект
            token_type: str - символическое имя токена ('IDENTIFIER', 'PROCEDURE_KEYWORD', etc.)
            lang: str - язык ('1c', 'python', etc.)
        """
        if token_type not in self.color_map.get(lang, {}):
            return

        # Создаем формат
        fmt = QTextCharFormat()
        color = QColor(self.color_map[lang][token_type])
        fmt.setForeground(color)

        # ⭐ ИСПРАВЛЕНИЕ: Позиция токена должна быть относительно начала текущего блока
        # В highlightBlock() мы обрабатываем только одну строку (блок)
        # token.column уже является позицией от начала строки
        start_pos = token.column  # Позиция от начала текущей строки
        length = len(token.text)  # Длина токена

        # Проверяем, что токен находится в текущем блоке
        # (token.line должен совпадать с номером текущего блока)
        current_block_number = self.currentBlock().blockNumber() + 1  # Qt нумерует с 0

        if token.line != current_block_number:
            # Токен из другой строки - пропускаем
            # (это не должно происходить, но для безопасности)
            return

        # Применяем форматирование
        self.setFormat(start_pos, length, fmt)

    def _token_to_position(self, token):
        """
        Конвертирует токен ANTLR в позицию символа в текущем блоке Qt.

        Args:
            token: ANTLR Token объект с атрибутами line, column, text

        Returns:
            int: Позиция символа от начала текущего блока (строки)
        """
        # В highlightBlock() text - это текущая строка
        # token.line начинается с 1, но в Qt блоки нумеруются с 1
        # token.column - позиция в строке (начинается с 0)

        # Получаем позицию начала текущего блока в документе
        block_position = self.currentBlock().position()

        # Получаем номер текущего блока (строки)
        current_block_number = self.currentBlock().blockNumber() + 1  # Qt нумерует с 0

        # Если токен из той же строки (блока), используем column напрямую
        if token.line == current_block_number:
            return token.column

        # Если токен из другой строки - это ошибка логики
        # (но в highlightBlock мы обрабатываем только текущую строку)
        # Просто возвращаем column как относительную позицию
        return token.column

    def _apply_1c_highlighting(self, text: str):
        """Применяет подсветку для языка 1C/BSL"""
        if not text.strip():
            return  # Пустая строка - нечего подсвечивать

        try:
            input_stream = InputStream(text)
            lexer = BSLLexer(input_stream)
            token = lexer.nextToken()

            while token.type != Token.EOF:
                # Получаем символическое имя токена
                if token.type >= 0 and token.type < len(lexer.symbolicNames):
                    token_type = lexer.symbolicNames[token.type]
                    if token_type and token_type != '<INVALID>':
                        # Используем token_type
                        pass

                # Проверяем на валидность
                if token_type and token_type != '<INVALID>':
                    # Применяем форматирование
                    self._apply_token_format(token, token_type, '1c')

                token = lexer.nextToken()
        except Exception as e:
            # Обработка ошибок лексера (чтобы не сломать подсветку)
            print(f"Ошибка подсветки 1C: {e}")

    def _apply_python_highlighting(self, text: str):
        pass

    def _apply_csharp_highlighting(self, text: str):
        pass

    def _apply_java_highlighting(self, text: str):
        pass