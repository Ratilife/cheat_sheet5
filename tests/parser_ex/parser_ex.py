import os
import sys

# Добавляем конкретный путь к файлам ANTLR4
antlr_path = r"F:\Языки\Python\Partfolio\cheat_sheet5\cheat_sheet\src\ANTLR4"
sys.path.insert(0, antlr_path)

from antlr4 import FileStream, CommonTokenStream, ParseTreeWalker
from antlr4.error.ErrorListener import ErrorListener
from STFileLexer import STFileLexer
from STFileParser import STFileParser
from STFileListener import STFileListener

class StructureListener(STFileListener):

    def __init__(self):
        """Инициализация слушателя с пустой структурой."""
        self.stack = [{'children': []}]             # Стек для хранения иерархии элементов
        self.current_parent = self.stack[0]         # Текущий родительский элемент
        self.root_name = "Unnamed"                  # Имя корневого элемента (по умолчанию)
        self.found_root = False                     # Флаг обнаружения корневого элемента


    def get_structure(self):

        return self.stack[0]['children']


    def enterEntry(self, ctx):

        if ctx.folderHeader():
            # Обработка папки
            header = ctx.folderHeader()
            name = header.STRING(0).getText()[1:-1]   # Извлечение имени (удаляем кавычки)

            # Создание элемента папки
            new_item = {
                'name': name,
                'type': 'folder',
                'children': []
            }
            # Добавление в текущего родителя и обновление стека
            self.current_parent['children'].append(new_item)
            self.stack.append(new_item)
            self.current_parent = new_item



        elif ctx.templateHeader():
            # Обработка шаблона
            header = ctx.templateHeader()
            name = header.STRING(0).getText()[1:-1]    # Имя шаблона
            # Содержимое шаблона (если есть)
            content = header.STRING(2).getText()[1:-1] if len(header.STRING()) > 1 else ""

            # Добавление шаблона в текущего родителя
            self.current_parent['children'].append({
                'name': name,
                'type': 'template',
                'content': content
            })

    def exitEntry(self, ctx):

        if ctx.folderHeader() and len(self.stack) > 1:
            # Для папки: возвращаемся к предыдущему родителю
            self.stack.pop()
            self.current_parent = self.stack[-1]

# использовать как план А
class MetadataStructureListener(StructureListener):
    def __init__(self):
        super().__init__()

    def enterEntry(self, ctx):
        # Пропускаем обработку template содержимого
        if ctx.folderHeader():
            # Обработка папки (как обычно)
            header = ctx.folderHeader()
            name = header.STRING(0).getText()[1:-1]

            new_item = {
                'name': name,
                'type': 'folder',
                'children': []
            }
            self.current_parent['children'].append(new_item)
            self.stack.append(new_item)
            self.current_parent = new_item

        elif ctx.templateHeader():
            # Обработка шаблона, но без содержимого
            header = ctx.templateHeader()
            name = header.STRING(0).getText()[1:-1]

            # Добавляем template без содержимого
            self.current_parent['children'].append({
                'name': name,
                'type': 'template',
                'content': ""  # Пустое содержимое
            })
class ExceptionErrorListener(ErrorListener):
    """
        Кастомный обработчик ошибок парсинга для ANTLR.
        Преобразует ошибки синтаксиса в исключения Python с подробным описанием.
    """
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        """
                Вызывается при обнаружении синтаксической ошибки.

                Параметры:
                - recognizer: распознаватель, обнаруживший ошибку
                - offendingSymbol: ошибочный символ
                - line: номер строки с ошибкой
                - column: позиция в строке
                - msg: сообщение об ошибке
                - e: исключение (если есть)
        """
        raise Exception(f"Ошибка парсинга в строке {line}:{column} - {msg}")
