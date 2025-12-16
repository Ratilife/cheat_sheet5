import sys
import os

# Добавляем путь к корню проекта
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from antlr4 import InputStream, CommonTokenStream
from src.ANTLR4.st_grammar.STFileLexer import STFileLexer


def analyze_tokens(input_text):
    """
    Практический анализ токенов с выявлением проблем грамматики
    """
    input_stream = InputStream(input_text)
    lexer = STFileLexer(input_stream)
    stream = CommonTokenStream(lexer)
    stream.fill()

    print("=== ПРАКТИЧЕСКИЙ АНАЛИЗ ТОКЕНОВ ===")
    print(f"Входные данные: {input_text}")
    print(f"Всего токенов: {len(stream.tokens)}")
    print("-" * 50)

    token_groups = {}
    problematic_tokens = []

    # Анализируем каждый токен
    for i, token in enumerate(stream.tokens):
        if token.type == -1:  # EOF токен
            print(f"[@{i}] <EOF> - конец потока")
            continue

        # Получаем имя токена
        token_name = f"Тип_{token.type}"
        if token.type < len(lexer.symbolicNames) and lexer.symbolicNames[token.type]:
            token_name = lexer.symbolicNames[token.type]

        # Группируем токены по типам для статистики
        if token_name not in token_groups:
            token_groups[token_name] = []
        token_groups[token_name].append(token.text)

        # Проверяем на возможные проблемы
        if token_name.startswith('Тип_'):
            problematic_tokens.append(f"Токен {i}: '{token.text}' не имеет символического имени")
        elif token_name == 'WS' and '"' in token.text:
            problematic_tokens.append(f"Токен {i}: '{token.text}' ошибочно классифицирован как пробел")

        # Форматируем вывод
        line_info = f"строка {token.line}:{token.column}"
        print(f"[@{i}] {token_name:15} = '{token.text:20}' ({line_info})")

    # Анализ результатов
    print("\n" + "=" * 50)
    print("СТАТИСТИЧЕСКИЙ АНАЛИЗ:")
    for token_type, tokens in token_groups.items():
        if token_type != '<EOF>':
            print(f"  {token_type:15}: {len(tokens):2} шт. ({tokens})")

    # Практические выводы
    print("\n" + "=" * 50)
    print("ПРАКТИЧЕСКИЕ ВЫВОДЫ:")

    if problematic_tokens:
        print("⚠️  ОБНАРУЖЕНЫ ПРОБЛЕМЫ В ГРАММАТИКЕ:")
        for problem in problematic_tokens:
            print(f"  • {problem}")
        print("\n  РЕКОМЕНДАЦИИ:")
        print("  1. Проверьте порядок правил лексера в STFile.g4")
        print("  2. Убедитесь, что все токены имеют символические имена")
        print("  3. Специфичные правила должны идти перед общими")
    else:
        print("✅ Грамматика корректно распознает токены")

    # Проверка соответствия ожидаемой структуре
    print("\n  СТРУКТУРНЫЙ АНАЛИЗ:")
    brace_count = sum(1 for t in stream.tokens if '{' in str(t.text) or '}' in str(t.text))
    string_count = sum(1 for t in stream.tokens if '"' in str(t.text))
    print(f"  • Фигурные скобки: {brace_count}")
    print(f"  • Строковые литералы: {string_count}")

    return stream, problematic_tokens


# Тестовые данные
test_input = '{1, {1, {"Folder", 1, 0, "type", "name"}}}'

if __name__ == '__main__':
    stream, problems = analyze_tokens(test_input)