# ANTLR4 Шпаргалка для Python

## 📋 Содержание
1. [Установка и настройка](#установка-и-настройка)
2. [Создание грамматики](#создание-грамматики)
3. [Генерация кода Python](#генерация-кода-python)
4. [Базовое использование](#базовое-использование)
5. [Работа с лексером](#работа-с-лексером)
6. [Работа с парсером](#работа-с-парсером)
7. [Работа с токенами](#работа-с-токенами)
8. [Работа с деревом разбора](#работа-с-деревом-разбора)
9. [Listener паттерн](#listener-паттерн)
10. [Visitor паттерн](#visitor-паттерн)
11. [Обработка ошибок](#обработка-ошибок)
12. [Полезные примеры](#полезные-примеры)

---

## Установка и настройка

### Установка ANTLR4
```bash
# Установка Java (требуется для ANTLR4)
# Скачать с https://www.java.com/

# Установка ANTLR4 через pip
pip install antlr4-python3-runtime

# Скачать ANTLR4 JAR файл
# https://www.antlr.org/download/antlr-4.13.1-complete.jar
# Или через wget:
wget https://www.antlr.org/download/antlr-4.13.1-complete.jar
```

### Настройка переменных окружения (Windows)
```powershell
# Добавить в PATH путь к Java
# Добавить переменную CLASSPATH с путем к antlr-4.13.1-complete.jar
$env:CLASSPATH = "C:\path\to\antlr-4.13.1-complete.jar;$env:CLASSPATH"
```

### Алиас для удобства (опционально)
```bash
# Создать alias для запуска ANTLR4
alias antlr4='java -Xmx500M -cp "/usr/local/lib/antlr-4.13.1-complete.jar:$CLASSPATH" org.antlr.v4.Tool'
```

---

## Создание грамматики

### Структура файла грамматики (.g4)

```antlr
grammar MyGrammar;

// Опции
options {
    language = Python3;
}

// Правила парсера (начинаются с маленькой буквы)
startRule: expression EOF;

expression: NUMBER | IDENTIFIER | expression '+' expression;

// Правила лексера (начинаются с большой буквы)
NUMBER: [0-9]+;
IDENTIFIER: [a-zA-Z_][a-zA-Z0-9_]*;
WS: [ \t\r\n]+ -> skip;  // Пропускать пробелы
```

### Основные элементы грамматики

#### Лексер (Lexer rules)
```antlr
// Простые токены
PLUS: '+';
MINUS: '-';
MULT: '*';
DIV: '/';

// Регулярные выражения
NUMBER: [0-9]+ ('.' [0-9]+)?;  // Числа с точкой
STRING: '"' .*? '"';            // Строки в кавычках
IDENTIFIER: [a-zA-Z_][a-zA-Z0-9_]*;

// Фрагменты (не создают токены, используются в других правилах)
fragment DIGIT: [0-9];
fragment LETTER: [a-zA-Z];

// Пропуск токенов
WS: [ \t\r\n]+ -> skip;         // Пропускать пробелы
COMMENT: '//' .*? '\n' -> skip; // Пропускать комментарии

// Каналы (для скрытых токенов)
LINE_COMMENT: '//' .*? '\n' -> channel(HIDDEN);
```

#### Парсер (Parser rules)
```antlr
// Простые правила
statement: assignment | expression;

// Альтернативы (|)
expression: NUMBER | IDENTIFIER | '(' expression ')';

// Последовательности
assignment: IDENTIFIER '=' expression ';';

// Опциональные элементы (?)
optional: IDENTIFIER ('=' expression)?;

// Повторения
// * - ноль или более
// + - один или более
list: item (',' item)*;

// Группировка
group: (a | b) c;

// Приоритет операций
expression: expression ('*' | '/') expression  // Высокий приоритет
          | expression ('+' | '-') expression  // Низкий приоритет
          | NUMBER
          | IDENTIFIER;
```

---

## Генерация кода Python

### Генерация из файла грамматики
```bash
# Генерация для Python3
java -Xmx500M -cp "antlr-4.13.1-complete.jar:$CLASSPATH" \
     org.antlr.v4.Tool -Dlanguage=Python3 MyGrammar.g4

# Или если установлен alias
antlr4 -Dlanguage=Python3 MyGrammar.g4
```

### Сгенерированные файлы
После генерации создаются следующие файлы:
- `MyGrammarLexer.py` - класс лексера
- `MyGrammarParser.py` - класс парсера
- `MyGrammarListener.py` - базовый класс listener
- `MyGrammarVisitor.py` - базовый класс visitor (если включен)
- `MyGrammar.tokens` - список токенов
- `MyGrammar.interp` - интерпретационные данные

### Опции генерации
```bash
# Генерация с visitor
antlr4 -Dlanguage=Python3 -visitor MyGrammar.g4

# Генерация без listener
antlr4 -Dlanguage=Python3 -no-listener MyGrammar.g4

# Указание выходной директории
antlr4 -Dlanguage=Python3 -o output_dir MyGrammar.g4
```

---

## Базовое использование

### Импорты
```python
from antlr4 import *
from antlr4.InputStream import InputStream
from antlr4.FileStream import FileStream
from antlr4.CommonTokenStream import CommonTokenStream
from antlr4.error.ErrorListener import ErrorListener

# Импорт сгенерированных классов
from MyGrammarLexer import MyGrammarLexer
from MyGrammarParser import MyGrammarParser
```

### Базовый пример: чтение из строки
```python
from antlr4 import *
from MyGrammarLexer import MyGrammarLexer
from MyGrammarParser import MyGrammarParser

# Создание входного потока из строки
input_stream = InputStream("2 + 3 * 4")

# Создание лексера
lexer = MyGrammarLexer(input_stream)

# Создание потока токенов
token_stream = CommonTokenStream(lexer)

# Создание парсера
parser = MyGrammarParser(token_stream)

# Парсинг (вызов стартового правила)
tree = parser.startRule()

# Вывод дерева в виде строки
print(tree.toStringTree(recog=parser))
```

### Базовый пример: чтение из файла
```python
from antlr4 import *
from antlr4.FileStream import FileStream
from MyGrammarLexer import MyGrammarLexer
from MyGrammarParser import MyGrammarParser

# Чтение из файла
input_stream = FileStream("input.txt", encoding="utf-8")

lexer = MyGrammarLexer(input_stream)
token_stream = CommonTokenStream(lexer)
parser = MyGrammarParser(token_stream)
tree = parser.startRule()

print(tree.toStringTree(recog=parser))
```

---

## Работа с лексером

### Базовое использование лексера
```python
from antlr4 import *
from MyGrammarLexer import MyGrammarLexer

# Создание входного потока
input_stream = InputStream("x = 42")

# Создание лексера
lexer = MyGrammarLexer(input_stream)

# Получение всех токенов
token = lexer.nextToken()
while token.type != Token.EOF:
    print(f"Токен: {token.text}, Тип: {token.type}")
    token = lexer.nextToken()
```

### Получение информации о токенах
```python
token = lexer.nextToken()

# Основные свойства токена
token.text        # Текст токена (строка)
token.type        # Тип токена (число)
token.line        # Номер строки (начинается с 1)
token.column      # Номер колонки (начинается с 0)
token.start       # Начальный индекс в потоке
token.stop        # Конечный индекс в потоке
token.startIndex  # Альтернативное название для start
token.stopIndex   # Альтернативное название для stop

# Получение имени типа токена
token_type_name = lexer.symbolicNames[token.type]
# или
token_type_name = lexer.symbolicNames[token.type] if token.type < len(lexer.symbolicNames) else None
```

### Работа с символическими именами
```python
# Получение всех символических имен
symbolic_names = lexer.symbolicNames

# Поиск типа токена по имени
def get_token_type(lexer, name):
    try:
        return lexer.symbolicNames.index(name)
    except ValueError:
        return -1

# Пример использования
if token.type == get_token_type(lexer, 'IDENTIFIER'):
    print("Это идентификатор!")
```

### Пример: Подсветка синтаксиса
```python
from antlr4 import *
from MyGrammarLexer import MyGrammarLexer

def apply_syntax_highlighting(text_widget, text):
    # Создание входного потока
    input_stream = InputStream(text)
    lexer = MyGrammarLexer(input_stream)
    
    # Цвета для разных типов токенов
    colors = {
        'KEYWORD': 'blue',
        'STRING': 'green',
        'NUMBER': 'purple',
        'COMMENT': 'gray',
        'IDENTIFIER': 'black',
    }
    
    # Настройка тегов в виджете
    for token_name, color in colors.items():
        text_widget.tag_configure(token_name, foreground=color)
    
    # Обработка токенов
    token = lexer.nextToken()
    while token.type != Token.EOF:
        token_type = lexer.symbolicNames[token.type]
        
        if token_type in colors:
            start_line = token.line
            start_col = token.column
            end_col = start_col + len(token.text)
            
            start_tag = f"{start_line}.{start_col}"
            end_tag = f"{start_line}.{end_col}"
            
            text_widget.tag_add(token_type, start_tag, end_tag)
        
        token = lexer.nextToken()
```

---

## Работа с парсером

### Базовое использование парсера
```python
from antlr4 import *
from MyGrammarLexer import MyGrammarLexer
from MyGrammarParser import MyGrammarParser

input_stream = InputStream("2 + 3")
lexer = MyGrammarLexer(input_stream)
token_stream = CommonTokenStream(lexer)
parser = MyGrammarParser(token_stream)

# Вызов правила парсера (зависит от вашей грамматики)
tree = parser.expression()

# Получение корневого узла
root = tree

# Проверка на ошибки
if parser.getNumberOfSyntaxErrors() > 0:
    print("Ошибки парсинга!")
```

### Получение информации о дереве
```python
# Получение текста узла
node_text = tree.getText()

# Получение количества дочерних узлов
child_count = tree.getChildCount()

# Получение дочернего узла по индексу
child = tree.getChild(0)

# Получение родительского узла
parent = tree.getParent()

# Получение типа узла (имя правила)
rule_name = parser.ruleNames[tree.getRuleIndex()]

# Вывод дерева в виде строки
tree_string = tree.toStringTree(recog=parser)
print(tree_string)
```

### Рекурсивный обход дерева
```python
def visit_tree(node, parser, level=0):
    """Рекурсивный обход дерева разбора"""
    if node is None:
        return
    
    indent = "  " * level
    node_text = node.getText()
    
    # Если это терминальный узел (лист)
    if node.getChildCount() == 0:
        print(f"{indent}Терминал: {node_text}")
    else:
        # Это нетерминальный узел
        rule_index = node.getRuleIndex()
        if rule_index >= 0:
            rule_name = parser.ruleNames[rule_index]
            print(f"{indent}Правило: {rule_name}")
        else:
            print(f"{indent}Узел: {node_text}")
    
    # Рекурсивный обход дочерних узлов
    for i in range(node.getChildCount()):
        visit_tree(node.getChild(i), parser, level + 1)

# Использование
visit_tree(tree, parser)
```

---

## Работа с токенами

### Получение всех токенов
```python
# Получение всех токенов из потока
token_stream.fill()  # Заполнить поток токенами
tokens = token_stream.tokens

# Итерация по токенам
for token in tokens:
    if token.type != Token.EOF:
        print(f"{token.text} -> {lexer.symbolicNames[token.type]}")
```

### Фильтрация токенов
```python
# Получение только определенных типов токенов
def get_tokens_by_type(token_stream, lexer, token_type_name):
    token_stream.fill()
    target_type = lexer.symbolicNames.index(token_type_name)
    
    return [token for token in token_stream.tokens 
            if token.type == target_type and token.type != Token.EOF]

# Пример: получить все идентификаторы
identifiers = get_tokens_by_type(token_stream, lexer, 'IDENTIFIER')
```

### Работа с позициями токенов
```python
token = lexer.nextToken()

# Абсолютные позиции в потоке
start_pos = token.start
end_pos = token.stop

# Позиции в тексте (строка, колонка)
line = token.line
column = token.column

# Длина токена
length = len(token.text)

# Получение подстроки из исходного текста
source_text = input_stream.strdata
token_substring = source_text[start_pos:end_pos + 1]
```

---

## Работа с деревом разбора

### Визуализация дерева (с использованием graphviz)
```python
from graphviz import Digraph
from antlr4 import *

def visualize_tree(node, parser, graph=None, parent_name=None, node_counter=[0]):
    """Визуализация дерева разбора с помощью graphviz"""
    if graph is None:
        graph = Digraph(format='png', graph_attr={'rankdir': 'TB'})
    
    # Создание уникального имени узла
    node_id = f"node_{node_counter[0]}"
    node_counter[0] += 1
    
    # Получение текста узла
    node_text = node.getText()
    if not node_text.strip():
        node_text = "EMPTY"
    
    # Очистка текста для graphviz
    node_text = node_text.replace('"', "'").replace('\n', '\\n')[:50]
    
    # Определение типа узла
    if node.getChildCount() == 0:
        # Терминальный узел
        graph.node(node_id, label=f'"{node_text}"', shape='box', style='filled', fillcolor='lightblue')
    else:
        # Нетерминальный узел
        rule_index = node.getRuleIndex()
        if rule_index >= 0:
            rule_name = parser.ruleNames[rule_index]
            graph.node(node_id, label=f'"{rule_name}"', shape='ellipse', style='filled', fillcolor='lightgreen')
        else:
            graph.node(node_id, label=f'"{node_text}"', shape='ellipse')
    
    # Связь с родителем
    if parent_name:
        graph.edge(parent_name, node_id)
    
    # Рекурсивный обход дочерних узлов
    for i in range(node.getChildCount()):
        visualize_tree(node.getChild(i), parser, graph, node_id, node_counter)
    
    return graph

# Использование
graph = visualize_tree(tree, parser)
graph.render('parse_tree', view=True)
```

### Поиск узлов в дереве
```python
def find_nodes_by_rule(tree, parser, rule_name):
    """Поиск всех узлов с определенным правилом"""
    result = []
    
    def visit(node):
        if node is None:
            return
        
        rule_index = node.getRuleIndex()
        if rule_index >= 0:
            if parser.ruleNames[rule_index] == rule_name:
                result.append(node)
        
        for i in range(node.getChildCount()):
            visit(node.getChild(i))
    
    visit(tree)
    return result

# Пример: найти все выражения
expressions = find_nodes_by_rule(tree, parser, 'expression')
```

### Извлечение данных из дерева
```python
def extract_identifiers(tree, lexer):
    """Извлечение всех идентификаторов из дерева"""
    identifiers = []
    
    def visit(node):
        if node is None:
            return
        
        # Если это терминальный узел
        if node.getChildCount() == 0:
            # Проверяем, является ли это идентификатором
            # (нужно получить токен из узла)
            pass
        
        for i in range(node.getChildCount()):
            visit(node.getChild(i))
    
    visit(tree)
    return identifiers
```

---

## Listener паттерн

### Создание кастомного Listener
```python
from antlr4 import *
from MyGrammarListener import MyGrammarListener
from MyGrammarParser import MyGrammarParser

class MyCustomListener(MyGrammarListener):
    """Кастомный listener для обработки дерева разбора"""
    
    def __init__(self):
        super().__init__()
        self.result = []
    
    # Переопределение методов для каждого правила
    def enterExpression(self, ctx: MyGrammarParser.ExpressionContext):
        """Вызывается при входе в правило expression"""
        print(f"Вход в expression: {ctx.getText()}")
    
    def exitExpression(self, ctx: MyGrammarParser.ExpressionContext):
        """Вызывается при выходе из правила expression"""
        print(f"Выход из expression: {ctx.getText()}")
        self.result.append(ctx.getText())
    
    def enterAssignment(self, ctx: MyGrammarParser.AssignmentContext):
        """Обработка присваивания"""
        var_name = ctx.IDENTIFIER().getText()
        expr_text = ctx.expression().getText()
        print(f"Присваивание: {var_name} = {expr_text}")

# Использование
input_stream = InputStream("x = 2 + 3")
lexer = MyGrammarLexer(input_stream)
token_stream = CommonTokenStream(lexer)
parser = MyGrammarParser(token_stream)
tree = parser.startRule()

# Создание и использование listener
listener = MyCustomListener()
walker = ParseTreeWalker()
walker.walk(listener, tree)

print(f"Результат: {listener.result}")
```

### Доступ к дочерним элементам в Listener
```python
class MyCustomListener(MyGrammarListener):
    def exitExpression(self, ctx: MyGrammarParser.ExpressionContext):
        # Получение всех дочерних элементов
        children = ctx.getChildren()
        
        # Получение конкретных элементов по имени правила
        # (если в грамматике есть именованные альтернативы)
        # Например: expression: left=expression op=('+'|'-') right=expression
        left = ctx.left
        op = ctx.op.getText()
        right = ctx.right
        
        # Получение токенов
        identifiers = ctx.IDENTIFIER()  # Список всех IDENTIFIER токенов
        first_id = ctx.IDENTIFIER(0)    # Первый IDENTIFIER
        
        # Получение текста
        full_text = ctx.getText()
        
        # Получение позиции
        start = ctx.start
        stop = ctx.stop
```

---

## Visitor паттерн

### Создание кастомного Visitor
```python
from antlr4 import *
from MyGrammarVisitor import MyGrammarVisitor
from MyGrammarParser import MyGrammarParser

class MyCustomVisitor(MyGrammarVisitor):
    """Кастомный visitor для обхода дерева разбора"""
    
    def visitExpression(self, ctx: MyGrammarParser.ExpressionContext):
        """Посещение узла expression"""
        # Если есть альтернативы, проверяем какая используется
        if ctx.getChildCount() == 1:
            # Простое выражение (NUMBER или IDENTIFIER)
            return self.visitChildren(ctx)
        else:
            # Бинарная операция
            left = self.visit(ctx.expression(0))
            right = self.visit(ctx.expression(1))
            op = ctx.getChild(1).getText()
            
            if op == '+':
                return left + right
            elif op == '-':
                return left - right
            elif op == '*':
                return left * right
            elif op == '/':
                return left / right
    
    def visitNumber(self, ctx: MyGrammarParser.NumberContext):
        """Посещение числа"""
        return int(ctx.NUMBER().getText())
    
    def visitIdentifier(self, ctx: MyGrammarParser.IdentifierContext):
        """Посещение идентификатора"""
        return ctx.IDENTIFIER().getText()

# Использование
input_stream = InputStream("2 + 3 * 4")
lexer = MyGrammarLexer(input_stream)
token_stream = CommonTokenStream(lexer)
parser = MyGrammarParser(token_stream)
tree = parser.expression()

# Создание и использование visitor
visitor = MyCustomVisitor()
result = visitor.visit(tree)
print(f"Результат вычисления: {result}")
```

### Разница между Listener и Visitor

**Listener:**
- Обход дерева управляется извне (ParseTreeWalker)
- Методы вызываются автоматически при входе/выходе из узлов
- Не может контролировать порядок обхода
- Не может возвращать значения из методов
- Лучше для простой обработки и сбора информации

**Visitor:**
- Обход дерева управляется самим visitor
- Нужно явно вызывать visit() для дочерних узлов
- Может контролировать порядок обхода
- Может возвращать значения из методов
- Лучше для вычислений и трансформаций

---

## Обработка ошибок

### Кастомный Error Listener
```python
from antlr4.error.ErrorListener import ErrorListener

class MyErrorListener(ErrorListener):
    """Кастомный обработчик ошибок"""
    
    def __init__(self):
        super().__init__()
        self.errors = []
    
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        """Обработка синтаксической ошибки"""
        error_info = {
            'line': line,
            'column': column,
            'message': msg,
            'symbol': offendingSymbol.text if offendingSymbol else None
        }
        self.errors.append(error_info)
        
        print(f"Ошибка на строке {line}, колонке {column}: {msg}")
        if offendingSymbol:
            print(f"Проблемный символ: {offendingSymbol.text}")
    
    def reportAmbiguity(self, recognizer, dfa, startIndex, stopIndex, exact, ambigAlts, configs):
        """Обработка неоднозначности"""
        print(f"Неоднозначность: {startIndex}-{stopIndex}")
    
    def reportAttemptingFullContext(self, recognizer, dfa, startIndex, stopIndex, conflictingAlts, configs):
        """Попытка полного контекста"""
        pass
    
    def reportContextSensitivity(self, recognizer, dfa, startIndex, stopIndex, prediction, configs):
        """Чувствительность к контексту"""
        pass

# Использование
input_stream = InputStream("x = 2 +")  # Неполное выражение
lexer = MyGrammarLexer(input_stream)
token_stream = CommonTokenStream(lexer)
parser = MyGrammarParser(token_stream)

# Установка кастомного error listener
error_listener = MyErrorListener()
parser.removeErrorListeners()  # Удалить стандартный listener
parser.addErrorListener(error_listener)

tree = parser.startRule()

# Проверка ошибок
if error_listener.errors:
    print(f"Найдено ошибок: {len(error_listener.errors)}")
    for error in error_listener.errors:
        print(f"  {error}")
```

### Восстановление после ошибок
```python
# ANTLR4 автоматически пытается восстановиться после ошибок
# Можно настроить стратегию восстановления

from antlr4.error.Errors import DefaultErrorStrategy

class MyErrorStrategy(DefaultErrorStrategy):
    """Кастомная стратегия обработки ошибок"""
    
    def recover(self, recognizer, e):
        """Восстановление после ошибки"""
        # Кастомная логика восстановления
        super().recover(recognizer, e)
    
    def recoverInline(self, recognizer):
        """Восстановление в текущей позиции"""
        return super().recoverInline(recognizer)

# Использование
parser._errHandler = MyErrorStrategy()
```

---

## Полезные примеры

### Пример 1: Простой калькулятор
```python
from antlr4 import *
from CalculatorLexer import CalculatorLexer
from CalculatorParser import CalculatorParser
from CalculatorVisitor import CalculatorVisitor

class Calculator(CalculatorVisitor):
    def visitNumber(self, ctx):
        return float(ctx.NUMBER().getText())
    
    def visitAdd(self, ctx):
        return self.visit(ctx.expression(0)) + self.visit(ctx.expression(1))
    
    def visitSubtract(self, ctx):
        return self.visit(ctx.expression(0)) - self.visit(ctx.expression(1))
    
    def visitMultiply(self, ctx):
        return self.visit(ctx.expression(0)) * self.visit(ctx.expression(1))
    
    def visitDivide(self, ctx):
        return self.visit(ctx.expression(0)) / self.visit(ctx.expression(1))

def calculate(expression):
    input_stream = InputStream(expression)
    lexer = CalculatorLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = CalculatorParser(token_stream)
    tree = parser.expression()
    
    calculator = Calculator()
    return calculator.visit(tree)

# Использование
result = calculate("2 + 3 * 4")
print(result)  # 14.0
```

### Пример 2: Подсчет статистики кода
```python
class CodeStatisticsListener(MyGrammarListener):
    def __init__(self):
        self.function_count = 0
        self.variable_count = 0
        self.line_count = 0
    
    def enterFunction(self, ctx):
        self.function_count += 1
    
    def enterVariable(self, ctx):
        self.variable_count += 1
    
    def enterStatement(self, ctx):
        self.line_count += 1

# Использование
listener = CodeStatisticsListener()
walker = ParseTreeWalker()
walker.walk(listener, tree)

print(f"Функций: {listener.function_count}")
print(f"Переменных: {listener.variable_count}")
print(f"Строк кода: {listener.line_count}")
```

### Пример 3: Трансформация кода
```python
class CodeTransformer(MyGrammarVisitor):
    def visitAssignment(self, ctx):
        var = ctx.IDENTIFIER().getText()
        expr = self.visit(ctx.expression())
        # Трансформация: добавляем проверку
        return f"if {var} is not None:\n    {var} = {expr}"
    
    def visitExpression(self, ctx):
        # Рекурсивная трансформация
        return self.visitChildren(ctx)

# Использование
transformer = CodeTransformer()
transformed = transformer.visit(tree)
print(transformed)
```

### Пример 4: Валидация кода
```python
class CodeValidator(MyGrammarListener):
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def exitFunction(self, ctx):
        # Проверка: функция должна иметь return
        has_return = any(
            child.getText() == 'return' 
            for child in ctx.getChildren()
        )
        if not has_return:
            self.warnings.append(f"Функция {ctx.IDENTIFIER().getText()} не имеет return")
    
    def exitAssignment(self, ctx):
        # Проверка: переменная должна быть объявлена
        var_name = ctx.IDENTIFIER().getText()
        # Логика проверки...
```

---

## Частые проблемы и решения

### Проблема: Кодировка файлов
```python
# Решение: явно указывать кодировку
input_stream = FileStream("file.txt", encoding="utf-8")
```

### Проблема: Пробелы и комментарии мешают
```antlr
// В грамматике добавить правила для пропуска
WS: [ \t\r\n]+ -> skip;
COMMENT: '//' .*? '\n' -> skip;
```

### Проблема: Неоднозначность грамматики
```antlr
// Использовать приоритет операций
expression: expression ('*' | '/') expression  // Высокий приоритет
          | expression ('+' | '-') expression  // Низкий приоритет
          | NUMBER;
```

### Проблема: Рекурсия слева
```antlr
// Левая рекурсия (не работает):
// expression: expression '+' NUMBER;

// Правая рекурсия (работает):
expression: NUMBER ('+' expression)?;
```

---

## Полезные ссылки

- [Официальный сайт ANTLR](https://www.antlr.org/)
- [Документация ANTLR4](https://github.com/antlr/antlr4/blob/master/doc/index.md)
- [ANTLR4 Runtime для Python](https://pypi.org/project/antlr4-python3-runtime/)
- [Грамматики ANTLR4](https://github.com/antlr/grammars-v4)

---

## Быстрая справка

### Основные классы
- `InputStream` - входной поток из строки
- `FileStream` - входной поток из файла
- `CommonTokenStream` - поток токенов
- `ParseTreeWalker` - обходчик дерева для listener
- `Token.EOF` - константа конца файла

### Основные методы
- `lexer.nextToken()` - получить следующий токен
- `parser.startRule()` - запустить парсинг с правила startRule
- `tree.getText()` - получить текст узла
- `tree.getChildCount()` - количество дочерних узлов
- `tree.getChild(i)` - получить дочерний узел
- `ctx.getChildren()` - получить все дочерние элементы
- `walker.walk(listener, tree)` - обойти дерево с listener
- `visitor.visit(tree)` - обойти дерево с visitor

---

**Удачной работы с ANTLR4! 🚀**

