# ANTLR4: Listeners и Visitors в Python

## 1. Введение: Зачем нужны Listeners и Visitors?

После этапа парсинга ANTLR4 строит **AST (Abstract Syntax Tree)** — абстрактное синтаксическое дерево, которое представляет структуру разобранного текста согласно правилам грамматики.

Однако само по себе дерево — это лишь структура данных. Чтобы извлечь информацию, выполнить вычисления, трансформировать код или провести анализ, нам нужны механизмы для обхода этого дерева.

**Listeners** и **Visitors** — это два основных паттерна (механизма), которые ANTLR4 предоставляет для обхода синтаксического дерева и обработки информации из него. Без них дерево просто существует, но мы не можем эффективно с ним взаимодействовать.

---

## 2. Механизм Listener (Наблюдатель)

### Концепция

**Listener** реализует паттерн "Наблюдатель" (Observer Pattern), похожий на event-driven подход. Это **пассивный механизм**, где мы "подписываемся" на события вхождения в узел дерева (`enterRuleName`) и выхода из него (`exitRuleName`).

Обход дерева управляется внутренним обходчиком ANTLR (`ParseTreeWalker`). Наш код просто реагирует на его события, не контролируя порядок обхода.

### Как работает

1. ANTLR автоматически генерирует базовый класс `<GrammarName>Listener` (например, `ExprListener`) с пустыми методами `enterEveryRuleName` и `exitEveryRuleName` для каждого правила грамматики.

2. Мы создаем свой собственный класс-наследник (например, `MyListener`) и переопределяем (override) только те методы, которые нас интересуют.

3. Мы создаем экземпляр `ParseTreeWalker` и вызываем его метод `walk`, передавая туда наш слушатель и корень дерева.

4. `ParseTreeWalker` проходит по дереву в порядке depth-first (слева направо) и для каждого узла:
   - Сначала вызывает `enterRuleName`
   - Затем обходит поддерево
   - После обхода поддерева вызывает `exitRuleName`

### Создание и использование (практика на Python)

#### Пример грамматики

Создадим простую грамматику для арифметических выражений (`Expr.g4`):

```antlr
grammar Expr;

expr
    : expr '*' expr  # Mul
    | expr '+' expr  # Add
    | INT            # Int
    ;

INT: [0-9]+;
WS: [ \t\r\n]+ -> skip;
```

#### Генерация парсера

Для генерации парсера используем команду:

```bash
antlr4 -Dlanguage=Python3 Expr.g4
```

Это создаст файлы:
- `ExprLexer.py`
- `ExprParser.py`
- `ExprListener.py` (базовый класс для Listener)

#### Сгенерированный класс ExprListener

ANTLR автоматически создаст базовый класс `ExprListener` примерно такого вида:

```python
class ExprListener(ParseTreeListener):
    def enterEveryRule(self, ctx):
        pass
    
    def exitEveryRule(self, ctx):
        pass
    
    def enterExpr(self, ctx):
        pass
    
    def exitExpr(self, ctx):
        pass
    
    def enterMul(self, ctx):
        pass
    
    def exitMul(self, ctx):
        pass
    
    # ... и так далее для всех правил
```

#### Кастомный класс-слушатель

Создадим свой класс для вычисления выражений:

```python
from ExprParser import ExprParser
from ExprListener import ExprListener

class MyListener(ExprListener):
    def __init__(self):
        self.stack = []  # Используем стек для хранения промежуточных результатов
    
    # Выход из узла с операцией сложения
    def exitAdd(self, ctx: ExprParser.AddContext):
        # ctx - это контекст узла, он содержит ссылки на дочерние элементы
        # Извлекаем два последних значения из стека
        right = self.stack.pop()
        left = self.stack.pop()
        # Выполняем операцию и помещаем результат обратно в стек
        self.stack.append(left + right)
    
    # Выход из узла с операцией умножения
    def exitMul(self, ctx: ExprParser.MulContext):
        right = self.stack.pop()
        left = self.stack.pop()
        self.stack.append(left * right)
    
    # Выход из узла с простым числом
    def exitInt(self, ctx: ExprParser.IntContext):
        # Получаем текстовое представление токена INT и преобразуем в число
        value = int(ctx.INT().getText())
        self.stack.append(value)
    
    def get_result(self):
        # Возвращаем конечный результат из стека
        return self.stack[0] if self.stack else None
```

