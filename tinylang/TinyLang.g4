grammar TinyLang;

// ===== Parser rules =====
program
    : (functionDecl | statement)* EOF
    ;

functionDecl
    : FUNC ID LPAREN paramList? RPAREN block
    ;

paramList
    : ID (COMMA ID)*
    ;

block
    : LBRACE statement* RBRACE
    ;

statement
    : LET ID (ASSIGN expr)? SEMI               // variable declaration
    | RETURN expr? SEMI                        // return
    | IF LPAREN expr RPAREN block (ELSE block)?// if/else
    | WHILE LPAREN expr RPAREN block           // while
    | expr SEMI                                // expression statement
    | block                                    // nested block
    ;

argList
    : expr (COMMA expr)*
    ;

expr
    : <assoc=right> ID ASSIGN expr                    # assignExpr
    | expr OR expr                                    # orExpr
    | expr AND expr                                   # andExpr
    | expr (EQUAL | BANGEQ) expr                      # equalityExpr
    | expr (LT | LE | GT | GE) expr                   # relationExpr
    | expr (PLUS | MINUS) expr                        # addExpr
    | expr (STAR | SLASH | PERCENT) expr              # mulExpr
    | (NOT | MINUS) expr                              # unaryExpr
    | postfix                                         # postfixExpr
    ;

postfix
    : primary (LPAREN argList? RPAREN)*               // call chaining: f()(1)(2)
    ;

primary
    : INT
    | FLOAT
    | STRING
    | TRUE
    | FALSE
    | NULL
    | ID
    | LPAREN expr RPAREN
    ;

// ===== Lexer rules =====
// Keywords
LET: 'let';
RETURN: 'return';
IF: 'if';
ELSE: 'else';
WHILE: 'while';
FUNC: 'func';
TRUE: 'true';
FALSE: 'false';
NULL: 'null';

// Operators (longer first)
AND: '&&';
OR: '||';
EQUAL: '==';
BANGEQ: '!=';
LE: '<=';
GE: '>=';
LT: '<';
GT: '>';
ASSIGN: '=';
PLUS: '+';
MINUS: '-';
STAR: '*';
SLASH: '/';
PERCENT: '%';
NOT: '!';

// Delimiters
LPAREN: '(';
RPAREN: ')';
LBRACE: '{';
RBRACE: '}';
COMMA: ',';
SEMI: ';';

// Literals
FLOAT: DIGIT+ '.' DIGIT+;         // simple float (no exponent in this teaching version)
INT: DIGIT+;

STRING: '"' (ESC | ~["\\\r\n])* '"';
fragment ESC: '\\' [btnfr"\\];

// Identifiers
fragment DIGIT: [0-9];
fragment LETTER: [A-Za-z_];
ID: LETTER (LETTER | DIGIT)*;

// Whitespace and comments
WS: [ \t\r\n]+ -> channel(HIDDEN);
LINE_COMMENT: '//' ~[\r\n]* -> channel(HIDDEN);
BLOCK_COMMENT: '/*' .*? '*/' -> channel(HIDDEN);