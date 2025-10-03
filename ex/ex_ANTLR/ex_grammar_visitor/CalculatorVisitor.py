# Generated from Calculator.g4 by ANTLR 4.13.1
from antlr4 import *
if "." in __name__:
    from .CalculatorParser import CalculatorParser
else:
    from CalculatorParser import CalculatorParser

# Этот класс определяет полного универсального посетителя для дерева синтаксического анализа, созданного CalculatorParser.

class CalculatorVisitor(ParseTreeVisitor):

    # Посетите дерево синтаксического анализа, созданное CalculatorParser#Multiplication.
    def visitMultiplication(self, ctx:CalculatorParser.MultiplicationContext):
        return self.visitChildren(ctx)


    # Посетите дерево синтаксического анализа, созданное CalculatorParser#Addition.
    def visitAddition(self, ctx:CalculatorParser.AdditionContext):
        return self.visitChildren(ctx)


    # Посетите дерево синтаксического анализа, созданное CalculatorParser#Subtraction.
    def visitSubtraction(self, ctx:CalculatorParser.SubtractionContext):
        return self.visitChildren(ctx)


    # Посетите дерево синтаксического анализа, созданное CalculatorParser#Number.
    def visitNumber(self, ctx:CalculatorParser.NumberContext):
        return self.visitChildren(ctx)


    # Посетите дерево синтаксического анализа, созданное CalculatorParser#Division.
    def visitDivision(self, ctx:CalculatorParser.DivisionContext):
        return self.visitChildren(ctx)


    # Посетите дерево синтаксического анализа, созданное CalculatorParser#Parentheses.
    def visitParentheses(self, ctx:CalculatorParser.ParenthesesContext):
        return self.visitChildren(ctx)



del CalculatorParser