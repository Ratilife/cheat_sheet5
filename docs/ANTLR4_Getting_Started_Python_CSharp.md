# ANTLR4: Изучение с нуля для начинающих (Python и C#)

## 1. Что такое ANTLR4 и зачем он нужен?

### Простая аналогия

Представьте, что вы встретили текст на неизвестном языке. Чтобы его понять, вам нужен переводчик. **ANTLR4** — это как "переводчик с иностранного языка" для компьютера.

- Есть текст на неизвестном языке (исходный код, конфигурационный файл, данные в специальном формате)
- ANTLR4 помогает написать "словарь и грамматику" этого языка
- На выходе мы получаем структурированное представление, которое уже может понять компьютер

### Формальное определение

**ANTLR4** (Another Tool for Language Recognition) — это **генератор парсеров**. Он автоматически создает программу (парсер), которая может читать и понимать текст согласно заданным правилам грамматики.

Вместо того чтобы вручную писать сложный код для разбора текста, вы описываете правила языка в специальном формате, а ANTLR4 генерирует весь необходимый код за вас.

### Примеры использования

ANTLR4 используется в самых разных областях:

- **Создание собственных языков программирования или DSL** (Domain Specific Languages)
  - Например, язык для описания бизнес-правил, конфигураций, запросов

- **Анализ конфигурационных файлов**
  - Парсинг SQL-запросов, логов, JSON, XML, YAML

- **Рефакторинг кода и статический анализ**
  - Поиск паттернов в коде, проверка стиля, поиск потенциальных ошибок

- **Трансляция из одного языка в другой**
  - Компиляция, преобразование форматов данных

---

## 2. Основная идея работы ANTLR4

### Упрощенный пайплайн работы

Работа с ANTLR4 состоит из нескольких простых шагов:

```
1. Я пишу грамматику (*.g4 файл)
   ↓
   Набор правил, описывающих язык
   
2. ANTLR4 генерирует код
   ↓
   На основе грамматики создает лексер и парсер на выбранном языке 
   (Python, C#, Java и др.)
   
3. Моя программа использует сгенерированный код
   ↓
   Подает на вход текст и получает структурированное дерево разбора
   
4. Я обхожу это дерево
   ↓
   Чтобы извлечь нужную информацию или выполнить действия
```

### Визуализация процесса

```
Исходный текст: "2 + 3 * 4"
         ↓
    [Лексер]
         ↓
Токены: [INT:2, PLUS:+, INT:3, MUL:*, INT:4]
         ↓
    [Парсер]
         ↓
   [AST - Дерево]
         ↓
  [Обход дерева]
         ↓
   Результат: 14
```

### Важное преимущество: переносимость грамматик

**Одна и та же грамматика** (`.g4` файл) может быть использована для генерации парсеров на разных языках программирования:

- Python: `antlr4 -Dlanguage=Python3 Grammar.g4`
- C#: `antlr4 -Dlanguage=CSharp Grammar.g4`
- Java: `antlr4 -Dlanguage=Java Grammar.g4`
- JavaScript: `antlr4 -Dlanguage=JavaScript Grammar.g4`

Это означает, что вы можете разработать грамматику один раз и использовать её в проектах на разных языках!

---

## 3. Ключевые концепции на пальцах

### Лексер (Lexer) vs Парсер (Parser)

#### Лексер (Lexer) — "Разбиватель на слова"

Лексер разбивает исходный текст на **токены** (tokens) — отдельные "слова" языка.

**Пример:**
- Исходный текст: `"2 + 3 * 4"`
- Токены после лексера: `[INT:2, PLUS:+, INT:3, MUL:*, INT:4]`

Лексер не понимает структуру — он просто разбивает текст на части согласно правилам.

#### Парсер (Parser) — "Пониматель структуры"

Парсер анализирует последовательность токенов согласно грамматике и строит **дерево разбора (AST)**. Он понимает, что умножение имеет высший приоритет, чем сложение, и строит правильную структуру.

**Пример:**
- Токены: `[INT:2, PLUS:+, INT:3, MUL:*, INT:4]`
- Парсер понимает: сначала `3 * 4`, потом `2 + 12`
- Результат: `14`

### Грамматика (*.g4 файл)

Грамматика — это файл с расширением `.g4`, где вы описываете правила языка. Давайте разберем максимально простой пример:

