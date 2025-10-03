grammar Calculator;

expression
    : NUMBER                    # Number
    | '(' expression ')'        # Parentheses
    | expression TIME5 expression  # Multiplication
    | expression DIV expression    # Division
    | expression PLUS expression   # Addition
    | expression MINUS expression  # Subtraction
    ;

PLUS: '+';
MINUS: '-';
TIME5: '*';
DIV: '/';
NUMBER: [0-9]+;
WS: [ \r\n\t]+ -> skip;