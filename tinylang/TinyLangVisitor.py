# Generated from TinyLang.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .TinyLangParser import TinyLangParser
else:
    from TinyLangParser import TinyLangParser

# This class defines a complete generic visitor for a parse tree produced by TinyLangParser.

class TinyLangVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by TinyLangParser#program.
    def visitProgram(self, ctx:TinyLangParser.ProgramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TinyLangParser#functionDecl.
    def visitFunctionDecl(self, ctx:TinyLangParser.FunctionDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TinyLangParser#paramList.
    def visitParamList(self, ctx:TinyLangParser.ParamListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TinyLangParser#block.
    def visitBlock(self, ctx:TinyLangParser.BlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TinyLangParser#statement.
    def visitStatement(self, ctx:TinyLangParser.StatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TinyLangParser#argList.
    def visitArgList(self, ctx:TinyLangParser.ArgListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TinyLangParser#unaryExpr.
    def visitUnaryExpr(self, ctx:TinyLangParser.UnaryExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TinyLangParser#addExpr.
    def visitAddExpr(self, ctx:TinyLangParser.AddExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TinyLangParser#mulExpr.
    def visitMulExpr(self, ctx:TinyLangParser.MulExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TinyLangParser#orExpr.
    def visitOrExpr(self, ctx:TinyLangParser.OrExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TinyLangParser#postfixExpr.
    def visitPostfixExpr(self, ctx:TinyLangParser.PostfixExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TinyLangParser#assignExpr.
    def visitAssignExpr(self, ctx:TinyLangParser.AssignExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TinyLangParser#equalityExpr.
    def visitEqualityExpr(self, ctx:TinyLangParser.EqualityExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TinyLangParser#relationExpr.
    def visitRelationExpr(self, ctx:TinyLangParser.RelationExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TinyLangParser#andExpr.
    def visitAndExpr(self, ctx:TinyLangParser.AndExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TinyLangParser#postfix.
    def visitPostfix(self, ctx:TinyLangParser.PostfixContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TinyLangParser#primary.
    def visitPrimary(self, ctx:TinyLangParser.PrimaryContext):
        return self.visitChildren(ctx)



del TinyLangParser