**Примечание:** В данном примере используется стек, так как при обходе дерева в порядке depth-first мы сначала обрабатываем листья (числа), а затем операции. Для более сложных случаев можно использовать кастомные поля контекста для передачи данных вверх по дереву.

#### Использование Listener

```python
from antlr4 import *
from ExprLexer import ExprLexer
from ExprParser import ExprParser
from MyListener import MyListener

# Создаем входной поток
input_stream = InputStream("2 + 3 * 4")

# Создаем лексер и парсер
lexer = ExprLexer(input_stream)
stream = CommonTokenStream(lexer)
parser = ExprParser(stream)

# Парсим выражение и получаем дерево
tree = parser.expr()  # Начинаем разбор с правила 'expr'

# Создаем слушатель и обходчик
listener = MyListener()
walker = ParseTreeWalker()

# Обходим дерево с нашим слушателем
walker.walk(listener, tree)

# Получаем результат
print(f"Result: {listener.get_result()}")
```

### Плюсы и минусы

**Плюсы:**
- Простота использования — не нужно управлять обходом вручную
- Идеально для задач анализа (сбор информации, проверка типов, линтинг)
- Порядок обхода предопределен и предсказуем
- Легко добавлять новую функциональность, просто добавляя новые методы

**Минусы:**
- Мало контроля над порядком обхода
- Сложно передавать параметры "вниз" по дереву (например, контекст вычислений)
- Логика часто оказывается размазанной по множеству методов
- Для вычислений требуется использовать дополнительные структуры данных (стек, поля класса)

---

## 3. Механизм Visitor (Посетитель)

### Концепция

**Visitor** реализует паттерн "Посетитель" (Visitor Pattern). Это **активный механизм**, где мы сами управляем обходом дерева. Мы решаем, когда и как посещать дочерние узлы, можем изменять порядок обхода и легко передавать параметры вниз и возвращать результаты наверх.

### Как работает

1. По умолчанию ANTLR генерирует код только для Listener. Чтобы включить генерацию Visitor, нужно передать опцию `-visitor` при вызове генератора:

   ```bash
   antlr4 -visitor -Dlanguage=Python3 Expr.g4
   ```

2. ANTLR сгенерирует базовый класс `<GrammarName>Visitor` (например, `ExprVisitor`) с методами `visitEveryRuleName` для каждого правила.

3. Мы создаем свой класс-наследник и переопределяем метод `visitEveryRuleName` для тех правил, которые хотим обработать.

4. Ключевой метод — `visitChildren(ctx)`. Он запускает обход дочерних узлов текущего контекста. Мы можем:
   - Вызывать его или не вызывать
   - Вызывать в определенном порядке
   - Передавать ему аргументы
   - Использовать `self.visit(child)` для посещения конкретных дочерних узлов

### Создание и использование (практика на Python)

#### Сгенерированный класс ExprVisitor

ANTLR автоматически создаст базовый класс `ExprVisitor` примерно такого вида:

```python
class ExprVisitor(ParseTreeVisitor):
    def visitChildren(self, node):
        result = self.defaultResult()
        n = node.getChildCount()
        for i in range(n):
            if not self.shouldVisitNextChild(node, result):
                return result
            c = node.getChild(i)
            childResult = c.accept(self)
            result = self.aggregateResult(result, childResult)
        return result
    
    def visitExpr(self, ctx):
        return self.visitChildren(ctx)
    
    def visitMul(self, ctx):
        return self.visitChildren(ctx)
    
    # ... и так далее для всех правил
```

#### Кастомный класс-посетитель

Создадим класс для вычисления выражений:

