# Generated from TinyLang.g4 by ANTLR 4.13.2
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,37,151,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,1,0,1,0,5,0,21,8,0,10,0,12,0,24,9,0,1,0,1,0,1,
        1,1,1,1,1,1,1,3,1,32,8,1,1,1,1,1,1,1,1,2,1,2,1,2,5,2,40,8,2,10,2,
        12,2,43,9,2,1,3,1,3,5,3,47,8,3,10,3,12,3,50,9,3,1,3,1,3,1,4,1,4,
        1,4,1,4,3,4,58,8,4,1,4,1,4,1,4,3,4,63,8,4,1,4,1,4,1,4,1,4,1,4,1,
        4,1,4,1,4,3,4,73,8,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,3,4,
        85,8,4,1,5,1,5,1,5,5,5,90,8,5,10,5,12,5,93,9,5,1,6,1,6,1,6,1,6,1,
        6,1,6,1,6,3,6,102,8,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,
        6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,5,6,122,8,6,10,6,12,6,125,9,6,1,7,
        1,7,1,7,3,7,130,8,7,1,7,5,7,133,8,7,10,7,12,7,136,9,7,1,8,1,8,1,
        8,1,8,1,8,1,8,1,8,1,8,1,8,1,8,1,8,3,8,149,8,8,1,8,0,1,12,9,0,2,4,
        6,8,10,12,14,16,0,5,2,0,20,20,24,24,1,0,12,13,1,0,14,17,1,0,19,20,
        1,0,21,23,172,0,22,1,0,0,0,2,27,1,0,0,0,4,36,1,0,0,0,6,44,1,0,0,
        0,8,84,1,0,0,0,10,86,1,0,0,0,12,101,1,0,0,0,14,126,1,0,0,0,16,148,
        1,0,0,0,18,21,3,2,1,0,19,21,3,8,4,0,20,18,1,0,0,0,20,19,1,0,0,0,
        21,24,1,0,0,0,22,20,1,0,0,0,22,23,1,0,0,0,23,25,1,0,0,0,24,22,1,
        0,0,0,25,26,5,0,0,1,26,1,1,0,0,0,27,28,5,6,0,0,28,29,5,34,0,0,29,
        31,5,25,0,0,30,32,3,4,2,0,31,30,1,0,0,0,31,32,1,0,0,0,32,33,1,0,
        0,0,33,34,5,26,0,0,34,35,3,6,3,0,35,3,1,0,0,0,36,41,5,34,0,0,37,
        38,5,29,0,0,38,40,5,34,0,0,39,37,1,0,0,0,40,43,1,0,0,0,41,39,1,0,
        0,0,41,42,1,0,0,0,42,5,1,0,0,0,43,41,1,0,0,0,44,48,5,27,0,0,45,47,
        3,8,4,0,46,45,1,0,0,0,47,50,1,0,0,0,48,46,1,0,0,0,48,49,1,0,0,0,
        49,51,1,0,0,0,50,48,1,0,0,0,51,52,5,28,0,0,52,7,1,0,0,0,53,54,5,
        1,0,0,54,57,5,34,0,0,55,56,5,18,0,0,56,58,3,12,6,0,57,55,1,0,0,0,
        57,58,1,0,0,0,58,59,1,0,0,0,59,85,5,30,0,0,60,62,5,2,0,0,61,63,3,
        12,6,0,62,61,1,0,0,0,62,63,1,0,0,0,63,64,1,0,0,0,64,85,5,30,0,0,
        65,66,5,3,0,0,66,67,5,25,0,0,67,68,3,12,6,0,68,69,5,26,0,0,69,72,
        3,6,3,0,70,71,5,4,0,0,71,73,3,6,3,0,72,70,1,0,0,0,72,73,1,0,0,0,
        73,85,1,0,0,0,74,75,5,5,0,0,75,76,5,25,0,0,76,77,3,12,6,0,77,78,
        5,26,0,0,78,79,3,6,3,0,79,85,1,0,0,0,80,81,3,12,6,0,81,82,5,30,0,
        0,82,85,1,0,0,0,83,85,3,6,3,0,84,53,1,0,0,0,84,60,1,0,0,0,84,65,
        1,0,0,0,84,74,1,0,0,0,84,80,1,0,0,0,84,83,1,0,0,0,85,9,1,0,0,0,86,
        91,3,12,6,0,87,88,5,29,0,0,88,90,3,12,6,0,89,87,1,0,0,0,90,93,1,
        0,0,0,91,89,1,0,0,0,91,92,1,0,0,0,92,11,1,0,0,0,93,91,1,0,0,0,94,
        95,6,6,-1,0,95,96,5,34,0,0,96,97,5,18,0,0,97,102,3,12,6,9,98,99,
        7,0,0,0,99,102,3,12,6,2,100,102,3,14,7,0,101,94,1,0,0,0,101,98,1,
        0,0,0,101,100,1,0,0,0,102,123,1,0,0,0,103,104,10,8,0,0,104,105,5,
        11,0,0,105,122,3,12,6,9,106,107,10,7,0,0,107,108,5,10,0,0,108,122,
        3,12,6,8,109,110,10,6,0,0,110,111,7,1,0,0,111,122,3,12,6,7,112,113,
        10,5,0,0,113,114,7,2,0,0,114,122,3,12,6,6,115,116,10,4,0,0,116,117,
        7,3,0,0,117,122,3,12,6,5,118,119,10,3,0,0,119,120,7,4,0,0,120,122,
        3,12,6,4,121,103,1,0,0,0,121,106,1,0,0,0,121,109,1,0,0,0,121,112,
        1,0,0,0,121,115,1,0,0,0,121,118,1,0,0,0,122,125,1,0,0,0,123,121,
        1,0,0,0,123,124,1,0,0,0,124,13,1,0,0,0,125,123,1,0,0,0,126,134,3,
        16,8,0,127,129,5,25,0,0,128,130,3,10,5,0,129,128,1,0,0,0,129,130,
        1,0,0,0,130,131,1,0,0,0,131,133,5,26,0,0,132,127,1,0,0,0,133,136,
        1,0,0,0,134,132,1,0,0,0,134,135,1,0,0,0,135,15,1,0,0,0,136,134,1,
        0,0,0,137,149,5,32,0,0,138,149,5,31,0,0,139,149,5,33,0,0,140,149,
        5,7,0,0,141,149,5,8,0,0,142,149,5,9,0,0,143,149,5,34,0,0,144,145,
        5,25,0,0,145,146,3,12,6,0,146,147,5,26,0,0,147,149,1,0,0,0,148,137,
        1,0,0,0,148,138,1,0,0,0,148,139,1,0,0,0,148,140,1,0,0,0,148,141,
        1,0,0,0,148,142,1,0,0,0,148,143,1,0,0,0,148,144,1,0,0,0,149,17,1,
        0,0,0,16,20,22,31,41,48,57,62,72,84,91,101,121,123,129,134,148
    ]