def parse_st_file( file_path) -> dict:
        """
           Парсит ST-файл и возвращает его иерархическую структуру.

           Данный метод выполняет разбор (парсинг) файла в формате ST (Structured Text) и строит его иерархическую структуру.
           Для этого используется парсер, сгенерированный на основе ANTLR, и специальный слушатель, собирающий структуру данных
           во время обхода дерева разбора.

           Параметры:
               file_path (str): Путь к ST-файлу, который требуется распарсить. Предполагается, что файл закодирован в UTF-8.

           Возвращает:
               dict: Словарь с двумя ключами:
                   - 'structure': иерархическая структура файла (обычно список или вложенные словари/списки),
                   полученная с помощью слушателя StructureListener.
                   - 'root_name': имя корневого элемента, совпадает с именем файла без расширения.

           Особенности:
               - В случае возникновения любой ошибки (например, если файл не найден, некорректен синтаксис или отсутствуют зависимости),
               метод возвращает "пустую" структуру (пустой список) и имя файла без расширения.
               - Для разбора используются классы FileStream, STFileLexer, STFileParser, StructureListener и ParseTreeWalker,
               а также настраивается пользовательский обработчик ошибок ExceptionErrorListener.
               - Имя корня структуры автоматически устанавливается в имя файла без расширения.

           Исключения:
               Все исключения перехватываются и не пробрасываются наружу — в случае ошибки возвращается структура по умолчанию.

           Пример использования:
               result = parser.parse_st_file("example.st")
               print(result['structure'])
               print(result['root_name'])
           """
        try:
            # Создание входного потока с указанием кодировки
            input_stream = FileStream(file_path, encoding="utf-8")
            # Лексический анализ
            lexer = STFileLexer(input_stream)
            tokens = CommonTokenStream(lexer)
            # Синтаксический анализ
            parser = STFileParser(tokens)

            # Устанавливаем обработчик ошибок
            parser.removeErrorListeners()
            parser.addErrorListener(ExceptionErrorListener())
            # Парсинг структуры файла
            tree = parser.fileStructure()
            # Создание и настройка слушателя
            listener = StructureListener()
            file_name = os.path.splitext(os.path.basename(file_path))[0]
            listener.root_name = file_name  # ИЗМЕНЕНИЕ: Имя файла в listener
            # Обход дерева разбора
            ParseTreeWalker().walk(listener, tree)

            return {
                'structure': listener.get_structure(),
                'root_name': listener.root_name
            }
        except Exception as e:
            # Возвращаем базовую структуру при ошибке парсинга
            return {
                'structure': [],
                'root_name': os.path.splitext(os.path.basename(file_path))[0]
            }

# использовать как план В
def parse_st_metadata(file_path) -> dict:
    """
    Парсит ST-файл и возвращает его метаданные, пропуская содержимое template блоков.
    """
    try:
        input_stream = FileStream(file_path, encoding="utf-8")
        lexer = STFileLexer(input_stream)
        tokens = CommonTokenStream(lexer)
        parser = STFileParser(tokens)

        parser.removeErrorListeners()
        parser.addErrorListener(ExceptionErrorListener())
        tree = parser.fileStructure()

        # Используем обычный StructureListener, но с модификацией для пропуска содержимого template
        listener = MetadataStructureListener()  # Используем специальный слушатель
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        listener.root_name = file_name

        ParseTreeWalker().walk(listener, tree)

        return {
            'structure': listener.get_structure(),
            'root_name': listener.root_name
        }
    except Exception as e:
        print(f"Ошибка при парсинге: {e}")  # Добавим отладочную информацию
        return {
            'structure': [],
            'root_name': os.path.splitext(os.path.basename(file_path))[0]
               }

# использовать как план В
def _remove_template_content(structure):
    """
    Рекурсивно удаляет содержимое template блоков из структуры.
    """
    if isinstance(structure, dict):
        if structure.get('type') == 'template':
            # Очищаем содержимое template
            structure['content'] = ""
        # Рекурсивно обрабатываем детей
        if 'children' in structure:
            for child in structure['children']:
                _remove_template_content(child)
    elif isinstance(structure, list):
        for item in structure:
            _remove_template_content(item)

