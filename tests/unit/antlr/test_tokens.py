import sys
import os

from antlr4 import FileStream, CommonTokenStream, ParseTreeWalker, InputStream
from src.ANTLR4.st_grammar.STFileLexer import STFileLexer
from src.ANTLR4.st_grammar.STFileParser import STFileParser

# Добавил путь к корню проекта
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

test_input = '{1, {1, {"Folder", 1, 0, "type", "name"}}}'
def basic_token_analysis(input_text):
    """Базовый анализ токенов"""
    input_stream = InputStream(input_text)
    lexer = STFileLexer(input_stream)
    stream = CommonTokenStream(lexer)

    # Заполняем поток токенов
    stream.fill()

    print("=== АНАЛИЗ ТОКЕНОВ ===")
    print(f"Всего токенов: {len(stream.tokens)}")
    print("-" * 50)

    # Выводим все токены
    for i, token in enumerate(stream.tokens):
        if token.type == -1:  # EOF токен
            print(f"[@{i}] <EOF>")
            break

        # Получаем имя токена из лексических символов
        token_type_name = lexer.symbolicNames[token.type]

        # Форматируем вывод
        line_info = f"строка {token.line}:{token.column}"
        print(f"[@{i}] {token_type_name:15} = '{token.text:20}' ({line_info})")

    return stream

if __name__ == '__main__':
    # Пример использования
    stream = basic_token_analysis(test_input)