class TinyLangParser ( Parser ):

    grammarFileName = "TinyLang.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'let'", "'return'", "'if'", "'else'", 
                     "'while'", "'func'", "'true'", "'false'", "'null'", 
                     "'&&'", "'||'", "'=='", "'!='", "'<='", "'>='", "'<'", 
                     "'>'", "'='", "'+'", "'-'", "'*'", "'/'", "'%'", "'!'", 
                     "'('", "')'", "'{'", "'}'", "','", "';'" ]

    symbolicNames = [ "<INVALID>", "LET", "RETURN", "IF", "ELSE", "WHILE", 
                      "FUNC", "TRUE", "FALSE", "NULL", "AND", "OR", "EQUAL", 
                      "BANGEQ", "LE", "GE", "LT", "GT", "ASSIGN", "PLUS", 
                      "MINUS", "STAR", "SLASH", "PERCENT", "NOT", "LPAREN", 
                      "RPAREN", "LBRACE", "RBRACE", "COMMA", "SEMI", "FLOAT", 
                      "INT", "STRING", "ID", "WS", "LINE_COMMENT", "BLOCK_COMMENT" ]

    RULE_program = 0
    RULE_functionDecl = 1
    RULE_paramList = 2
    RULE_block = 3
    RULE_statement = 4
    RULE_argList = 5
    RULE_expr = 6
    RULE_postfix = 7
    RULE_primary = 8

    ruleNames =  [ "program", "functionDecl", "paramList", "block", "statement", 
                   "argList", "expr", "postfix", "primary" ]

    EOF = Token.EOF
    LET=1
    RETURN=2
    IF=3
    ELSE=4
    WHILE=5
    FUNC=6
    TRUE=7
    FALSE=8
    NULL=9
    AND=10
    OR=11
    EQUAL=12
    BANGEQ=13
    LE=14
    GE=15
    LT=16
    GT=17
    ASSIGN=18
    PLUS=19
    MINUS=20
    STAR=21
    SLASH=22
    PERCENT=23
    NOT=24
    LPAREN=25
    RPAREN=26
    LBRACE=27
    RBRACE=28
    COMMA=29
    SEMI=30
    FLOAT=31
    INT=32
    STRING=33
    ID=34
    WS=35
    LINE_COMMENT=36
    BLOCK_COMMENT=37

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.2")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class ProgramContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EOF(self):
            return self.getToken(TinyLangParser.EOF, 0)

        def functionDecl(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(TinyLangParser.FunctionDeclContext)
            else:
                return self.getTypedRuleContext(TinyLangParser.FunctionDeclContext,i)


        def statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(TinyLangParser.StatementContext)
            else:
                return self.getTypedRuleContext(TinyLangParser.StatementContext,i)


        def getRuleIndex(self):
            return TinyLangParser.RULE_program

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitProgram" ):
                return visitor.visitProgram(self)
            else:
                return visitor.visitChildren(self)




    def program(self):

        localctx = TinyLangParser.ProgramContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_program)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 22
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 32397853678) != 0):
                self.state = 20
                self._errHandler.sync(self)
                token = self._input.LA(1)
                if token in [6]:
                    self.state = 18
                    self.functionDecl()
                    pass
                elif token in [1, 2, 3, 5, 7, 8, 9, 20, 24, 25, 27, 31, 32, 33, 34]:
                    self.state = 19
                    self.statement()
                    pass
                else:
                    raise NoViableAltException(self)

                self.state = 24
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 25
            self.match(TinyLangParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class FunctionDeclContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def FUNC(self):
            return self.getToken(TinyLangParser.FUNC, 0)

        def ID(self):
            return self.getToken(TinyLangParser.ID, 0)

        def LPAREN(self):
            return self.getToken(TinyLangParser.LPAREN, 0)

        def RPAREN(self):
            return self.getToken(TinyLangParser.RPAREN, 0)

        def block(self):
            return self.getTypedRuleContext(TinyLangParser.BlockContext,0)


        def paramList(self):
            return self.getTypedRuleContext(TinyLangParser.ParamListContext,0)


        def getRuleIndex(self):
            return TinyLangParser.RULE_functionDecl

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitFunctionDecl" ):
                return visitor.visitFunctionDecl(self)
            else:
                return visitor.visitChildren(self)




    def functionDecl(self):

        localctx = TinyLangParser.FunctionDeclContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_functionDecl)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 27
            self.match(TinyLangParser.FUNC)
            self.state = 28
            self.match(TinyLangParser.ID)
            self.state = 29
            self.match(TinyLangParser.LPAREN)
            self.state = 31
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==34:
                self.state = 30
                self.paramList()


            self.state = 33
            self.match(TinyLangParser.RPAREN)
            self.state = 34
            self.block()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ParamListContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ID(self, i:int=None):
            if i is None:
                return self.getTokens(TinyLangParser.ID)
            else:
                return self.getToken(TinyLangParser.ID, i)

        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(TinyLangParser.COMMA)
            else:
                return self.getToken(TinyLangParser.COMMA, i)

        def getRuleIndex(self):
            return TinyLangParser.RULE_paramList

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitParamList" ):
                return visitor.visitParamList(self)
            else:
                return visitor.visitChildren(self)




    def paramList(self):

        localctx = TinyLangParser.ParamListContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_paramList)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 36
            self.match(TinyLangParser.ID)
            self.state = 41
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==29:
                self.state = 37
                self.match(TinyLangParser.COMMA)
                self.state = 38
                self.match(TinyLangParser.ID)
                self.state = 43
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class BlockContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LBRACE(self):
            return self.getToken(TinyLangParser.LBRACE, 0)

        def RBRACE(self):
            return self.getToken(TinyLangParser.RBRACE, 0)

        def statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(TinyLangParser.StatementContext)
            else:
                return self.getTypedRuleContext(TinyLangParser.StatementContext,i)


        def getRuleIndex(self):
            return TinyLangParser.RULE_block

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitBlock" ):
                return visitor.visitBlock(self)
            else:
                return visitor.visitChildren(self)




    def block(self):

        localctx = TinyLangParser.BlockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_block)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 44
            self.match(TinyLangParser.LBRACE)
            self.state = 48
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 32397853614) != 0):
                self.state = 45
                self.statement()
                self.state = 50
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 51
            self.match(TinyLangParser.RBRACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class StatementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LET(self):
            return self.getToken(TinyLangParser.LET, 0)

        def ID(self):
            return self.getToken(TinyLangParser.ID, 0)

        def SEMI(self):
            return self.getToken(TinyLangParser.SEMI, 0)

        def ASSIGN(self):
            return self.getToken(TinyLangParser.ASSIGN, 0)

        def expr(self):
            return self.getTypedRuleContext(TinyLangParser.ExprContext,0)


        def RETURN(self):
            return self.getToken(TinyLangParser.RETURN, 0)

        def IF(self):
            return self.getToken(TinyLangParser.IF, 0)

        def LPAREN(self):
            return self.getToken(TinyLangParser.LPAREN, 0)

        def RPAREN(self):
            return self.getToken(TinyLangParser.RPAREN, 0)

        def block(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(TinyLangParser.BlockContext)
            else:
                return self.getTypedRuleContext(TinyLangParser.BlockContext,i)


        def ELSE(self):
            return self.getToken(TinyLangParser.ELSE, 0)

        def WHILE(self):
            return self.getToken(TinyLangParser.WHILE, 0)

        def getRuleIndex(self):
            return TinyLangParser.RULE_statement

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitStatement" ):
                return visitor.visitStatement(self)
            else:
                return visitor.visitChildren(self)




    def statement(self):

        localctx = TinyLangParser.StatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_statement)
        self._la = 0 # Token type
        try:
            self.state = 84
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [1]:
                self.enterOuterAlt(localctx, 1)
                self.state = 53
                self.match(TinyLangParser.LET)
                self.state = 54
                self.match(TinyLangParser.ID)
                self.state = 57
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==18:
                    self.state = 55
                    self.match(TinyLangParser.ASSIGN)
                    self.state = 56
                    self.expr(0)


                self.state = 59
                self.match(TinyLangParser.SEMI)
                pass
            elif token in [2]:
                self.enterOuterAlt(localctx, 2)
                self.state = 60
                self.match(TinyLangParser.RETURN)
                self.state = 62
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if (((_la) & ~0x3f) == 0 and ((1 << _la) & 32263635840) != 0):
                    self.state = 61
                    self.expr(0)


                self.state = 64
                self.match(TinyLangParser.SEMI)
                pass
            elif token in [3]:
                self.enterOuterAlt(localctx, 3)
                self.state = 65
                self.match(TinyLangParser.IF)
                self.state = 66
                self.match(TinyLangParser.LPAREN)
                self.state = 67
                self.expr(0)
                self.state = 68
                self.match(TinyLangParser.RPAREN)
                self.state = 69
                self.block()
                self.state = 72
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==4:
                    self.state = 70
                    self.match(TinyLangParser.ELSE)
                    self.state = 71
                    self.block()


                pass
            elif token in [5]:
                self.enterOuterAlt(localctx, 4)
                self.state = 74
                self.match(TinyLangParser.WHILE)
                self.state = 75
                self.match(TinyLangParser.LPAREN)
                self.state = 76
                self.expr(0)
                self.state = 77
                self.match(TinyLangParser.RPAREN)
                self.state = 78
                self.block()
                pass
            elif token in [7, 8, 9, 20, 24, 25, 31, 32, 33, 34]:
                self.enterOuterAlt(localctx, 5)
                self.state = 80
                self.expr(0)
                self.state = 81
                self.match(TinyLangParser.SEMI)
                pass
            elif token in [27]:
                self.enterOuterAlt(localctx, 6)
                self.state = 83
                self.block()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ArgListContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def expr(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(TinyLangParser.ExprContext)
            else:
                return self.getTypedRuleContext(TinyLangParser.ExprContext,i)


        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(TinyLangParser.COMMA)
            else:
                return self.getToken(TinyLangParser.COMMA, i)

        def getRuleIndex(self):
            return TinyLangParser.RULE_argList

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitArgList" ):
                return visitor.visitArgList(self)
            else:
                return visitor.visitChildren(self)




    def argList(self):

        localctx = TinyLangParser.ArgListContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_argList)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 86
            self.expr(0)
            self.state = 91
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==29:
                self.state = 87
                self.match(TinyLangParser.COMMA)
                self.state = 88
                self.expr(0)
                self.state = 93
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ExprContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return TinyLangParser.RULE_expr

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)


    class UnaryExprContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a TinyLangParser.ExprContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expr(self):
            return self.getTypedRuleContext(TinyLangParser.ExprContext,0)

        def NOT(self):
            return self.getToken(TinyLangParser.NOT, 0)
        def MINUS(self):
            return self.getToken(TinyLangParser.MINUS, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitUnaryExpr" ):
                return visitor.visitUnaryExpr(self)
            else:
                return visitor.visitChildren(self)


    class AddExprContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a TinyLangParser.ExprContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expr(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(TinyLangParser.ExprContext)
            else:
                return self.getTypedRuleContext(TinyLangParser.ExprContext,i)

        def PLUS(self):
            return self.getToken(TinyLangParser.PLUS, 0)
        def MINUS(self):
            return self.getToken(TinyLangParser.MINUS, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAddExpr" ):
                return visitor.visitAddExpr(self)
            else:
                return visitor.visitChildren(self)


    class MulExprContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a TinyLangParser.ExprContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expr(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(TinyLangParser.ExprContext)
            else:
                return self.getTypedRuleContext(TinyLangParser.ExprContext,i)

        def STAR(self):
            return self.getToken(TinyLangParser.STAR, 0)
        def SLASH(self):
            return self.getToken(TinyLangParser.SLASH, 0)
        def PERCENT(self):
            return self.getToken(TinyLangParser.PERCENT, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitMulExpr" ):
                return visitor.visitMulExpr(self)
            else:
                return visitor.visitChildren(self)


    class OrExprContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a TinyLangParser.ExprContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expr(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(TinyLangParser.ExprContext)
            else:
                return self.getTypedRuleContext(TinyLangParser.ExprContext,i)

        def OR(self):
            return self.getToken(TinyLangParser.OR, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitOrExpr" ):
                return visitor.visitOrExpr(self)
            else:
                return visitor.visitChildren(self)


    class PostfixExprContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a TinyLangParser.ExprContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def postfix(self):
            return self.getTypedRuleContext(TinyLangParser.PostfixContext,0)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitPostfixExpr" ):
                return visitor.visitPostfixExpr(self)
            else:
                return visitor.visitChildren(self)


    class AssignExprContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a TinyLangParser.ExprContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def ID(self):
            return self.getToken(TinyLangParser.ID, 0)
        def ASSIGN(self):
            return self.getToken(TinyLangParser.ASSIGN, 0)
        def expr(self):
            return self.getTypedRuleContext(TinyLangParser.ExprContext,0)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAssignExpr" ):
                return visitor.visitAssignExpr(self)
            else:
                return visitor.visitChildren(self)


    class EqualityExprContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a TinyLangParser.ExprContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expr(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(TinyLangParser.ExprContext)
            else:
                return self.getTypedRuleContext(TinyLangParser.ExprContext,i)

        def EQUAL(self):
            return self.getToken(TinyLangParser.EQUAL, 0)
        def BANGEQ(self):
            return self.getToken(TinyLangParser.BANGEQ, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitEqualityExpr" ):
                return visitor.visitEqualityExpr(self)
            else:
                return visitor.visitChildren(self)


    class RelationExprContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a TinyLangParser.ExprContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expr(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(TinyLangParser.ExprContext)
            else:
                return self.getTypedRuleContext(TinyLangParser.ExprContext,i)

        def LT(self):
            return self.getToken(TinyLangParser.LT, 0)
        def LE(self):
            return self.getToken(TinyLangParser.LE, 0)
        def GT(self):
            return self.getToken(TinyLangParser.GT, 0)
        def GE(self):
            return self.getToken(TinyLangParser.GE, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitRelationExpr" ):
                return visitor.visitRelationExpr(self)
            else:
                return visitor.visitChildren(self)


    class AndExprContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a TinyLangParser.ExprContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expr(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(TinyLangParser.ExprContext)
            else:
                return self.getTypedRuleContext(TinyLangParser.ExprContext,i)

        def AND(self):
            return self.getToken(TinyLangParser.AND, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAndExpr" ):
                return visitor.visitAndExpr(self)
            else:
                return visitor.visitChildren(self)



    def expr(self, _p:int=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = TinyLangParser.ExprContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 12
        self.enterRecursionRule(localctx, 12, self.RULE_expr, _p)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 101
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,10,self._ctx)
            if la_ == 1:
                localctx = TinyLangParser.AssignExprContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx

                self.state = 95
                self.match(TinyLangParser.ID)
                self.state = 96
                self.match(TinyLangParser.ASSIGN)
                self.state = 97
                self.expr(9)
                pass

            elif la_ == 2:
                localctx = TinyLangParser.UnaryExprContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 98
                _la = self._input.LA(1)
                if not(_la==20 or _la==24):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 99
                self.expr(2)
                pass

            elif la_ == 3:
                localctx = TinyLangParser.PostfixExprContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 100
                self.postfix()
                pass


            self._ctx.stop = self._input.LT(-1)
            self.state = 123
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,12,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    self.state = 121
                    self._errHandler.sync(self)
                    la_ = self._interp.adaptivePredict(self._input,11,self._ctx)
                    if la_ == 1:
                        localctx = TinyLangParser.OrExprContext(self, TinyLangParser.ExprContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expr)
                        self.state = 103
                        if not self.precpred(self._ctx, 8):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 8)")
                        self.state = 104
                        self.match(TinyLangParser.OR)
                        self.state = 105
                        self.expr(9)
                        pass

                    elif la_ == 2:
                        localctx = TinyLangParser.AndExprContext(self, TinyLangParser.ExprContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expr)
                        self.state = 106
                        if not self.precpred(self._ctx, 7):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 7)")
                        self.state = 107
                        self.match(TinyLangParser.AND)
                        self.state = 108
                        self.expr(8)
                        pass

                    elif la_ == 3:
                        localctx = TinyLangParser.EqualityExprContext(self, TinyLangParser.ExprContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expr)
                        self.state = 109
                        if not self.precpred(self._ctx, 6):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 6)")
                        self.state = 110
                        _la = self._input.LA(1)
                        if not(_la==12 or _la==13):
                            self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()
                        self.state = 111
                        self.expr(7)
                        pass

                    elif la_ == 4:
                        localctx = TinyLangParser.RelationExprContext(self, TinyLangParser.ExprContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expr)
                        self.state = 112
                        if not self.precpred(self._ctx, 5):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 5)")
                        self.state = 113
                        _la = self._input.LA(1)
                        if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 245760) != 0)):
                            self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()
                        self.state = 114
                        self.expr(6)
                        pass

                    elif la_ == 5:
                        localctx = TinyLangParser.AddExprContext(self, TinyLangParser.ExprContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expr)
                        self.state = 115
                        if not self.precpred(self._ctx, 4):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 4)")
                        self.state = 116
                        _la = self._input.LA(1)
                        if not(_la==19 or _la==20):
                            self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()
                        self.state = 117
                        self.expr(5)
                        pass

                    elif la_ == 6:
                        localctx = TinyLangParser.MulExprContext(self, TinyLangParser.ExprContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expr)
                        self.state = 118
                        if not self.precpred(self._ctx, 3):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 3)")
                        self.state = 119
                        _la = self._input.LA(1)
                        if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 14680064) != 0)):
                            self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()
                        self.state = 120
                        self.expr(4)
                        pass

             
                self.state = 125
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,12,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.unrollRecursionContexts(_parentctx)
        return localctx


    class PostfixContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def primary(self):
            return self.getTypedRuleContext(TinyLangParser.PrimaryContext,0)


        def LPAREN(self, i:int=None):
            if i is None:
                return self.getTokens(TinyLangParser.LPAREN)
            else:
                return self.getToken(TinyLangParser.LPAREN, i)

        def RPAREN(self, i:int=None):
            if i is None:
                return self.getTokens(TinyLangParser.RPAREN)
            else:
                return self.getToken(TinyLangParser.RPAREN, i)

        def argList(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(TinyLangParser.ArgListContext)
            else:
                return self.getTypedRuleContext(TinyLangParser.ArgListContext,i)


        def getRuleIndex(self):
            return TinyLangParser.RULE_postfix

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitPostfix" ):
                return visitor.visitPostfix(self)
            else:
                return visitor.visitChildren(self)




    def postfix(self):

        localctx = TinyLangParser.PostfixContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_postfix)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 126
            self.primary()
            self.state = 134
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,14,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 127
                    self.match(TinyLangParser.LPAREN)
                    self.state = 129
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if (((_la) & ~0x3f) == 0 and ((1 << _la) & 32263635840) != 0):
                        self.state = 128
                        self.argList()


                    self.state = 131
                    self.match(TinyLangParser.RPAREN) 
                self.state = 136
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,14,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class PrimaryContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def INT(self):
            return self.getToken(TinyLangParser.INT, 0)

        def FLOAT(self):
            return self.getToken(TinyLangParser.FLOAT, 0)

        def STRING(self):
            return self.getToken(TinyLangParser.STRING, 0)

        def TRUE(self):
            return self.getToken(TinyLangParser.TRUE, 0)

        def FALSE(self):
            return self.getToken(TinyLangParser.FALSE, 0)

        def NULL(self):
            return self.getToken(TinyLangParser.NULL, 0)

        def ID(self):
            return self.getToken(TinyLangParser.ID, 0)

        def LPAREN(self):
            return self.getToken(TinyLangParser.LPAREN, 0)

        def expr(self):
            return self.getTypedRuleContext(TinyLangParser.ExprContext,0)


        def RPAREN(self):
            return self.getToken(TinyLangParser.RPAREN, 0)

        def getRuleIndex(self):
            return TinyLangParser.RULE_primary

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitPrimary" ):
                return visitor.visitPrimary(self)
            else:
                return visitor.visitChildren(self)




    def primary(self):

        localctx = TinyLangParser.PrimaryContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_primary)
        try:
            self.state = 148
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [32]:
                self.enterOuterAlt(localctx, 1)
                self.state = 137
                self.match(TinyLangParser.INT)
                pass
            elif token in [31]:
                self.enterOuterAlt(localctx, 2)
                self.state = 138
                self.match(TinyLangParser.FLOAT)
                pass
            elif token in [33]:
                self.enterOuterAlt(localctx, 3)
                self.state = 139
                self.match(TinyLangParser.STRING)
                pass
            elif token in [7]:
                self.enterOuterAlt(localctx, 4)
                self.state = 140
                self.match(TinyLangParser.TRUE)
                pass
            elif token in [8]:
                self.enterOuterAlt(localctx, 5)
                self.state = 141
                self.match(TinyLangParser.FALSE)
                pass
            elif token in [9]:
                self.enterOuterAlt(localctx, 6)
                self.state = 142
                self.match(TinyLangParser.NULL)
                pass
            elif token in [34]:
                self.enterOuterAlt(localctx, 7)
                self.state = 143
                self.match(TinyLangParser.ID)
                pass
            elif token in [25]:
                self.enterOuterAlt(localctx, 8)
                self.state = 144
                self.match(TinyLangParser.LPAREN)
                self.state = 145
                self.expr(0)
                self.state = 146
                self.match(TinyLangParser.RPAREN)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx



    def sempred(self, localctx:RuleContext, ruleIndex:int, predIndex:int):
        if self._predicates == None:
            self._predicates = dict()
        self._predicates[6] = self.expr_sempred
        pred = self._predicates.get(ruleIndex, None)
        if pred is None:
            raise Exception("No predicate with index:" + str(ruleIndex))
        else:
            return pred(localctx, predIndex)

    def expr_sempred(self, localctx:ExprContext, predIndex:int):
            if predIndex == 0:
                return self.precpred(self._ctx, 8)
         

            if predIndex == 1:
                return self.precpred(self._ctx, 7)
         

            if predIndex == 2:
                return self.precpred(self._ctx, 6)
         

            if predIndex == 3:
                return self.precpred(self._ctx, 5)
         

            if predIndex == 4:
                return self.precpred(self._ctx, 4)
         

            if predIndex == 5:
                return self.precpred(self._ctx, 3)
         




