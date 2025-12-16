#!/usr/bin/env python3
# visualize_tree.py - Визуализация дерева разбора ST файлов

import sys
import os
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

# Добавляем путь к корню проекта ПЕРЕД импортами
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from antlr4 import InputStream, CommonTokenStream
from src.ANTLR4.st_grammar.STFileLexer import STFileLexer
from src.ANTLR4.st_grammar.STFileParser import STFileParser


class ANTLRGuiVisualizer:
    def __init__(self, parser_class, lexer_class):
        self.parser_class = parser_class
        self.lexer_class = lexer_class
        
        self.window = tk.Tk()
        self.window.title("ANTLR Parse Tree Visualizer - ST File Parser")
        self.window.geometry("1200x700")
        
        self.setup_ui()
    
    def setup_ui(self):
        # Левая панель - ввод
        left_frame = ttk.Frame(self.window)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Label(left_frame, text="Введите текст для разбора:", 
                 font=('Arial', 11, 'bold')).pack(anchor=tk.W)
        
        self.input_text = scrolledtext.ScrolledText(
            left_frame, 
            height=15,
            width=50,
            font=('Consolas', 10)
        )
        self.input_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Пример данных по умолчанию
        default_text = '''{1, {1, {"Folder", 1, 0, "type", "name"}, {2, {"SubFolder", 1, 1, "type2", "name2"}}}}'''
        self.input_text.insert('1.0', default_text)
        
        # Кнопки
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Показать дерево", 
                  command=self.show_tree).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Токены", 
                  command=self.show_tokens).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Очистить", 
                  command=self.clear_all).pack(side=tk.LEFT, padx=5)
        
        # Правая панель - вывод
        right_frame = ttk.Frame(self.window)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Notebook с вкладками
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Вкладка с деревом
        self.tree_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.tree_frame, text="Дерево разбора")
        
        # Scrollbar для дерева
        tree_scrollbar = ttk.Scrollbar(self.tree_frame)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview для отображения
        self.tree_view = ttk.Treeview(self.tree_frame, yscrollcommand=tree_scrollbar.set)
        self.tree_view.pack(fill=tk.BOTH, expand=True)
        tree_scrollbar.config(command=self.tree_view.yview)
        
        # Вкладка с токенами
        self.token_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.token_frame, text="Токены")
        
        self.token_text = scrolledtext.ScrolledText(
            self.token_frame,
            font=('Consolas', 9)
        )
        self.token_text.pack(fill=tk.BOTH, expand=True)
        
        # Вкладка с LISP-представлением
        self.lisp_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.lisp_frame, text="LISP формат")
        
        self.lisp_text = scrolledtext.ScrolledText(
            self.lisp_frame,
            font=('Consolas', 9)
        )
        self.lisp_text.pack(fill=tk.BOTH, expand=True)
    
    def parse_input(self):
        """Парсинг введенного текста"""
        input_str = self.input_text.get('1.0', tk.END).strip()
        
        if not input_str:
            messagebox.showwarning("Предупреждение", "Введите текст для разбора")
            return None
        
        input_stream = InputStream(input_str)
        lexer = self.lexer_class(input_stream)
        stream = CommonTokenStream(lexer)
        parser = self.parser_class(stream)
        
        # Пытаемся выполнить разбор
        try:
            tree = parser.fileStructure()
            return lexer, parser, tree, stream
        except Exception as e:
            messagebox.showerror("Ошибка парсинга", f"Ошибка при разборе текста:\n{str(e)}")
            return None
    
    def show_tree(self):
        """Отображение дерева в Treeview"""
        result = self.parse_input()
        if not result:
            return
        
        lexer, parser, tree, stream = result
        
        # Очистка предыдущего дерева
        for item in self.tree_view.get_children():
            self.tree_view.delete(item)
        
        # Рекурсивное построение дерева
        def add_tree_items(node, parent=""):
            node_text = type(node).__name__
            
            # Добавляем текст токена если есть
            if hasattr(node, 'start') and node.start:
                token_text = node.start.text
                if len(token_text) > 30:
                    token_text = token_text[:27] + "..."
                node_text += f" : {token_text}"
            
            item_id = self.tree_view.insert(
                parent, 
                'end', 
                text=node_text,
                open=True  # Автоматически раскрываем
            )
            
            # Обрабатываем детей
            if hasattr(node, 'children') and node.children:
                for child in node.children:
                    add_tree_items(child, item_id)
        
        try:
            add_tree_items(tree)
            
            # Показываем LISP-представление
            self.lisp_text.delete('1.0', tk.END)
            self.lisp_text.insert('1.0', tree.toStringTree(recog=parser))
            
            # Переключаемся на вкладку с деревом
            self.notebook.select(0)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при построении дерева:\n{str(e)}")
    
    def show_tokens(self):
        """Отображение списка токенов"""
        result = self.parse_input()
        if not result:
            return
        
        lexer, parser, tree, stream = result
        
        # Заполняем токены
        stream.fill()
        tokens = stream.tokens
        
        self.token_text.delete('1.0', tk.END)
        
        for i, token in enumerate(tokens):
            if token.type != -1:  # Игнорируем EOF для отображения
                # Безопасно получаем имя токена
                token_name = f"<{token.type}>"
                if token.type < len(lexer.symbolicNames) and lexer.symbolicNames[token.type] is not None:
                    token_name = lexer.symbolicNames[token.type]
                elif token.type < len(lexer.literalNames) and lexer.literalNames[token.type] is not None:
                    token_name = lexer.literalNames[token.type]
                
                line_info = f"Строка {token.line}:{token.column}"
                self.token_text.insert(tk.END, 
                    f"[@{i}] {token_name:15} = '{token.text:20}' ({line_info})\n")
        
        # Переключаемся на вкладку с токенами
        self.notebook.select(1)
    
    def clear_all(self):
        """Очистка всех полей"""
        self.input_text.delete('1.0', tk.END)
        self.token_text.delete('1.0', tk.END)
        self.lisp_text.delete('1.0', tk.END)
        for item in self.tree_view.get_children():
            self.tree_view.delete(item)
    
    def run(self):
        """Запуск приложения"""
        self.window.mainloop()


# Использование
if __name__ == "__main__":
    app = ANTLRGuiVisualizer(STFileParser, STFileLexer)
    app.run()