```antlr
grammar SimpleMath;

// Правила для лексера (токены) - ЗАГЛАВНЫЕ БУКВЫ
INT     : [0-9]+ ;           // Одно или более цифр
PLUS    : '+' ;              // Символ плюс
MUL     : '*' ;              // Символ умножения
WS      : [ \t\r\n]+ -> skip ; // Пропускаем пробельные символы

// Правила для парсера (структура) - строчные буквы
expr    : expr PLUS expr  # Add    // Сложение
        | expr MUL expr   # Mul    // Умножение
        | INT             # Number // Число
        ;
```

#### Разбор грамматики по частям:

1. **`grammar SimpleMath;`**
   - Название грамматики. Должно совпадать с именем файла (SimpleMath.g4)

2. **`INT : [0-9]+ ;`** (правило лексера)
   - `INT` — имя токена (заглавные буквы)
   - `[0-9]+` — регулярное выражение: одна или более цифр
   - Это правило говорит: "если видишь последовательность цифр, создай токен INT"

3. **`expr : expr PLUS expr # Add`** (правило парсера)
   - `expr` — имя правила (строчные буквы)
   - `expr PLUS expr` — структура: выражение, затем плюс, затем выражение
   - `# Add` — метка для удобства (позволяет различать альтернативы)

4. **`WS : [ \t\r\n]+ -> skip ;`**
   - `WS` — пробельные символы (whitespace)
   - `-> skip` — пропустить эти токены (не передавать в парсер)

#### Важное правило:

- **ЗАГЛАВНЫЕ БУКВЫ** (INT, PLUS, MUL) — правила для **лексера** (токены)
- **строчные буквы** (expr) — правила для **парсера** (структура)

### AST (Abstract Syntax Tree) — Дерево разбора

AST — это структурированное представление текста в виде дерева. Дерево показывает **структуру**, а не просто последовательность токенов.

#### Визуальное представление для выражения "2 + 3 * 4":

```
        expr (Add)
       /         \
   expr (Number)  expr (Mul)
      |          /         \
    INT(2)   expr (Number) expr (Number)
                 |            |
              INT(3)        INT(4)
```

#### Что показывает дерево:

- **Структура**: умножение выполняется первым (выше в дереве)
- **Приоритет**: `3 * 4` вычисляется до сложения
- **Иерархия**: каждое выражение может содержать подвыражения

Дерево позволяет нам правильно вычислить выражение: сначала `3 * 4 = 12`, затем `2 + 12 = 14`.

---

## 4. Практический пример "Hello World"

### Вариант A: Python (для простоты и обучения)

Python — отличный выбор для изучения ANTLR4 благодаря простоте синтаксиса и быстрой разработке.

#### Шаг 0: Установка

```bash
# Установка Python runtime для ANTLR4
pip install antlr4-python3-runtime

# Установка ANTLR4 (генератор парсеров)
# Для Windows (через Chocolatey):
choco install antlr4

# Для Linux/Mac:
# Скачайте JAR файл с https://www.antlr.org/download.html
# Или используйте: brew install antlr
```

#### Шаг 1: Создаем грамматику

Создайте файл `SimpleMath.g4`:

```antlr
grammar SimpleMath;

// Правила для лексера (токены)
INT     : [0-9]+ ;
PLUS    : '+' ;
MUL     : '*' ;
WS      : [ \t\r\n]+ -> skip ; // Пропускаем пробельные символы

// Правила для парсера (структура)
expr    : expr PLUS expr  # Add
        | expr MUL expr   # Mul
        | INT             # Number
        ;
```

#### Шаг 2: Генерируем парсер

Выполните команду в терминале (в папке с файлом `SimpleMath.g4`):

```bash
antlr4 -Dlanguage=Python3 SimpleMath.g4
```

Эта команда создаст несколько файлов:
- `SimpleMathLexer.py` — лексер
- `SimpleMathParser.py` — парсер
- `SimpleMathListener.py` — базовый класс для обхода дерева
- `SimpleMath.tokens` — служебный файл
- `SimpleMathLexer.tokens` — служебный файл

#### Шаг 3: Пишем простую программу на Python

Создайте файл `main.py`:

```python
from antlr4 import *
from SimpleMathLexer import SimpleMathLexer
from SimpleMathParser import SimpleMathParser

# Создаем входной поток
input_text = "2 + 3 * 4"
input_stream = InputStream(input_text)

# Создаем лексер
lexer = SimpleMathLexer(input_stream)

# Создаем поток токенов
token_stream = CommonTokenStream(lexer)

# Создаем парсер
parser = SimpleMathParser(token_stream)

# Запускаем парсинг, начиная с корневого правила 'expr'
tree = parser.expr()

# Выводим дерево в текстовом виде
print("Дерево разбора:")
print(tree.toStringTree(recog=parser))
```

#### Шаг 4: Запускаем программу

```bash
python main.py
```

**Вывод:**
```
Дерево разбора:
(expr (expr 2) + (expr (expr 3) * (expr 4)))
```

#### Расширенный пример: просмотр токенов (Python)

```python
from antlr4 import *
from SimpleMathLexer import SimpleMathLexer
from SimpleMathParser import SimpleMathParser

input_text = "2 + 3 * 4"
input_stream = InputStream(input_text)

lexer = SimpleMathLexer(input_stream)
token_stream = CommonTokenStream(lexer)

# Просмотр всех токенов
print("Токены:")
token_stream.fill()  # Загружаем все токены
for token in token_stream.tokens:
    if token.type != -1:  # -1 это EOF (конец файла)
        print(f"  {lexer.symbolicNames[token.type]}: '{token.text}'")

# Парсинг
parser = SimpleMathParser(token_stream)
tree = parser.expr()

print("\nДерево разбора:")
print(tree.toStringTree(recog=parser))
```

**Вывод:**
```
Токены:
  INT: '2'
  PLUS: '+'
  INT: '3'
  MUL: '*'
  INT: '4'

Дерево разбора:
(expr (expr 2) + (expr (expr 3) * (expr 4)))
```

---

### Вариант B: C# (для реальных проектов)

C# — отличный выбор для production-проектов благодаря производительности, строгой типизации и интеграции с .NET экосистемой.

#### Шаг 0: Установка

**Вариант 1: Использование JAR файла (универсальный способ)**

