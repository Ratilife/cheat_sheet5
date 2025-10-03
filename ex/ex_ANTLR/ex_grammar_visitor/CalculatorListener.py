# Generated from Calculator.g4 by ANTLR 4.13.1
from antlr4 import *
if "." in __name__:
    from .CalculatorParser import CalculatorParser
else:
    from CalculatorParser import CalculatorParser

# This class defines a complete listener for a parse tree produced by CalculatorParser.
class CalculatorListener(ParseTreeListener):

    # Enter a parse tree produced by CalculatorParser#Multiplication.
    def enterMultiplication(self, ctx:CalculatorParser.MultiplicationContext):
        pass

    # Exit a parse tree produced by CalculatorParser#Multiplication.
    def exitMultiplication(self, ctx:CalculatorParser.MultiplicationContext):
        pass


    # Enter a parse tree produced by CalculatorParser#Addition.
    def enterAddition(self, ctx:CalculatorParser.AdditionContext):
        pass

    # Exit a parse tree produced by CalculatorParser#Addition.
    def exitAddition(self, ctx:CalculatorParser.AdditionContext):
        pass


    # Enter a parse tree produced by CalculatorParser#Subtraction.
    def enterSubtraction(self, ctx:CalculatorParser.SubtractionContext):
        pass

    # Exit a parse tree produced by CalculatorParser#Subtraction.
    def exitSubtraction(self, ctx:CalculatorParser.SubtractionContext):
        pass


    # Enter a parse tree produced by CalculatorParser#Number.
    def enterNumber(self, ctx:CalculatorParser.NumberContext):
        pass

    # Exit a parse tree produced by CalculatorParser#Number.
    def exitNumber(self, ctx:CalculatorParser.NumberContext):
        pass


    # Enter a parse tree produced by CalculatorParser#Division.
    def enterDivision(self, ctx:CalculatorParser.DivisionContext):
        pass

    # Exit a parse tree produced by CalculatorParser#Division.
    def exitDivision(self, ctx:CalculatorParser.DivisionContext):
        pass


    # Enter a parse tree produced by CalculatorParser#Parentheses.
    def enterParentheses(self, ctx:CalculatorParser.ParenthesesContext):
        pass

    # Exit a parse tree produced by CalculatorParser#Parentheses.
    def exitParentheses(self, ctx:CalculatorParser.ParenthesesContext):
        pass



del CalculatorParser