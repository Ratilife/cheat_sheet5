# Анализ функционала класса STHighlighter

## 1. Архитектура и назначение

### 1.1 Наследование и базовый функционал
- Класс `STHighlighter` наследуется от `QSyntaxHighlighter` (PySide6)
- Предназначен для подсветки синтаксиса в файлах `.st`
- Поддерживает множественные языки через ANTLR лексеры (1C/BSL, Python, C#, Java)
- Использует механизм кэширования токенов для оптимизации

### 1.2 Основные компоненты
- **Цветовая схема** (`color_map`): словарь с цветами для токенов по языкам
- **Карта ключевых слов** (`keywords_map`): маппинг русских ключевых слов 1C на типы токенов
- **Кэш токенов** (`_tokens_by_line`): словарь `dict[int, list]` для хранения токенов по номерам строк
- **Текущий текст документа** (`_document_text`): строка для отслеживания изменений

---

## 2. Инициализация

### 2.1 Метод `__init__(parent, language)`
**Параметры:**
- `parent`: QTextDocument - документ из QTextEdit
- `language`: str - язык программирования (опционально)

**Действия:**
1. Вызывает `super().__init__(parent)` для инициализации базового класса
2. Сохраняет язык в `self.language`
3. Вызывает `_init_color_map()` для инициализации цветовой схемы
4. Инициализирует `_tokens_by_line = {}` (пустой словарь)
5. Инициализирует `_document_text = ""` (пустая строка)

### 2.2 Метод `_init_color_map()`
**Назначение:** Создает цветовую схему для токенов

**Структура данных:**
- `self.color_map`: словарь с ключами `'1c'`, `'python'`, `'csharp'`, `'java'`
- Для языка `'1c'` заполнено ~150+ типов токенов с цветами
- Для остальных языков - пустые словари `{}`

**Цвета:**
- `'green'`: комментарии (`LINE_COMMENT`)
- `'red'`: ключевые слова, операторы, скобки
- `'blue'`: идентификаторы (`IDENTIFIER`, `UNKNOWN`)
- `'brown'`: препроцессорные директивы, аннотации
- `'gray'`: числа (`DECIMAL`, `FLOAT`, `DATETIME`)
- `'black'`: строки (`STRING`, `STRINGSTART`, и т.д.)
- `None`: пробелы (`WHITE_SPACE`)

**Дополнительно:**
- `self.keywords_map`: словарь русских ключевых слов 1C → типы токенов
  - Примеры: `'Процедура' → 'PROCEDURE_KEYWORD'`, `'Если' → 'IF_KEYWORD'`

---

## 3. Управление языком

### 3.1 Метод `set_language(language: str)`
**Назначение:** Устанавливает язык программирования и переподсвечивает документ

**Алгоритм работы:**
1. **Нормализация языка:**
   - Приводит к нижнему регистру
   - Применяет маппинг синонимов: `'bsl' → '1c'`, `'cs' → 'csharp'`, `'c#' → 'csharp'`
   - Если `language` пустой/None, устанавливает `None`

2. **Сохранение старого языка:**
   - `old_language = self.language`
   - `self.language = language`

3. **Переподсветка при изменении:**
   - Если `old_language != self.language`:
     - Вызывает `self.rehighlight()` (строка 257)
     - Вызывает `self._rebuild_tokens_cache()` (строка 260)
     - Вызывает `self.rehighlight()` еще раз (строка 261)

**Проблема:** Двойной вызов `rehighlight()` при изменении языка

---

## 4. Кэширование токенов

### 4.1 Метод `_rebuild_tokens_cache()`
**Назначение:** Пересчитывает кэш токенов для всего документа

**Условия выхода:**
- Если язык не установлен (`not self.language`)
- Если язык не равен `'1c'` (`self.language != '1c'`)
- Если документ не установлен (`not self.document()`)
- Если документ пуст (`not document_text.strip()`)

**Алгоритм работы:**
1. **Очистка кэша:**
   - `self._tokens_by_line = {}`

2. **Получение текста документа:**
   - `document_text = self.document().toPlainText()`
   - `self._document_text = document_text` (сохранение для сравнения)

3. **Лексический анализ через ANTLR:**
   - Создает `InputStream(self._document_text)`
   - Создает `BSLLexer(input_stream)`
   - Итерирует по токенам через `lexer.nextToken()`

4. **Обработка каждого токена:**
   - Получает номер строки: `line_number = token.line` (ANTLR нумерует с 1)
   - Определяет тип токена:
     - Из `lexer.symbolicNames[token.type]`
     - Если тип `'<INVALID>'`, устанавливает `token_type = None`
   - Проверяет ключевые слова:
     - `lexeme = (token.text or '').lower()`
     - Если `lexeme in self.keywords_map`, заменяет `token_type` на значение из словаря

5. **Сохранение в кэш:**
   - Проверяет наличие строки: `if line_number not in self._tokens_by_line`
   - Создает список: `self._tokens_by_line[line_number] = []`
   - Добавляет кортеж: `self._tokens_by_line[line_number].append((token, token_type))` (строка 315)
   
   **ПРОБЛЕМА:** Дублирование кода (строки 318-322):
   - Повторная проверка `if line_number not in self._tokens_by_line`
   - Добавление просто токена: `self._tokens_by_line[line_number].append(token)`
   - Это приводит к смешанной структуре данных в кэше

**Обработка ошибок:**
- При исключении выводит traceback и пробрасывает исключение дальше
- Закомментированная строка очистки кэша при ошибке

**Результат:**
- `_tokens_by_line`: словарь, где ключ - номер строки (int), значение - список
- **Проблема структуры:** список может содержать как кортежи `(token, token_type)`, так и просто `token`

---

## 5. Подсветка блоков (highlightBlock)

### 5.1 Метод `highlightBlock(text: str)`
**Назначение:** Автоматически вызывается Qt для каждой строки текста

**Параметры:**
- `text: str` - текст текущей строки

**Алгоритм:**
1. Если язык не установлен (`not self.language`), выходит
2. Вызывает соответствующий метод подсветки:
   - `'1c'` → `_apply_1c_highlighting(text)`
   - `'python'` → `_apply_python_highlighting(text)` (заглушка)
   - `'csharp'` → `_apply_csharp_highlighting(text)` (заглушка)
   - `'java'` → `_apply_java_highlighting(text)` (заглушка)

**Особенность:** Qt вызывает этот метод для каждого блока (строки) документа при переподсветке

---

## 6. Подсветка языка 1C

### 6.1 Метод `_apply_1c_highlighting(text: str)`
**Назначение:** Применяет подсветку для языка 1C/BSL используя кэш токенов

**Алгоритм:**
1. **Получение номера строки:**
   - `current_block_number = self.currentBlock().blockNumber() + 1`
   - Qt нумерует блоки с 0, поэтому добавляется 1

2. **Получение токенов из кэша:**
   - `tokens_for_line = self._tokens_by_line.get(current_block_number, [])`
   - Если токенов нет, выходит

3. **Обработка токенов:**
   - Итерирует по `tokens_for_line`
   - **Ожидает кортежи:** `for token, token_type in tokens_for_line:`
   - Пропускает невалидные: `if not token_type or token_type == '<INVALID>'`
   - Вызывает `_apply_token_format(token, token_type, '1c')`

**Проблема:** Если в кэше есть просто токены (не кортежи), произойдет ошибка распаковки

**Отладочный вывод:**
- `print(f"[STHighlighter] highlight line {current_block_number}, tokens={len(tokens_for_line)}")`

---

## 7. Применение форматирования токенов

### 7.1 Метод `_apply_token_format(token, token_type: str, lang: str)`
**Назначение:** Применяет форматирование к токену

**Параметры:**
- `token`: ANTLR Token объект
- `token_type`: str - символическое имя токена
- `lang`: str - язык ('1c', 'python', etc.)

**Алгоритм:**
1. **Проверка наличия типа в цветовой схеме:**
   - Если `token_type not in self.color_map.get(lang, {})`, выходит

2. **Создание формата:**
   - `fmt = QTextCharFormat()`
   - `color = QColor(self.color_map[lang][token_type])`
   - `fmt.setForeground(color)`

3. **Определение позиции токена:**
   - Получает позицию начала блока: `block_start = block.position()`
   - Использует `token.column` как позицию от начала строки
   - `start_pos = token.column`
   - `length = len(token.text)`

4. **Проверка принадлежности токена текущему блоку:**
   - `current_block_number = self.currentBlock().blockNumber() + 1`
   - Если `token.line != current_block_number`, выходит (токен из другой строки)

5. **Применение форматирования:**
   - `self.setFormat(start_pos, length, fmt)`

**Потенциальные проблемы:**
- `token.column` может быть неправильным для многострочных токенов
- Не учитывается табуляция (ANTLR может учитывать табы в column)

---

## 8. Управление документом

### 8.1 Метод `setDocument(doc)`
**Назначение:** Переопределяет метод для пересчёта кэша при смене документа

**Алгоритм:**
1. Вызывает `super().setDocument(doc)`
2. Если документ установлен (`doc`), вызывает `_rebuild_tokens_cache()`

**Особенность:** Вызывается автоматически Qt при установке документа в highlighter

### 8.2 Метод `rehighlight()`
**Назначение:** Переопределяет для пересчёта кэша перед переподсветкой

**Алгоритм:**
1. **Проверка изменения текста:**
   - Если документ установлен:
     - `current_text = self.document().toPlainText()`
     - Если `current_text != self._document_text`:
       - Вызывает `_rebuild_tokens_cache()`

2. **Вызов родительского метода:**
   - `super().rehighlight()` - вызывает `highlightBlock()` для каждого блока

**Особенность:** Вызывается при изменении документа или языка

---

## 9. Вспомогательные методы

### 9.1 Метод `_token_to_position(token)`
**Назначение:** Конвертирует токен ANTLR в позицию символа в текущем блоке Qt

**Алгоритм:**
- Получает позицию блока: `block_position = self.currentBlock().position()`
- Получает номер блока: `current_block_number = self.currentBlock().blockNumber() + 1`
- Если `token.line == current_block_number`, возвращает `token.column`
- Иначе возвращает `token.column` (с комментарием о потенциальной ошибке)

**Статус:** Метод определен, но не используется в текущей реализации

### 9.2 Метод `_apply_1c_highlighting_old(text: str)`
**Назначение:** Старая версия подсветки (не используется)

**Алгоритм:**
- Создает новый лексер для каждой строки
- Лексирует строку заново
- Применяет форматирование

**Статус:** Метод оставлен, но не вызывается (заменен на версию с кэшем)

### 9.3 Методы для других языков
- `_apply_python_highlighting(text: str)`: заглушка (`pass`)
- `_apply_csharp_highlighting(text: str)`: заглушка (`pass`)
- `_apply_java_highlighting(text: str)`: заглушка (`pass`)

---

## 10. Интеграция с редактором

### 10.1 Использование в STEditor
**Создание:**
```python
self._highlighter = STHighlighter(
    self._text_edit.document(),
    language=None
)
```

**Установка языка:**
- В методе `set_content()` редактора:
  - Определяется язык через `_identify_language(content)`
  - Вызывается `self._highlighter.set_language(self.language)`
  - Вызывается `self._highlighter.rehighlight()`

**Особенность:** Язык определяется по маркеру `@@` в первой строке файла

---

## 11. Потоки выполнения

### 11.1 Сценарий загрузки файла
1. `STEditor.load(file_path)` → читает файл
2. `STEditor.set_content(content)` → устанавливает содержимое
3. `STEditor._identify_language(content)` → определяет язык
4. `STHighlighter.set_language(language)` → устанавливает язык
5. `STHighlighter._rebuild_tokens_cache()` → пересчитывает кэш (весь документ)
6. `STHighlighter.rehighlight()` → переподсвечивает документ
7. Qt вызывает `highlightBlock()` для каждой строки
8. `_apply_1c_highlighting()` → применяет форматирование из кэша

### 11.2 Сценарий изменения текста
1. Пользователь редактирует текст в QTextEdit
2. Qt автоматически вызывает `highlightBlock()` для измененных блоков
3. `_apply_1c_highlighting()` использует существующий кэш
4. **Проблема:** Кэш не обновляется при изменении текста, если не вызван `rehighlight()`

### 11.3 Сценарий изменения языка
1. `set_language(new_language)` вызывается
2. Вызывается `rehighlight()` (первый раз)
3. Вызывается `_rebuild_tokens_cache()` (пересчет кэша)
4. Вызывается `rehighlight()` (второй раз)
5. Qt вызывает `highlightBlock()` для каждой строки

---

## 12. Структуры данных

### 12.1 `_tokens_by_line`
**Тип:** `dict[int, list]`

**Ожидаемая структура:**
```python
{
    1: [(token1, token_type1), (token2, token_type2), ...],
    2: [(token3, token_type3), ...],
    ...
}
```

**Фактическая структура (из-за бага):**
```python
{
    1: [(token1, token_type1), token1, (token2, token_type2), token2, ...],
    ...
}
```

**Проблема:** Смешанные типы данных в списке из-за дублирования кода в `_rebuild_tokens_cache()`

### 12.2 `_document_text`
**Тип:** `str`
**Назначение:** Хранит текст документа для сравнения при изменении
**Обновление:** В `_rebuild_tokens_cache()` и `rehighlight()`

---

## 13. Особенности работы с ANTLR

### 13.1 Нумерация строк
- ANTLR нумерует строки с 1 (`token.line` начинается с 1)
- Qt нумерует блоки с 0 (`blockNumber()` начинается с 0)
- **Преобразование:** `current_block_number = blockNumber() + 1`

### 13.2 Позиция токена
- `token.column`: позиция от начала строки (начинается с 0)
- Может учитывать табуляцию (зависит от настроек лексера)
- Используется напрямую как `start_pos` в `_apply_token_format()`

### 13.3 Типы токенов
- `lexer.symbolicNames`: список символических имен токенов
- `token.type`: числовой индекс типа
- Если `token_type == '<INVALID>'`, токен считается невалидным

---

## 14. Производительность

### 14.1 Кэширование
**Преимущества:**
- Лексический анализ выполняется один раз для всего документа
- При подсветке отдельных строк используется готовый кэш

**Недостатки:**
- При изменении текста кэш не обновляется автоматически
- Пересчет кэша требует полного лексического анализа документа

### 14.2 Вызовы методов
- `_rebuild_tokens_cache()`: вызывается при изменении документа/языка
- `rehighlight()`: может вызываться дважды при смене языка
- `highlightBlock()`: вызывается Qt для каждой строки при переподсветке

---

## 15. Обработка ошибок

### 15.1 В `_rebuild_tokens_cache()`
- При исключении выводит traceback
- Пробрасывает исключение дальше (не обрабатывает)
- Закомментированная строка очистки кэша при ошибке

### 15.2 В `_apply_1c_highlighting()`
- При ошибке обработки токена выводит сообщение в консоль
- Не прерывает выполнение (продолжает обработку других токенов)

### 15.3 В `_apply_token_format()`
- Нет явной обработки ошибок
- Может упасть при неправильной структуре данных в кэше

---

## 16. Отладочная информация

### 16.1 Print-выводы
- `[STHighlighter] rebuild cache, language={self.language}, doc_len={len(self._document_text)}` - в `_rebuild_tokens_cache()`
- `[STHighlighter] highlight line {current_block_number}, tokens={len(tokens_for_line)}` - в `_apply_1c_highlighting()`
- `Ошибка при обработке токена: {e}` - в `_apply_1c_highlighting()`

---

## Конец анализа функционала

