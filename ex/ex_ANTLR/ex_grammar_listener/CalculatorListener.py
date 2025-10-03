"""
Основная идея заключается в использовании стека для накопления промежуточных результатов.
При выходе из каждого правила мы будем вычислять результат и помещать его обратно в стек.

"""
# Generated from Calculator.g4 by ANTLR 4.13.1

from antlr4 import *
if "." in __name__:
    from .CalculatorParser import CalculatorParser
else:
    from CalculatorParser import CalculatorParser

# Этот класс определяет полный прослушиватель для дерева синтаксического анализа, созданного CalculatorParser.
class CalculatorListener(ParseTreeListener):

    # Введите дерево синтаксического анализа, созданное с помощью CalculatorParser#Multiplication.
    def enterMultiplication(self, ctx:CalculatorParser.MultiplicationContext):
        pass

    # Выход из дерева синтаксического анализа, созданного с помощью CalculatorParser#Multiplication.
    def exitMultiplication(self, ctx:CalculatorParser.MultiplicationContext):
        pass


    # Введите дерево синтаксического анализа, созданное с помощью CalculatorParser#Addition.
    def enterAddition(self, ctx:CalculatorParser.AdditionContext):
        pass

    # Выход из дерева синтаксического анализа, созданного с помощью CalculatorParser#Addition.
    def exitAddition(self, ctx:CalculatorParser.AdditionContext):
        pass


    # Введите дерево синтаксического анализа, созданное с помощью CalculatorParser#Subtraction.
    def enterSubtraction(self, ctx:CalculatorParser.SubtractionContext):
        pass

    # Выход из дерева синтаксического анализа, созданного с помощью CalculatorParser#Subtraction.
    def exitSubtraction(self, ctx:CalculatorParser.SubtractionContext):
        pass


    # Введите дерево синтаксического анализа, созданное с помощью CalculatorParser#Number.
    def enterNumber(self, ctx:CalculatorParser.NumberContext):
        pass

    # Выход из дерева синтаксического анализа, созданного с помощью CalculatorParser#Number.
    def exitNumber(self, ctx:CalculatorParser.NumberContext):
        pass


    # Введите дерево синтаксического анализа, созданное с помощью CalculatorParser#Division.
    def enterDivision(self, ctx:CalculatorParser.DivisionContext):
        pass

    # Выход из дерева синтаксического анализа, созданного с помощью CalculatorParser#Division.
    def exitDivision(self, ctx:CalculatorParser.DivisionContext):
        pass


    # Введите дерево синтаксического анализа, созданное с помощью CalculatorParser#Parentheses.
    def enterParentheses(self, ctx:CalculatorParser.ParenthesesContext):
        pass

    # Выход из дерева синтаксического анализа, созданного с помощью CalculatorParser#Parentheses.
    def exitParentheses(self, ctx:CalculatorParser.ParenthesesContext):
        pass



del CalculatorParser