# мертвый код parse_st_metadata3
def parse_st_metadata3(file_path):
    """
        Парсит ST-файл и возвращает его иерархическую структуру (ограничиваясь третьим уровнем вложения).
        """
    try:
        # Создание входного потока с указанием кодировки
        input_stream = FileStream(file_path, encoding="utf-8")
        # Лексический анализ
        lexer = STFileLexer(input_stream)
        tokens = CommonTokenStream(lexer)
        # Синтаксический анализ
        parser = STFileParser(tokens)

        # Устанавливаем обработчик ошибок
        parser.removeErrorListeners()
        parser.addErrorListener(ExceptionErrorListener())
        # Парсинг структуры файла
        tree = parser.fileStructure()
        # Создание и настройка слушателя
        listener = StructureListener()
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        listener.root_name = file_name
        # Обход дерева разбора
        ParseTreeWalker().walk(listener, tree)

        # Получаем полную структуру
        full_structure = listener.get_structure()

        # Ограничиваем третим уровнем вложения
        def limit_depth(structure, current_level=1, max_level=3):
            if current_level > max_level:
                return []

            limited_structure = []
            for item in structure:
                if item['type'] == 'folder':
                    # Для папок ограничиваем глубину детей
                    limited_item = item.copy()
                    limited_item['children'] = limit_depth(item['children'], current_level + 1, max_level)
                    limited_structure.append(limited_item)
                else:
                    # Для шаблонов оставляем как есть
                    limited_structure.append(item)
            return limited_structure

        limited_structure = limit_depth(full_structure)

        return {
            'structure': limited_structure,
            'root_name': listener.root_name
        }
    except Exception as e:
        # Возвращаем базовую структуру при ошибке парсинга
        return {
            'structure': [],
            'root_name': os.path.splitext(os.path.basename(file_path))[0]
        }

# использовать как план А
def parse_st_metadata_level2(file_path) -> dict:
    """
    Парсит ST-файл и возвращает его метаданные, пропуская содержимое template блоков
    и ограничиваясь вторым уровнем вложенности.
    """
    try:
        input_stream = FileStream(file_path, encoding="utf-8")
        lexer = STFileLexer(input_stream)
        tokens = CommonTokenStream(lexer)
        parser = STFileParser(tokens)

        parser.removeErrorListeners()
        parser.addErrorListener(ExceptionErrorListener())
        tree = parser.fileStructure()

        # Используем специальный слушатель для метаданных
        listener = MetadataStructureListener()
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        listener.root_name = file_name

        ParseTreeWalker().walk(listener, tree)

        # Получаем полную структуру и ограничиваем глубину
        full_structure = listener.get_structure()
        limited_structure = _limit_depth_level2(full_structure)

        return {
            'structure': limited_structure,
            'root_name': listener.root_name
        }
    except Exception as e:
        print(f"Ошибка при парсинге: {e}")
        return {
            'structure': [],
            'root_name': os.path.splitext(os.path.basename(file_path))[0]
        }
# использовать как план А
def _limit_depth_level2(structure, current_level=1):
    """
    Рекурсивно ограничивает структуру вторым уровнем вложенности.
    """
    if current_level > 2:
        return []

    limited_structure = []
    for item in structure:
        if item['type'] == 'folder':
            # Для папок ограничиваем глубину детей
            limited_item = item.copy()
            limited_item['children'] = _limit_depth_level2(item['children'], current_level + 1)
            limited_structure.append(limited_item)
        else:
            # Для шаблонов оставляем как есть
            limited_structure.append(item)
    return limited_structure

#------------Отчет---------------
def save_structure_to_txt(data_dict, output_file_path):
    """
    Записывает содержимое словаря с результатами парсинга ST-файла в текстовый файл.
    
    Параметры:
        data_dict (dict): Словарь с ключами 'structure' и 'root_name'
        output_file_path (str): Путь к выходному txt-файлу
    """
    try:
        with open(output_file_path, 'w', encoding='utf-8') as f:
            # Записываем имя корневого элемента
            f.write(f"Root Name: {data_dict['root_name']}\n")
            f.write("=" * 50 + "\n\n")
            
            # Записываем структуру
            f.write("Structure:\n")
            f.write("-" * 20 + "\n")
            
            # Преобразуем структуру в строку и записываем
            # Если structure уже является строкой, записываем как есть
            # Если это список/словарь, преобразуем в читаемый формат
            structure = data_dict['structure']
            if isinstance(structure, (list, dict)):
                import json
                # Используем indent для красивого форматирования
                f.write(json.dumps(structure, indent=2, ensure_ascii=False))
            else:
                f.write(str(structure))
                
        print(f"Данные успешно сохранены в файл: {output_file_path}")
        
    except Exception as e:
        print(f"Ошибка при записи в файл: {e}")
        
    
def start():
    rezultat = parse_st_metadata_level2(r"F:\Языки\Python\Partfolio\cheat_sheet5\root\cheat_sheet\bookmarks\1C\Новый1.st")
        
    path = r"F:\Языки\Python\Partfolio\cheat_sheet5\cheat_sheet\tests\parser_ex\Новый1-огр2 уровнем.txt"
        
    save_structure_to_txt(rezultat,path)
        
    
if __name__ == '__main__':
    start()
