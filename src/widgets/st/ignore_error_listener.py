from antlr4.error.ErrorListener import ErrorListener
class IgnoreErrorListener(ErrorListener):
    """
    "Тихий" обработчик ошибок для ANTLR лексеров.
    Игнорирует все ошибки лексирования для ускорения работы.
    """

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        """
        Игнорирует ошибки синтаксиса вместо вывода в stderr.

        Args:
            recognizer: Распознаватель ANTLR
            offendingSymbol: Ошибочный символ
            line: Номер строки с ошибкой
            column: Позиция в строке
            msg: Сообщение об ошибке
            e: Исключение
        """
        pass  # Намеренно игнорируем ошибки

    def reportAmbiguity(self, recognizer, dfa, startIndex, stopIndex, exact, ambigAlts, configs):
        """Игнорирует сообщения о неоднозначностях"""
        pass

    def reportAttemptingFullContext(self, recognizer, dfa, startIndex, stopIndex, conflictingAlts, configs):
        """Игнорирует сообщения о попытках полного контекста"""
        pass

    def reportContextSensitivity(self, recognizer, dfa, startIndex, stopIndex, prediction, configs):
        """Игнорирует сообщения о чувствительности к контексту"""
        pass