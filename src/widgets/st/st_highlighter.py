from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor
from PySide6.QtCore import Qt
from antlr4 import InputStream
from antlr4 import Token
from ANTLR4.one_c_grammar.BSLLexer import BSLLexer
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
        self._tokens_by_line = {}  # dict[int, list[Token]]
        self._document_text = ""  # Текущий текст документа для отслеживания изменений

    def _init_color_map(self):
        """Инициализация цветовой схемы для токенов"""
        # Общие цвета для всех языков
        self.color_map = {
            # 1C/BSL
        '1c': {
        'LINE_COMMENT': 'green',
        'WHITE_SPACE': None,
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
        'QUOTIENT':'red',
        'MODULO': 'red',
        'QUESTION': 'red',
        'AMPERSAND': 'red',
        'PREPROC_DELETE': 'brown',
        'PREPROC_INSERT': 'brown',
        'PREPROC_ENDINSERT': 'brown',
        'HASH': 'brown',
        'BAR': 'black',
        'TILDA': 'black',
        'TRUE': 'red',
        'FALSE': 'red',
        'UNDEFINED': 'red',
        'NULL': 'red',
        'DECIMAL': 'gray',
        'DATETIME': 'gray',
        'FLOAT': 'gray',
        'STRING': 'black',
        'STRINGSTART': 'black',
        'STRINGTAIL': 'black',
        'STRINGPART': 'black',
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
        'NOT_KEYWORD':'red',
        'OR_KEYWORD': 'red',
        'AND_KEYWORD': 'red',
        'NEW_KEYWORD': 'red',
        'GOTO_KEYWORD': 'red',
        'BREAK_KEYWORD': 'red',
        'EXECUTE_KEYWORD': 'red',
        'ADDHANDLER_KEYWORD': 'red',
        'REMOVEHANDLER_KEYWORD': 'red',
        'ASYNC_KEYWORD': 'red',
        'IDENTIFIER': 'blue',
        'UNKNOWN': 'blue',
        'PREPROC_EXCLAMATION_MARK': 'brown',
        'PREPROC_LPAREN': 'brown',
        'PREPROC_RPAREN': 'brown',
        'PREPROC_STRING': 'brown',
        'PREPROC_NATIVE': 'brown',
        'PREPROC_USE_KEYWORD': 'brown',
        'PREPROC_REGION': 'brown',
        'PREPROC_END_REGION': 'brown',
        'PREPROC_NOT_KEYWORD': 'brown',
        'PREPROC_OR_KEYWORD': 'brown',
        'PREPROC_AND_KEYWORD': 'brown',
        'PREPROC_IF_KEYWORD': 'brown',
        'PREPROC_THEN_KEYWORD': 'brown',
        'PREPROC_ELSIF_KEYWORD': 'brown',
        'PREPROC_ENDIF_KEYWORD': 'brown',
        'PREPROC_ELSE_KEYWORD': 'brown',
        'PREPROC_MOBILEAPPCLIENT_SYMBOL': 'brown',
        'PREPROC_MOBILEAPPSERVER_SYMBOL': 'brown',
        'PREPROC_MOBILECLIENT_SYMBOL': 'brown',
        'PREPROC_THICKCLIENTORDINARYAPPLICATION_SYMBOL': 'brown',
        'PREPROC_THICKCLIENTMANAGEDAPPLICATION_SYMBOL': 'brown',
        'PREPROC_EXTERNALCONNECTION_SYMBOL': 'brown',
        'PREPROC_THINCLIENT_SYMBOL': 'brown',
        'PREPROC_WEBCLIENT_SYMBOL': 'brown',
        'PREPROC_ATCLIENT_SYMBOL': 'brown',
        'PREPROC_CLIENT_SYMBOL': 'brown',
        'PREPROC_ATSERVER_SYMBOL':'brown',
        'PREPROC_SERVER_SYMBOL': 'brown',
        'PREPROC_MOBILE_STANDALONE_SERVER': 'brown',
        'PREPROC_LINUX': 'brown',
        'PREPROC_WINDOWS': 'brown',
        'PREPROC_MACOS': 'brown',
        'PREPROC_IDENTIFIER': 'brown',
        'PREPROC_NEWLINE': 'brown',
        'PREPROC_ANY': 'brown',
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
        'ANNOTATION_UNKNOWN': 'brown',
        'PREPROC_ENDDELETE': 'brown',
        'PREPROC_DELETE_ANY': 'brown',
        'AWAIT_KEYWORD': 'red',
        },
            # Python
            'python': {}, # Будет заполнено позже
            # C#
            'csharp': {},
            # Java
            'java': {}
        }

        self.keywords_map = {
            # Процедуры и функции
            'Процедура': 'PROCEDURE_KEYWORD',
            'КонецПроцедуры': 'ENDPROCEDURE_KEYWORD',
            'Функция': 'FUNCTION_KEYWORD',
            'КонецФункции': 'ENDFUNCTION_KEYWORD',
            'Экспорт': 'EXPORT_KEYWORD',
            'Знач': 'VAL_KEYWORD',

            # Условные операторы
            'Если': 'IF_KEYWORD',
            'ИначеЕсли': 'ELSIF_KEYWORD',
            'Иначе': 'ELSE_KEYWORD',
            'Тогда': 'THEN_KEYWORD',
            'КонецЕсли': 'ENDIF_KEYWORD',

            # Циклы
            'Пока': 'WHILE_KEYWORD',
            'Цикл': 'DO_KEYWORD',
            'КонецЦикла': 'ENDDO_KEYWORD',
            'Для': 'FOR_KEYWORD',
            'По': 'TO_KEYWORD',
            'Каждого': 'EACH_KEYWORD',
            'Из': 'IN_KEYWORD',

            # Обработка исключений
            'Попытка': 'TRY_KEYWORD',
            'Исключение': 'EXCEPT_KEYWORD',
            'КонецПопытки': 'ENDTRY_KEYWORD',

            # Управление выполнением
            'Возврат': 'RETURN_KEYWORD',
            'Продолжить': 'CONTINUE_KEYWORD',
            'Прервать': 'BREAK_KEYWORD',
            'ВызватьИсключение': 'RAISE_KEYWORD',
            'Перейти': 'GOTO_KEYWORD',

            # Прочие
            'Перем': 'VAR_KEYWORD',
            'Не': 'NOT_KEYWORD',
            'Или': 'OR_KEYWORD',
            'И': 'AND_KEYWORD',
            'Новый': 'NEW_KEYWORD',
            'Выполнить': 'EXECUTE_KEYWORD',
            'ДобавитьОбработчик': 'ADDHANDLER_KEYWORD',
            'УдалитьОбработчик': 'REMOVEHANDLER_KEYWORD',
            'Асинхронный': 'ASYNC_KEYWORD',

            # Логические значения
            'Истина': 'TRUE',
            'Ложь': 'FALSE',
            'Неопределено': 'UNDEFINED',
            'NULL': 'NULL',
        }

    def set_language(self, language: str):
        """
        Устанавливает язык программирования для подсветки синтаксиса.

        Этот метод:
        1. Нормализует язык (приводит к нижнему регистру)
        2. Сохраняет язык в self.language
        3. Если язык изменился:
            - Пересчитывает кэш токенов (_rebuild_tokens_cache)
            - Вызывает rehighlight() для переподсветки всего документа

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
            # маппинг синонимов
            language_map = {
                'bsl': '1c',
                '1С': '1c',
                '1с': '1c',
                'cs': 'csharp',
                'С#': 'csharp',
                'c#': 'csharp'
            }
            language = language_map.get(language, language)
        else:
            language = None

        # 2. Сохранение языка
        old_language = self.language
        self.language = language

        '''# 3. Переподсветка, если язык изменился
        if old_language != self.language:
            self.rehighlight()  # ← Ключевой момент!'''

        if old_language != self.language:
            self._rebuild_tokens_cache()  # Пересчитываем кэш
            self.rehighlight()  # Переподсвечиваем


    def _rebuild_tokens_cache(self):
        """
        Пересчитывает кэш токенов для всего документа.
        Вызывается при изменении документа или языка.
        """
        print(f"[STHighlighter] rebuild cache, language={self.language}, doc_len={len(self._document_text)}")
        # Очищаем старый кэш
        self._tokens_by_line = {}

        # Если язык не установлен - выходим
        if not self.language or self.language != '1c':
            return

        # Получаем весь текст документа
        if not self.document():
            return

        document_text = self.document().toPlainText()
        self._document_text = document_text  # Сохраняем для сравнения

        # Если документ пуст - выходим
        if not document_text.strip():
            return

        try:
            # Создаём входной поток для всего документа
            input_stream = InputStream(self._document_text)
            lexer = BSLLexer(input_stream)

            # Лексируем весь документ
            token = lexer.nextToken()

            while token.type != Token.EOF:
                # Получаем номер строки токена (ANTLR нумерует с 1)
                line_number = token.line

                # Получаем символическое имя токена сразу
                token_type = None
                if token.type >= 0 and token.type < len(lexer.symbolicNames):
                    token_type = lexer.symbolicNames[token.type]
                    if token_type == '<INVALID>':
                        token_type = None

                lexeme = (token.text or '').lower()
                if lexeme in self.keywords_map:
                    token_type = self.keywords_map[lexeme]

                line_number = token.line

                if line_number not in self._tokens_by_line:
                    self._tokens_by_line[line_number] = []
                self._tokens_by_line[line_number].append((token, token_type))

                '''#  Сохраняем кортеж (токен, тип) вместо просто токена
                if line_number not in self._tokens_by_line:
                    self._tokens_by_line[line_number] = []

                # Добавляем токен в список для его строки
                self._tokens_by_line[line_number].append(token)'''

                # Переходим к следующему токену
                token = lexer.nextToken()
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise
            #self._tokens_by_line = {}  # Очищаем кэш при ошибке

    def highlightBlock(self, text: str):
        """
        Автоматически вызывается Qt для каждой строки текста.
        Это переопределенный метод из QSyntaxHighlighter.

        Args:
            text: str - текст текущей строки
        """
        if not self.language:
            return  # Если язык не определен, не подсвечиваем

        if self.document():
            current_text = self.document().toPlainText()
            if current_text != self._document_text:
                # Текст изменился - пересчитываем кэш
                self._rebuild_tokens_cache()

        # Вызываем соответствующий метод подсветки
        if self.language == '1c':
            self._apply_1c_highlighting(text)
        elif self.language == 'python':
            self._apply_python_highlighting(text)
        elif self.language == 'csharp':
            self._apply_csharp_highlighting(text)
        elif self.language == 'java':
            self._apply_java_highlighting(text)

    def setDocument(self, doc):
        """
        Переопределяем метод для пересчёта кэша при смене документа.
        """
        # Вызываем родительский метод
        super().setDocument(doc)

        # Если документ установлен - пересчитываем кэш
        if doc:
            self._rebuild_tokens_cache()

    def rehighlight(self):
        """
        Переопределяем для пересчёта кэша перед переподсветкой.
        """
        # Проверяем, изменился ли текст документа
        if self.document():
            current_text = self.document().toPlainText()
            if current_text != self._document_text:
                # Текст изменился - пересчитываем кэш
                self._rebuild_tokens_cache()
        # Проверяем актуальность кэша
        if self.document():
            current_text = self.document().toPlainText()
            if current_text != self._document_text:
                # Текст изменился - пересчитываем кэш
                self._rebuild_tokens_cache()

        # Вызываем родительский метод для переподсветки
        super().rehighlight()

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

        # ⭐ ВАЖНО: Позиция токена относительно начала текущего блока (строки)
        # token.column - это позиция от начала строки (начинается с 0)
        # Но нужно учесть, что в ANTLR column может быть с учётом табуляции

        # Получаем позицию начала текущего блока в документе
        block = self.currentBlock()
        #block_start = block.position()  # Позиция начала блока в документе
        block_text = block.text()

        # Позиция токена в строке (от начала строки)
        # В ANTLR column начинается с 0, но может быть с учётом табуляции
        # Для простоты используем column напрямую
        start_pos =  token.column if token.column is not None else 0

        # Длина токена
        length = len(token.text or "")

        # Защита от некорректных значений
        if start_pos < 0:
            start_pos = 0

        if start_pos >= len(block_text):
            # Токен указывает за пределы строки — логируем и выходим
            # print(f"[WARN] token.column вне строки: {start_pos}, длина блока: {len(block_text)}")
            return

        # Если токен "выходит" за пределы строки — подрежем
        if start_pos + length > len(block_text):
            length = len(block_text) - start_pos
            if length <= 0:
                return

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

    def _apply_1c_highlighting_old(self, text: str):
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

    def _apply_1c_highlighting(self, text: str):
        """
        Применяет подсветку для языка 1C/BSL используя кэш токенов.
        """

        # Получаем номер текущего блока (строки)
        # Qt нумерует блоки с 0, но нам нужен номер строки (с 1)
        current_block_number = self.currentBlock().blockNumber() + 1

        # Получаем токены для этой строки из кэша
        tokens_for_line = self._tokens_by_line.get(current_block_number, [])

        # Если токенов нет - выходим
        if not tokens_for_line:
            return
        print(f"[STHighlighter] highlight line {current_block_number}, tokens={len(tokens_for_line)}")
        try:
            # Проходим по всем токенам этой строки
            for item in tokens_for_line:
                # Защита: проверяем структуру данных
                if not isinstance(item, tuple) or len(item) != 2:
                    print(f"[ERROR] Неправильная структура токена: {type(item)}, значение: {item}")
                    continue  # Пропускаем некорректные элементы

                token, token_type = item  # Распаковываем только после проверки
                # Пропускаем невалидные токены
                if not token_type or token_type == '<INVALID>':
                    continue
                # Применяем форматирование
                self._apply_token_format(token, token_type, '1c')

        except Exception as e:
            print(f"Ошибка при обработке токена: {e}")


    def _apply_python_highlighting(self, text: str):
        pass

    def _apply_csharp_highlighting(self, text: str):
        pass

    def _apply_java_highlighting(self, text: str):
        pass