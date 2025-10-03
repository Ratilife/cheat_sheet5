import sys
from antlr4 import *
from ex_grammar_visitor.CalculatorLexer import CalculatorLexer
from ex_grammar_visitor.CalculatorParser import CalculatorParser
from ex_grammar_visitor.CalculatorVisitor import CalculatorVisitor


class CalcEvalVisitor(CalculatorVisitor):

    def visitNumber(self, ctx):
        # Посещаем правило Number: возвращаем числовое значение
        return int(ctx.NUMBER().getText())

    def visitParentheses(self, ctx):
        # Посещаем правило Parentheses: возвращаем результат выражения в скобках
        return self.visit(ctx.expression())

    def visitMultiplication(self, ctx):
        # Посещаем правило Multiplication: рекурсивно вычисляем левую и правую части
        left = self.visit(ctx.expression(0))
        right = self.visit(ctx.expression(1))
        return left * right

    def visitDivision(self, ctx):
        # Посещаем правило Division: рекурсивно вычисляем левую и правую части
        left = self.visit(ctx.expression(0))
        right = self.visit(ctx.expression(1))

        if right == 0:
            raise ZeroDivisionError("Деление на ноль!")
        return left // right  # Целочисленное деление

    def visitAddition(self, ctx):
        # Посещаем правило Addition: рекурсивно вычисляем левую и правую части
        left = self.visit(ctx.expression(0))
        right = self.visit(ctx.expression(1))
        return left + right

    def visitSubtraction(self, ctx):
        # Посещаем правило Subtraction: рекурсивно вычисляем левую и правую части
        left = self.visit(ctx.expression(0))
        right = self.visit(ctx.expression(1))
        return left - right


def main():
    if len(sys.argv) > 1:
        input_stream = InputStream(sys.argv[1])
    else:
        input_stream = InputStream(input("Введите выражение: "))

    # Создаем лексер, парсер и дерево разбора
    lexer = CalculatorLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = CalculatorParser(stream)
    tree = parser.expression()  # Начинаем разбор с правила 'expression'

    # Создаем нашего посетителя и обходим дерево
    visitor = CalcEvalVisitor()
    result = visitor.visit(tree)

    print(f"Результат: {result}")


if __name__ == '__main__':
    main()