# Описание типов токенов 1C

## Операторы и разделители

- `'DOT'` - Точка
- `'LBRACK'` - Левая квадратная скобка [
- `'RBRACK'` - Правая квадратная скобка ]
- `'LPAREN'` - Левая круглая скобка (
- `'RPAREN'` - Правая круглая скобка )
- `'COLON'` - Двоеточие :
- `'SEMICOLON'` - Точка с запятой ;
- `'COMMA'` - Запятая ,
- `'ASSIGN'` - Оператор присваивания =
- `'PLUS'` - Плюс +
- `'MINUS'` - Минус -
- `'LESS_OR_EQUAL'` - Меньше или равно <=
- `'NOT_EQUAL'` - Не равно <>
- `'LESS'` - Меньше <
- `'GREATER_OR_EQUAL'` - Больше или равно >=
- `'GREATER'` - Больше >
- `'MUL'` - Умножение *
- `'QUOTIENT'` - Деление /
- `'MODULO'` - Остаток от деления %
- `'QUESTION'` - Вопросительный знак ?
- `'AMPERSAND'` - Амперсанд &

## Ключевые слова процедур и функций

- `'PROCEDURE_KEYWORD'` - Процедура
- `'FUNCTION_KEYWORD'` - Функция
- `'ENDPROCEDURE_KEYWORD'` - КонецПроцедуры
- `'ENDFUNCTION_KEYWORD'` - КонецФункции
- `'EXPORT_KEYWORD'` - Экспорт
- `'VAL_KEYWORD'` - Знач

## Ключевые слова условных операторов

- `'IF_KEYWORD'` - Если
- `'ELSIF_KEYWORD'` - ИначеЕсли
- `'ELSE_KEYWORD'` - Иначе
- `'THEN_KEYWORD'` - Тогда
- `'ENDIF_KEYWORD'` - КонецЕсли

## Ключевые слова циклов

- `'WHILE_KEYWORD'` - Пока
- `'DO_KEYWORD'` - Цикл
- `'ENDDO_KEYWORD'` - КонецЦикла
- `'FOR_KEYWORD'` - Для
- `'TO_KEYWORD'` - По
- `'EACH_KEYWORD'` - Каждого
- `'IN_KEYWORD'` - Из

## Ключевые слова обработки исключений

- `'TRY_KEYWORD'` - Попытка
- `'EXCEPT_KEYWORD'` - Исключение
- `'ENDTRY_KEYWORD'` - КонецПопытки

## Ключевые слова управления выполнением

- `'RETURN_KEYWORD'` - Возврат
- `'CONTINUE_KEYWORD'` - Продолжить
- `'BREAK_KEYWORD'` - Прервать
- `'RAISE_KEYWORD'` - ВызватьИсключение
- `'GOTO_KEYWORD'` - Перейти

## Прочие ключевые слова

- `'VAR_KEYWORD'` - Перем
- `'NOT_KEYWORD'` - Не
- `'OR_KEYWORD'` - Или
- `'AND_KEYWORD'` - И
- `'NEW_KEYWORD'` - Новый
- `'EXECUTE_KEYWORD'` - Выполнить
- `'ADDHANDLER_KEYWORD'` - ДобавитьОбработчик
- `'REMOVEHANDLER_KEYWORD'` - УдалитьОбработчик
- `'ASYNC_KEYWORD'` - Асинхронный

## Логические и специальные значения

- `'TRUE'` - Истина
- `'FALSE'` - Ложь
- `'UNDEFINED'` - Неопределено
- `'NULL'` - NULL

## Типы данных

- `'DECIMAL'` - Число (десятичное)
- `'FLOAT'` - Число (с плавающей точкой)
- `'STRING'` - Строка
- `'UNKNOWN'` - Неизвестный тип

## Идентификаторы и комментарии

- `'IDENTIFIER'` - Идентификатор
- `'LINE_COMMENT'` - Строковый комментарий

## Директивы препроцессора

- `'PREPROC_DELETE'` - Удаление кода
- `'PREPROC_INSERT'` - Вставка кода
- `'PREPROC_ENDINSERT'` - Конец вставки кода
- `'PREPROC_USE_KEYWORD'` - Использовать
- `'PREPROC_REGION'` - Область
- `'PREPROC_END_REGION'` - КонецОбласти
- `'PREPROC_NOT_KEYWORD'` - Не (в препроцессоре)
- `'PREPROC_OR_KEYWORD'` - Или (в препроцессоре)
- `'PREPROC_AND_KEYWORD'` - И (в препроцессоре)
- `'PREPROC_IF_KEYWORD'` - Если (в препроцессоре)
- `'PREPROC_THEN_KEYWORD'` - Тогда (в препроцессоре)
- `'PREPROC_ELSIF_KEYWORD'` - ИначеЕсли (в препроцессоре)
- `'PREPROC_ENDIF_KEYWORD'` - КонецЕсли (в препроцессоре)
- `'PREPROC_ELSE_KEYWORD'` - Иначе (в препроцессоре)

## Символы платформ препроцессора

- `'PREPROC_MOBILEAPPCLIENT_SYMBOL'` - МобильноеПриложениеКлиент
- `'PREPROC_MOBILEAPPSERVER_SYMBOL'` - МобильноеПриложениеСервер
- `'PREPROC_MOBILECLIENT_SYMBOL'` - МобильныйКлиент
- `'PREPROC_THICKCLIENTORDINARYAPPLICATION_SYMBOL'` - ТолстыйКлиентОбычноеПриложение
- `'PREPROC_THICKCLIENTMANAGEDAPPLICATION_SYMBOL'` - ТолстыйКлиентУправляемоеПриложение
- `'PREPROC_EXTERNALCONNECTION_SYMBOL'` - ВнешнееСоединение
- `'PREPROC_THINCLIENT_SYMBOL'` - ТонкийКлиент
- `'PREPROC_WEBCLIENT_SYMBOL'` - ВебКлиент
- `'PREPROC_ATCLIENT_SYMBOL'` - НаКлиенте
- `'PREPROC_CLIENT_SYMBOL'` - Клиент
- `'PREPROC_ATSERVER_SYMBOL'` - НаСервере
- `'PREPROC_SERVER_SYMBOL'` - Сервер
- `'PREPROC_MOBILE_STANDALONE_SERVER'` - МобильныйАвтономныйСервер

## Аннотации

- `'ANNOTATION_ATSERVERNOCONTEXT_SYMBOL'` - НаСервереБезКонтекста
- `'ANNOTATION_ATCLIENTATSERVERNOCONTEXT_SYMBOL'` - НаКлиентеНаСервереБезКонтекста
- `'ANNOTATION_ATCLIENTATSERVER_SYMBOL'` - НаКлиентеНаСервере
- `'ANNOTATION_ATCLIENT_SYMBOL'` - НаКлиенте
- `'ANNOTATION_ATSERVER_SYMBOL'` - НаСервере
- `'ANNOTATION_BEFORE_SYMBOL'` - Перед
- `'ANNOTATION_AFTER_SYMBOL'` - После
- `'ANNOTATION_AROUND_SYMBOL'` - Вокруг
- `'ANNOTATION_CHANGEANDVALIDATE_SYMBOL'` - ИзменитьИПроверить
- `'ANNOTATION_CUSTOM_SYMBOL'` - Пользовательская аннотация
- `'ANNOTATION_WHITE_SPACE'` - Пробел в аннотации
- `'ANNOTATION_UNKNOWN'` - Неизвестная аннотация

- `'PREPROC_ENDDELETE'`- Удаление
- `'PREPROC_DELETE_ANY'`-
- `'AWAIT_KEYWORD'`- Ждать