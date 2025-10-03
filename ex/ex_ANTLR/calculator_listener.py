import sys
from antlr4 import *
from ex_grammar_listener.CalculatorLexer import CalculatorLexer
from ex_grammar_listener.CalculatorParser import CalculatorParser
from ex_grammar_listener.CalculatorListener import CalculatorListener

class CalkEvalListener(CalculatorListener):
    def __init__(self):
        self.stack = []     # Стек для хранения промежуточных результатов

    def exitNumber(self,ctx):
        # При выходе из правила int, помещаем число в стек
        value = int(ctx.NUMBER().getText())
        self.stack.append(value)

    def exitMultiplication(self, ctx:CalculatorParser.MultiplicationContext):
        #Извлекаем два последних значения из стека
        right = self.stack.pop()
        left = self.stack.pop()
        # Выполняем операцию умножения и помещаем результат обратно в стек
        self.stack.append(left*right)

    def exitDivision(self, ctx:CalculatorParser.DivisionContext):
        # Извлекаем два последних значения из стека
        right = self.stack.pop()
        left = self.stack.pop()
        # Выполняем операцию деления и помещаем результат обратно в стек
        if right == 0:
            raise ZeroDivisionError("Деление на ноль!")
        self.stack.append(left // right)  # Целочисленное деление

    def exitAddition(self, ctx):
        # Извлекаем два последних значения из стека
        right = self.stack.pop()
        left = self.stack.pop()

        # Выполняем операцию сложения и помещаем результат обратно в стек
        self.stack.append(left + right)

    def exitSubtraction(self, ctx):
        # Извлекаем два последних значения из стека
        right = self.stack.pop()
        left = self.stack.pop()

        # Выполняем операцию вычитания и помещаем результат обратно в стек
        self.stack.append(left - right)

    def exitParentheses(self, ctx):
        # Для скобок ничего не делаем - результат выражения уже в стеке
        pass

    def get_result(self):
        # Возвращаем конечный результат из стека
        return self.stack[0] if self.stack else None

def main1():
    if len(sys.argv)>1:
        input_stream = InputStream(sys.argv[1])
    else:
        input_stream = InputStream(input("Введите выражение: "))

    #Создаем лексер, парсер и дерево разбора
    lexer = CalculatorLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = CalculatorParser(stream)
    tree = parser.expression() # Начинаем разбор с правила 'expression'

    # Создаем обходчик и наш слушатель
    walker = ParseTreeWalker()
    listener = CalkEvalListener()

    # Обходим дерево с нашим слушателем
    walker.walk(listener,tree)

    # Получаем и выводим результат
    result = listener.get_result()
    print(f"Результат: {result}")


def main():
    while True:
        try:
            if len(sys.argv) > 1:
                input_stream = InputStream(sys.argv[1])
                # Очищаем аргументы командной строки после первого использования
                sys.argv = [sys.argv[0]]
            else:
                user_input = input("Введите выражение (или 'выход' для завершения): ")

                # Проверяем, не хочет ли пользователь выйти
                if user_input.lower() in ('выход', 'exit', 'quit', 'q'):
                    print("Завершение работы калькулятора.")
                    break

                # Пропускаем пустые вводы
                if not user_input.strip():
                    continue

                input_stream = InputStream(user_input)

            # Создаем лексер, парсер и дерево разбора
            lexer = CalculatorLexer(input_stream)
            stream = CommonTokenStream(lexer)
            parser = CalculatorParser(stream)
            tree = parser.expression()  # Начинаем разбор с правила 'expression'

            # Создаем обходчик и наш слушатель
            walker = ParseTreeWalker()
            listener = CalkEvalListener()

            # Обходим дерево с нашим слушателем
            walker.walk(listener, tree)

            # Получаем и выводим результат
            result = listener.get_result()
            print(f"Результат: {result}")
            print()  # Пустая строка для разделения

        except EOFError:
            print("\nЗавершение работы калькулятора.")
            break
        except KeyboardInterrupt:
            print("\nЗавершение работы калькулятора.")
            break
        except Exception as e:
            print(f"Ошибка: {e}")
            print("Попробуйте еще раз.\n")

if __name__ == '__main__':
    main()