```python
from ExprParser import ExprParser
from ExprVisitor import ExprVisitor

class MyVisitor(ExprVisitor):
    # Посещаем узел сложения
    def visitAdd(self, ctx: ExprParser.AddContext):
        # Рекурсивно посещаем левое и правое поддерево, чтобы вычислить их значения
        left_value = self.visit(ctx.expr(0))  # Посещаем первое дочернее выражение
        right_value = self.visit(ctx.expr(1))  # Посещаем второе дочернее выражение
        return left_value + right_value
    
    # Посещаем узел умножения
    def visitMul(self, ctx: ExprParser.MulContext):
        left_value = self.visit(ctx.expr(0))
        right_value = self.visit(ctx.expr(1))
        return left_value * right_value
    
    # Посещаем узел с целым числом
    def visitInt(self, ctx: ExprParser.IntContext):
        # Возвращаем числовое значение токена
        return int(ctx.INT().getText())
```

**Примечание:** Метод `visit` автоматически определяет тип узла и вызывает соответствующий метод `visitRuleName`. Если метод для конкретного правила не переопределен, будет вызван `visitChildren`, который обойдет все дочерние узлы.

#### Использование Visitor

```python
from antlr4 import *
from ExprLexer import ExprLexer
from ExprParser import ExprParser
from MyVisitor import MyVisitor

# Создаем входной поток
input_stream = InputStream("2 + 3 * 4")

# Создаем лексер и парсер
lexer = ExprLexer(input_stream)
stream = CommonTokenStream(lexer)
parser = ExprParser(stream)

# Парсим выражение и получаем дерево
tree = parser.expr()

# Создаем посетителя и обходим дерево
visitor = MyVisitor()
result = visitor.visit(tree)  # Запускаем обход с корня дерева

print(f"Result: {result}")
```

#### Расширенный пример: передача параметров вниз

Visitor позволяет легко передавать параметры вниз по дереву:

```python
class MyVisitor(ExprVisitor):
    def visitAdd(self, ctx: ExprParser.AddContext):
        # Передаем контекст вычислений вниз
        left_value = self.visit(ctx.expr(0))
        right_value = self.visit(ctx.expr(1))
        return left_value + right_value
    
    def visitMul(self, ctx: ExprParser.MulContext):
        # Можно передать дополнительные параметры, если переопределить visit
        left_value = self.visit(ctx.expr(0))
        right_value = self.visit(ctx.expr(1))
        return left_value * right_value
    
    def visitInt(self, ctx: ExprParser.IntContext):
        return int(ctx.INT().getText())
    
    # Можно переопределить visit для передачи параметров
    def visit(self, tree, param=None):
        if param is not None:
            # Обработка с параметром
            pass
        return super().visit(tree)
```

### Плюсы и минусы

**Плюсы:**
- Полный контроль над порядком обхода
- Легко передавать параметры вниз по дереву (как аргументы метода `visit`)
- Легко возвращать результаты наверх (через `return`)
- Идеально для трансляции, интерпретации, компиляции
- Более естественный способ выражения вычислений (рекурсивный стиль)

**Минусы:**
- Нужно самостоятельно управлять обходом (вызывать `visit` для дочерних узлов)
- Может быть немного более многословно
- Требует большей внимательности (легко забыть вызвать `visit` для дочернего узла)

---

## 4. Ключевые различия и когда что использовать

### Сравнительная таблица

| Характеристика | Listener | Visitor |
|----------------|----------|---------|
| **Управление обходом** | Автоматическое (`ParseTreeWalker`) | Ручное (вы сами вызываете `visit`) |
| **Передача данных** | Через поля класса (вверх) или кастомные поля контекста (вверх) | Через возвращаемые значения и параметры методов (вверх и вниз) |
| **Порядок обхода** | Строгий (depth-first, слева направо) | Произвольный (зависит от вашей реализации) |
| **Стиль программирования** | Event-driven (реактивный) | Императивный (активный) |
| **Сложность** | Проще для начинающих | Требует больше контроля |
| **Идеальные сценарии** | Анализ кода, сбор метрик, линтинг, поиск шаблонов, валидация | Вычисление выражений, трансляция в другой язык, генерация кода, интерпретация |

### Простое правило выбора