1. Установите **Java Runtime Environment (JRE)** версии 8 или выше
   - Скачайте с [Oracle](https://www.oracle.com/java/technologies/downloads/) или используйте OpenJDK

2. Скачайте **ANTLR JAR файл**:
   - Перейдите на [официальный сайт ANTLR](https://www.antlr.org/download.html)
   - Скачайте `antlr-4.13.1-complete.jar` (или последнюю версию)

3. Добавьте JAR в PATH или используйте полный путь

**Вариант 2: Использование NuGet пакета (рекомендуется для Visual Studio)**

1. Откройте проект в Visual Studio
2. Установите NuGet пакет `Antlr4.Runtime.Standard`:
   ```powershell
   Install-Package Antlr4.Runtime.Standard
   ```
   Или через Package Manager Console:
   ```
   NuGet\Install-Package Antlr4.Runtime.Standard
   ```

#### Шаг 1: Создаем грамматику

Создайте файл `SimpleMath.g4` (тот же самый, что и для Python):

```antlr
grammar SimpleMath;

// Правила для лексера (токены)
INT     : [0-9]+ ;
PLUS    : '+' ;
MUL     : '*' ;
WS      : [ \t\r\n]+ -> skip ; // Пропускаем пробельные символы

// Правила для парсера (структура)
expr    : expr PLUS expr  # Add
        | expr MUL expr   # Mul
        | INT             # Number
        ;
```

#### Шаг 2: Генерируем парсер

Выполните команду в терминале (в папке с файлом `SimpleMath.g4`):

```bash
java -jar antlr-4.13.1-complete.jar -Dlanguage=CSharp SimpleMath.g4
```

Или если ANTLR в PATH:

```bash
antlr4 -Dlanguage=CSharp SimpleMath.g4
```

Эта команда создаст файлы:
- `SimpleMathLexer.cs` — лексер
- `SimpleMathParser.cs` — парсер
- `SimpleMathListener.cs` — базовый класс для обхода дерева
- `SimpleMathBaseListener.cs` — базовый класс Listener
- `SimpleMathVisitor.cs` — базовый класс Visitor
- `SimpleMathBaseVisitor.cs` — базовая реализация Visitor
- Служебные файлы `.tokens`

#### Шаг 3: Пишем простую программу на C#

Создайте файл `Program.cs`:

```csharp
using Antlr4.Runtime;
using System;

class Program
{
    static void Main()
    {
        // Создаем входной поток
        string inputText = "2 + 3 * 4";
        ICharStream inputStream = CharStreams.fromString(inputText);
        
        // Создаем лексер
        SimpleMathLexer lexer = new SimpleMathLexer(inputStream);
        
        // Создаем поток токенов
        CommonTokenStream tokenStream = new CommonTokenStream(lexer);
        
        // Создаем парсер
        SimpleMathParser parser = new SimpleMathParser(tokenStream);
        
        // Запускаем парсинг, начиная с корневого правила 'expr'
        SimpleMathParser.ExprContext tree = parser.expr();
        
        // Выводим дерево в текстовом виде
        Console.WriteLine("Дерево разбора:");
        Console.WriteLine(tree.ToStringTree(parser));
    }
}
```

#### Шаг 4: Настройка проекта

**В Visual Studio:**

1. Добавьте сгенерированные файлы в проект (Add → Existing Item)
2. Убедитесь, что установлен NuGet пакет `Antlr4.Runtime.Standard`
3. Если используете .NET Core/.NET 5+, добавьте в `.csproj`:

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net6.0</TargetFramework>
  </PropertyGroup>
  
  <ItemGroup>
    <PackageReference Include="Antlr4.Runtime.Standard" Version="4.13.1" />
  </ItemGroup>
</Project>
```

#### Шаг 5: Запускаем программу

```bash
dotnet run
```

Или в Visual Studio: `F5` или `Ctrl+F5`

**Вывод:**
```
Дерево разбора:
(expr (expr 2) + (expr (expr 3) * (expr 4)))
```

#### Расширенный пример: просмотр токенов (C#)

```csharp
using Antlr4.Runtime;
using System;

class Program
{
    static void Main()
    {
        string inputText = "2 + 3 * 4";
        ICharStream inputStream = CharStreams.fromString(inputText);
        
        SimpleMathLexer lexer = new SimpleMathLexer(inputStream);
        CommonTokenStream tokenStream = new CommonTokenStream(lexer);
        
        // Просмотр всех токенов
        Console.WriteLine("Токены:");
        tokenStream.Fill();
        foreach (var token in tokenStream.GetTokens())
        {
            if (token.Type != SimpleMathLexer.Eof) // Eof = -1
            {
                var tokenName = lexer.Vocabulary.GetSymbolicName(token.Type);
                Console.WriteLine($"  {tokenName}: '{token.Text}'");
            }
        }
        
        // Парсинг
        SimpleMathParser parser = new SimpleMathParser(tokenStream);
        var tree = parser.expr();
        
        Console.WriteLine("\nДерево разбора:");
        Console.WriteLine(tree.ToStringTree(parser));
    }
}
```

**Вывод:**
```
Токены:
  INT: '2'
  PLUS: '+'
  INT: '3'
  MUL: '*'
  INT: '4'

Дерево разбора:
(expr (expr 2) + (expr (expr 3) * (expr 4)))
```

---

## 5. Пример: Анализ простого подмножества C#

Давайте создадим более практичный пример — грамматику для анализа классов C#.

### Грамматика для анализа классов C#

Создайте файл `CSharpMini.g4`:

```antlr
grammar CSharpMini;

// Лексер
CLASS       : 'class' ;
PUBLIC      : 'public' ;
PRIVATE     : 'private' ;
ID          : [a-zA-Z_][a-zA-Z_0-9]* ;
LBRACE      : '{' ;
RBRACE      : '}' ;
SEMICOLON   : ';' ;
WS          : [ \t\r\n]+ -> skip ;

// Парсер
compilationUnit : classDefinition+ ;

classDefinition : accessModifier? CLASS ID LBRACE classBody RBRACE ;

accessModifier  : PUBLIC | PRIVATE ;

classBody       : (methodDefinition | fieldDefinition)* ;

methodDefinition : accessModifier? ID '(' ')' LBRACE RBRACE ;

fieldDefinition  : accessModifier? ID ID SEMICOLON ;
```

### Использование в C#

Создайте файл `CSharpAnalyzer.cs`:

```csharp
using Antlr4.Runtime;
using System;

class CSharpAnalyzer
{
    static void Main()
    {
        string code = @"
            public class Program 
            { 
                private int count;
                public void Main() { }
            } 
            class Calculator 
            { 
                public int Add() { }
            }";
        
        ICharStream stream = CharStreams.fromString(code);
        
        CSharpMiniLexer lexer = new CSharpMiniLexer(stream);
        CommonTokenStream tokens = new CommonTokenStream(lexer);
        CSharpMiniParser parser = new CSharpMiniParser(tokens);
        
        var tree = parser.compilationUnit();
        
        // Подсчитываем классы
        var classes = tree.classDefinition();
        Console.WriteLine($"Найдено классов: {classes.Length}");
        
        // Выводим имена классов
        foreach (var classDef in classes)
        {
            var className = classDef.ID().GetText();
            Console.WriteLine($"  - {className}");
        }
        
        // Выводим дерево
        Console.WriteLine("\nДерево разбора:");
        Console.WriteLine(tree.ToStringTree(parser));
    }
}
```

**Вывод:**
```
Найдено классов: 2
  - Program
  - Calculator

Дерево разбора:
(compilationUnit (classDefinition public class Program { (classBody (fieldDefinition private int count ;) (methodDefinition public Main ( ) { })) } ) (classDefinition class Calculator { (classBody (methodDefinition public Add ( ) { })) } ))
```

### Использование в Python

Та же грамматика работает и в Python! Сгенерируйте парсер:

```bash
antlr4 -Dlanguage=Python3 CSharpMini.g4
```

Использование:

```python
from antlr4 import *
from CSharpMiniLexer import CSharpMiniLexer
from CSharpMiniParser import CSharpMiniParser

code = """
public class Program 
{ 
    private int count;
    public void Main() { }
} 
class Calculator 
{ 
    public int Add() { }
}"""

stream = InputStream(code)
lexer = CSharpMiniLexer(stream)
tokens = CommonTokenStream(lexer)
parser = CSharpMiniParser(tokens)

tree = parser.compilationUnit()

# Подсчитываем классы
classes = tree.classDefinition()
print(f"Найдено классов: {len(classes)}")

# Выводим имена классов
for class_def in classes:
    class_name = class_def.ID().getText()
    print(f"  - {class_name}")

# Выводим дерево
print("\nДерево разбора:")
print(tree.toStringTree(recog=parser))
```

**Вывод:**
```
Найдено классов: 2
  - Program
  - Calculator

Дерево разбора:
(compilationUnit (classDefinition public class Program { (classBody (fieldDefinition private int count ;) (methodDefinition public Main ( ) { })) } ) (classDefinition class Calculator { (classBody (methodDefinition public Add ( ) { })) } ))
```

**Это демонстрирует переносимость грамматик!** Одна и та же грамматика работает и в Python, и в C#.

---

## 6. Что дальше? Listeners и Visitors

После того как вы создали дерево разбора, вам нужно его обойти, чтобы извлечь информацию или выполнить действия. ANTLR4 предоставляет два основных механизма:

### Listener (Слушатель) — автоматический обход

**Как работает:**
- ANTLR автоматически обходит дерево
- Вызывает ваши методы, когда заходит в узел (`enterRuleName`)
- Вызывает ваши методы, когда выходит из узла (`exitRuleName`)
- Вы не управляете порядком обхода

**Когда использовать:**
- Анализ кода
- Сбор статистики
- Поиск паттернов
- Валидация

**Пример концепции (Python):**
```python
class MyListener(SimpleMathListener):
    def exitAdd(self, ctx):
        print("Найдено сложение!")
    
    def exitMul(self, ctx):
        print("Найдено умножение!")
```

**Пример концепции (C#):**
```csharp
class MyListener : SimpleMathBaseListener
{
    public override void ExitAdd(SimpleMathParser.AddContext context)
    {
        Console.WriteLine("Найдено сложение!");
    }
    
    public override void ExitMul(SimpleMathParser.MulContext context)
    {
        Console.WriteLine("Найдено умножение!");
    }
}
```

### Visitor (Посетитель) — ручной обход

**Как работает:**
- Вы сами управляете обходом дерева
- Решаете, какие узлы посещать и в каком порядке
- Можете передавать параметры вниз и возвращать результаты наверх

**Когда использовать:**
- Вычисление выражений
- Трансляция в другой язык
- Генерация кода
- Интерпретация

**Пример концепции (Python):**
```python
class MyVisitor(SimpleMathVisitor):
    def visitAdd(self, ctx):
        left = self.visit(ctx.expr(0))
        right = self.visit(ctx.expr(1))
        return left + right
```

**Пример концепции (C#):**
```csharp
class MyVisitor : SimpleMathBaseVisitor<int>
{
    public override int VisitAdd(SimpleMathParser.AddContext context)
    {
        int left = Visit(context.expr(0));
        int right = Visit(context.expr(1));
        return left + right;
    }
}
```

### Рекомендация для начинающих

**Начните с Listener**, так как он проще:
- Не нужно управлять обходом вручную
- Меньше кода для написания
- Легче понять концепцию

Подробнее о Listeners и Visitors читайте в конспекте `ANTLR4_Listeners_and_Visitors.md`.

---

## 7. Типичные ошибки новичков

### Ошибка 1: Перепутал правила лексера и парсера

**Неправильно:**
```antlr
grammar Wrong;

expr : EXPR PLUS EXPR ;  // ОШИБКА: EXPR должен быть строчным
EXPR : [a-z]+ ;          // ОШИБКА: это правило парсера, не лексера
```

**Правильно:**
```antlr
grammar Correct;

ID : [a-z]+ ;            // Лексер - ЗАГЛАВНЫЕ
expr : expr PLUS expr ;  // Парсер - строчные
```

**Правило:** Заглавные буквы = лексер, строчные = парсер.

### Ошибка 2: Не учел приоритет операций в грамматике

**Проблема:**
```antlr
expr : expr PLUS expr    // Сложение
     | expr MUL expr     // Умножение
     | INT
     ;
```

Такая грамматика не учитывает приоритет! Умножение и сложение имеют одинаковый приоритет, что неправильно.

**Решение:** Используйте отдельные уровни правил:

```antlr
expr : expr PLUS term    // Сложение на верхнем уровне
     | term
     ;

term : term MUL factor   // Умножение на нижнем уровне (выше приоритет)
     | factor
     ;

factor : INT
       | '(' expr ')'
       ;
```

### Ошибка 3: Забыл пропускать пробельные символы

**Проблема:**
```antlr
grammar NoWhitespace;

INT : [0-9]+ ;
PLUS : '+' ;
// Нет правила для WS!
```

Парсер будет пытаться обработать пробелы как токены и выдаст ошибку.

**Решение:**
```antlr
WS : [ \t\r\n]+ -> skip ; // Всегда добавляйте это правило!
```

### Ошибка 4: Не понимает разницу между getText() и доступом к контексту

**getText()** возвращает весь текст узла как строку:
- Python: `ctx.getText()` → `"2 + 3 * 4"`
- C#: `context.GetText()` → `"2 + 3 * 4"`

**Доступ к контексту** позволяет получить дочерние элементы:
- Python: `ctx.expr(0)` → первое дочернее выражение (контекст, не строка!)
- C#: `context.expr(0)` → первое дочернее выражение (контекст, не строка!)

**Пример правильного использования (Python):**
```python
def exitAdd(self, ctx):
    # Неправильно:
    text = ctx.getText()  # Получим "2+3", но не сможем разделить
    
    # Правильно:
    left = ctx.expr(0).getText()   # "2"
    right = ctx.expr(1).getText()  # "3"
```

**Пример правильного использования (C#):**
```csharp
public override void ExitAdd(SimpleMathParser.AddContext context)
{
    // Неправильно:
    string text = context.GetText();  // Получим "2+3", но не сможем разделить
    
    // Правильно:
    string left = context.expr(0).GetText();   // "2"
    string right = context.expr(1).GetText();  // "3"
}
```

### Ошибка 5: В C# — забыл подключить ссылки на Antlr4.Runtime

**Проблема:**
При компиляции C# проекта возникают ошибки:
```
The type or namespace name 'Antlr4' could not be found
```

**Решение:**

1. **Через NuGet Package Manager:**
   ```
   Install-Package Antlr4.Runtime.Standard
   ```

2. **Через .csproj файл:**
   ```xml
   <ItemGroup>
     <PackageReference Include="Antlr4.Runtime.Standard" Version="4.13.1" />
   </ItemGroup>
   ```

3. **Через .NET CLI:**
   ```bash
   dotnet add package Antlr4.Runtime.Standard
   ```

### Ошибка 6: Неправильный порядок правил в грамматике

ANTLR4 выбирает первое подходящее правило. Если более общее правило стоит первым, более специфичное никогда не сработает.

**Неправильно:**
```antlr
ID : [a-z]+ ;        // Это сработает для "if", "while" и т.д.
IF : 'if' ;          // Это никогда не сработает!
WHILE : 'while' ;
```

**Правильно:**
```antlr
IF : 'if' ;          // Специфичные правила ПЕРВЫМИ
WHILE : 'while' ;
ID : [a-z]+ ;        // Общее правило ПОСЛЕДНИМ
```

### Ошибка 7: Забыл указать язык при генерации

**Неправильно:**
```bash
antlr4 SimpleMath.g4  # Сгенерирует Java код по умолчанию!
```

**Правильно:**
```bash
# Для Python
antlr4 -Dlanguage=Python3 SimpleMath.g4

# Для C#
antlr4 -Dlanguage=CSharp SimpleMath.g4
```

### Ошибка 8: В C# — не добавил сгенерированные файлы в проект

**Проблема:**
Сгенерированные `.cs` файлы не компилируются.

**Решение:**
1. В Visual Studio: правой кнопкой на проект → Add → Existing Item → выберите все `.cs` файлы
2. Или добавьте в `.csproj`:
   ```xml
   <ItemGroup>
     <Compile Include="SimpleMath*.cs" />
   </ItemGroup>
   ```

---

## 8. Заключение

### Резюме

**ANTLR4** — это мощный инструмент, который избавляет от рутинного написания парсеров. Вместо того чтобы вручную писать сложный код для разбора текста, вы:

1. Описываете правила языка в файле грамматики (`.g4`)
2. Генерируете парсер одной командой
3. Используете сгенерированный код в своей программе

### Основная работа — проектирование правильной грамматики

Самая важная и сложная часть работы с ANTLR4 — это **правильное проектирование грамматики**:

- Правила должны корректно отражать структуру языка
- Нужно учитывать приоритет операций
- Важно правильно разделить правила лексера и парсера
- Специфичные правила должны идти перед общими

### Рекомендации по выбору языка

**Начните с Python для обучения:**
- Простой синтаксис
- Быстрая разработка
- Легко экспериментировать
- Отлично подходит для прототипирования

**Переходите к C# для production-проектов:**
- Строгая типизация
- Высокая производительность
- Интеграция с .NET экосистемой
- Поддержка Visual Studio и современных инструментов разработки

### Переносимость грамматик

**Важное преимущество ANTLR4:** грамматики переносимы между разными языками программирования!

- Одна и та же грамматика (`.g4` файл) может использоваться для генерации парсеров на Python, C#, Java, JavaScript и других языках
- Это означает, что вы можете разработать грамматику один раз и использовать её в проектах на разных языках
- Идеально для команд, работающих с разными технологиями

### Следующие шаги

1. **Попрактикуйтесь** с простыми грамматиками (арифметика, простые команды)
2. **Изучите Listeners** для обхода дерева
3. **Изучите Visitors** для более сложных задач
4. **Экспериментируйте** с разными конструкциями грамматики
5. **Изучите реальные грамматики** популярных языков (SQL, JSON, XML)

### Полезные ресурсы

- [Официальный сайт ANTLR4](https://www.antlr.org/)
- [Документация ANTLR4](https://github.com/antlr/antlr4/blob/master/doc/index.md)
- [ANTLR4 Python Runtime](https://github.com/antlr/antlr4-python3-runtime)
- [ANTLR4 C# Runtime](https://www.nuget.org/packages/Antlr4.Runtime.Standard/)
- Книга: "The Definitive ANTLR 4 Reference" by Terence Parr
- [Грамматики популярных языков](https://github.com/antlr/grammars-v4)

### Помните

ANTLR4 — это инструмент, который делает сложное простым. Начните с простых примеров на Python, постепенно усложняйте задачи, и когда будете готовы к production-проектам, переходите на C#. Одна и та же грамматика будет работать везде!

---

**Удачи в изучении ANTLR4! 🚀**



