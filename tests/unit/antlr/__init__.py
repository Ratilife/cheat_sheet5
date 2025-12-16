# run_st_parser.py

import argparse
import sys
import time
from antlr4 import FileStream, CommonTokenStream, ParseTreeWalker
from src.ANTLR4.st_grammar.STFileLexer import STFileLexer
from src.ANTLR4.st_grammar.STFileParser import STFileParser

def main(argv):
    parser = argparse.ArgumentParser(description='Запуск сгенерированного ANTLR4 Python-парсера.')
    # Путь к файлу для разбора
    parser.add_argument('input_file', type=str, help='Путь к входному файлу для разбора')
    # Имя стартового правила (по умолчанию 'fileStructure')
    parser.add_argument('start_rule', type=str, default='fileStructure', nargs='?', help='Имя стартового правила (по умолчанию: fileStructure)')
    # Только токены
    parser.add_argument('-tokens', action='store_true', help='Вывести только токены (фаза лексического анализа)')
    # Вывести дерево разбора в LISP-формате
    parser.add_argument('-tree', action='store_true', help='Вывести дерево разбора в LISP-формате после парсинга')
    # Попытаться показать GUI дерево разбора
    parser.add_argument('-gui', action='store_true', help='Попытаться отобразить графическое дерево разбора (требует tkinter и TreeViewer - не стандарт)')

    args = parser.parse_args()

    input_stream = None
    try:
        # 1. Создать поток символов из файла
        input_stream = FileStream(args.input_file, encoding='utf-8')
    except FileNotFoundError:
        print(f"Ошибка: Файл '{args.input_file}' не найден.", file=sys.stderr)
        return 1
    except UnicodeDecodeError as e:
        print(f"Ошибка чтения файла '{args.input_file}': {e}", file=sys.stderr)
        print("Убедитесь, что кодировка файла соответствует ожидаемой FileStream (по умолчанию utf-8).", file=sys.stderr)
        return 1

    # 2. Создать лексер
    lexer = STFileLexer(input_stream)

    # 3. Создать поток токенов из лексера
    token_stream = CommonTokenStream(lexer)

    # Проверить, нужно ли только вывести токены
    if args.tokens:
        token_stream.fill() # Заполнить поток, чтобы пройтись по всем токенам
        for token in token_stream.tokens:
            if token.type == lexer.EOF:
                break
            print(f"{token.type} '{token.text}' <{lexer.symbolicNames[token.type]}> @{token.line}:{token.column}")
        return 0

    # 4. Создать парсер
    parser_instance = STFileParser(token_stream)

    # 5. Вызвать указанное стартовое правило
    # Использовать getattr для динамического вызова метода, соответствующего имени стартового правила
    start_rule_func = getattr(parser_instance, args.start_rule, None)
    if start_rule_func is None:
        print(f"Ошибка: Стартовое правило '{args.start_rule}' не найдено в сгенерированном парсере.", file=sys.stderr)
        print(f"Возможные правила могут включать: {[method for method in dir(parser_instance) if not method.startswith('_') and callable(getattr(parser_instance, method))]}", file=sys.stderr)
        return 1

    start_time = time.time()
    try:
        # 6. Выполнить стартовое правило, чтобы получить дерево разбора
        tree = start_rule_func()
        parse_time = time.time() - start_time
        print(f"Разбор успешно завершен за {parse_time:.3f} секунд.", file=sys.stderr)

        # 7. Вывести дерево, если запрошено
        if args.tree:
             print(tree.toStringTree(recog=parser_instance))

        # 8. Отобразить графическое дерево, если запрошено
        # Примечание: Стандартная библиотека antlr4-python3-runtime НЕ включает TreeViewer.
        # Вам потребуется сторонняя библиотека или реализация самостоятельно.
        # Эта часть демонстрирует *намерение*, но, скорее всего, потребует дополнительной настройки или библиотек.
        if args.gui:
             print("Запрошено графическое представление дерева (-gui).")
             print("Стандартная библиотека antlr4-python3-runtime не включает встроенный просмотрщик, как TestRig в Java.")
             print("Вам может потребоваться использовать пользовательское решение или стороннюю библиотеку для визуализации дерева.")
             # Пример использования гипотетического просмотрщика (не стандарт):
             # from some_tree_viewer import TreeViewer
             # viewer = TreeViewer(tree, parser_instance)
             # viewer.display()
             # Пока что просто выводим сообщение, указывающее, что это не доступно по умолчанию.
             # Или, вы можете вывести дерево в LISP-формате как запасной вариант, если просмотрщик не найден.
             print("--- ДЕРЕВО РАЗБОРА (LISP-ФОРМАТ) ---")
             print(tree.toStringTree(recog=parser_instance))
             print("--- КОНЕЦ ДЕРЕВА ---")


    except Exception as e:
        print(f"Разбор не удался с ошибкой: {e}", file=sys.stderr)
        return 1

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))