- **Используйте Listener**, если вам нужно **проанализировать** дерево:
  - Сбор статистики (количество функций, переменных)
  - Поиск определенных паттернов
  - Проверка правил кодирования (линтинг)
  - Валидация структуры

- **Используйте Visitor**, если вам нужно **вычислить** что-то на основе дерева или **трансформировать** его:
  - Вычисление выражений
  - Трансляция в другой язык
  - Генерация кода
  - Интерпретация
  - Оптимизация кода

---

## 5. Общие элементы для обоих подходов

### Контекст (ctx)

**Контекст** — это самое важное, что передается в каждый метод. Контекст узла (`AddContext`, `MulContext`, `IntContext` и т.д.) содержит всю информацию об этом узле:

- **Токены**: доступ через методы типа `ctx.INT()`, `ctx.PLUS()`
- **Дочерние контексты**: доступ через методы типа `ctx.expr(0)`, `ctx.expr(1)`
- **Методы для работы с узлом**: `getText()`, `getChildCount()`, `getChild(i)`

**Пример:**

```python
def exitAdd(self, ctx: ExprParser.AddContext):
    # Получаем дочерние выражения
    left_expr = ctx.expr(0)   # Первое выражение
    right_expr = ctx.expr(1)  # Второе выражение
    
    # Получаем токен оператора (если нужно)
    operator = ctx.PLUS()     # Токен '+'
    
    # Получаем текстовое представление всего узла
    text = ctx.getText()      # Например, "2 + 3"
```

### Метод getText()

`getText()` — основной способ получить текстовое представление токена или узла:

```python
# Для токена
token_text = ctx.INT().getText()  # "123"

# Для узла (включает весь текст всех дочерних узлов)
node_text = ctx.getText()  # "2 + 3 * 4"
```

### Структура сгенерированного парсера

Понимание структуры сгенерированного парсера — ключ к успешной работе:

- Для каждого правила грамматики создается класс контекста: `RuleNameContext`
- Для альтернатив с метками (например, `# Add`, `# Mul`) создаются отдельные классы: `AddContext`, `MulContext`
- Каждый контекст содержит методы для доступа к дочерним элементам и токенам

**Пример грамматики:**

```antlr
expr
    : expr '*' expr  # Mul
    | expr '+' expr  # Add
    | INT            # Int
    ;
```

**Сгенерированные классы:**

- `ExprContext` (базовый класс)
- `MulContext` (наследуется от `ExprContext`)
- `AddContext` (наследуется от `ExprContext`)
- `IntContext` (наследуется от `ExprContext`)

---

## 6. Заключение

Оба подхода — **Listener** и **Visitor** — мощны и эффективны для работы с синтаксическими деревьями в ANTLR4. Выбор между ними зависит от конкретной задачи:

- **Listener** идеален для анализа и сбора информации
- **Visitor** идеален для вычислений и трансформаций

Для работы с Python необходимо:

1. Использовать опцию `-Dlanguage=Python3` при генерации парсера
2. Для Visitor дополнительно использовать опцию `-visitor`
3. Установить библиотеку `antlr4-python3-runtime`:

   ```bash
   pip install antlr4-python3-runtime
   ```

**Полная команда генерации:**

```bash
# Для Listener (по умолчанию)
antlr4 -Dlanguage=Python3 Grammar.g4

# Для Visitor
antlr4 -visitor -Dlanguage=Python3 Grammar.g4

# Для обоих одновременно
antlr4 -visitor -Dlanguage=Python3 Grammar.g4
```

Понимание структуры сгенерированного парсера (какие классы контекста создаются для правил грамматики) — ключ к успешной работе с любым из механизмов. Изучайте сгенерированный код, чтобы лучше понимать, какие методы и свойства доступны в контекстах.

---

## Дополнительные ресурсы

- [Официальная документация ANTLR4](https://github.com/antlr/antlr4/blob/master/doc/index.md)
- [ANTLR4 Python Runtime](https://github.com/antlr/antlr4-python3-runtime)
- [The Definitive ANTLR 4 Reference](https://pragprog.com/titles/tpantlr2/the-definitive-antlr-4-reference/) — книга Теренса Парра






